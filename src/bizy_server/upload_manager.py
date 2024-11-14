import asyncio
import base64
import hashlib
import os
import threading
import time

import aiofiles
import crcmod
import oss2

from .errno import errnos
from .error_handler import ErrorHandler
from .oss import AliOssStorageClient
from .utils import is_string_valid


class UploadManager:
    def __init__(self, server):
        self.error_handler = ErrorHandler()
        self.upload_progresses_updated_at = dict()
        self.server = server
        self.oss_clients = {}

    async def calculate_hash(self, file_path):
        do_crc64 = crcmod.mkCrcFun(
            0x142F0E1EBA9EA3693, initCrc=0, xorOut=0xFFFFFFFFFFFFFFFF, rev=True
        )
        crc64_signature = 0
        buf_size = 65536 * 16

        async with aiofiles.open(file_path, "rb") as f:
            while chunk := await f.read(buf_size):
                crc64_signature = do_crc64(chunk, crc64_signature)

        md5_hash = hashlib.md5()
        async with aiofiles.open(file_path, "rb") as file:
            while chunk := await file.read(buf_size):
                md5_hash.update(chunk)
        md5_str = base64.b64encode(md5_hash.digest()).decode("utf-8")

        hasher = hashlib.sha256()
        hasher.update(f"{md5_str}{crc64_signature}".encode("utf-8"))
        hash_string = hasher.hexdigest()

        return hash_string

    async def interrupt_uploading(self, upload_id):
        if upload_id in self.oss_clients:
            self.oss_clients[upload_id].interruptUploading()

    async def do_upload(self, item):
        sid = item["sid"]
        upload_id = item["upload_id"]
        self.server.send_sync(
            event="status",
            data={
                "status": "starting",
                "upload_id": upload_id,
                "message": "start uploading",
            },
            sid=sid,
        )

        root_dir = item["root"]
        model_files = []
        for file in item["files"]:
            filename = file["path"]
            filepath = os.path.abspath(os.path.join(root_dir, filename))
            if not os.path.exists(filepath):
                self.server.send_sync_error(err=errnos.FILE_NOT_EXISTS, sid=sid)
                return

            sha256sum = await self.calculate_hash(filepath)

            sign_data, err = await self.server.api_client.sign(sha256sum)
            if err is not None:
                self.server.send_sync_error(err=err, sid=sid)
                return

            file_record = sign_data.get("file")

            if not is_string_valid(file_record.get("id")):
                print(f"\033[94m[BizyAir]\033[0m Start uploading file: {filename}")
                file_storage = sign_data.get("storage")
                try:
                    self.upload_progresses_updated_at[upload_id] = 0

                    def updateProgress(consume_bytes, total_bytes):
                        current_time = time.time()
                        if (
                            current_time - self.upload_progresses_updated_at[upload_id]
                            >= 1
                        ):
                            self.upload_progresses_updated_at[upload_id] = current_time

                            progress = (
                                f"{consume_bytes / total_bytes * 100:.0f}%"
                                if consume_bytes / total_bytes * 100
                                == int(consume_bytes / total_bytes * 100)
                                else "{:.2f}%".format(consume_bytes / total_bytes * 100)
                            )
                            self.server.send_sync(
                                event="progress",
                                data={
                                    "upload_id": upload_id,
                                    "path": filename,
                                    "progress": progress,
                                },
                                sid=sid,
                            )

                    def sendInterruptMsg():
                        self.server.send_sync(
                            event="interrupted",
                            data={
                                "upload_id": upload_id,
                                "path": filename,
                            },
                            sid=sid,
                        )
                        return

                    oss_client = AliOssStorageClient(
                        endpoint=file_storage.get("endpoint"),
                        bucket_name=file_storage.get("bucket"),
                        access_key=file_record.get("access_key_id"),
                        secret_key=file_record.get("access_key_secret"),
                        security_token=file_record.get("security_token"),
                        onUploading=updateProgress,
                        onInterrupted=sendInterruptMsg,
                    )
                    self.oss_clients[upload_id] = oss_client
                    await oss_client.upload_file(
                        filepath, file_record.get("object_key")
                    )
                except oss2.exceptions.OssError as e:
                    print(f"\033[31m[BizyAir]\033[0m OSS err:{str(e)}")
                    self.server.send_sync_error(errnos.UPLOAD, sid)
                    return
                finally:
                    self.oss_clients.pop(upload_id, None)

                commit_data, err = await self.server.api_client.commit_file(
                    signature=sha256sum, object_key=file_record.get("object_key")
                )
                if err is not None:
                    self.server.send_sync_error(err)
                    return

                print(f"\033[32m[BizyAir]\033[0m {filename} Already Uploaded")
            self.server.send_sync(
                event="progress",
                data={"upload_id": upload_id, "path": filename, "progress": "100%"},
                sid=sid,
            )

            model_files.append({"sign": sha256sum, "path": filename})

        print("\033[32m[BizyAir]\033[0m Uploaded successfully")

        self.server.send_sync(
            event="status",
            data={
                "status": "finish",
                "upload_id": upload_id,
                "model_files": model_files,
                "message": "uploading finished",
            },
            sid=sid,
        )
