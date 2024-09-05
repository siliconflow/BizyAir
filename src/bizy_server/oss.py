import asyncio
import logging
import os

import oss2
from oss2.models import PartInfo
from tqdm import tqdm

logging.basicConfig(level=logging.DEBUG)


class AliOssStorageClient:
    def __init__(
        self,
        endpoint,
        bucket_name,
        access_key,
        secret_key,
        security_token,
        onUploading,
    ):
        auth = (
            oss2.StsAuth(access_key, secret_key, security_token)
            if security_token
            else oss2.Auth(access_key, secret_key)
        )
        self.bucket = oss2.Bucket(auth, endpoint, bucket_name)
        self.bucket_name = bucket_name
        self.region = endpoint
        self.onUploading = onUploading
        logging.debug(
            f"New OSS storage client initialized: {self.bucket_name} in {self.region}"
        )

    async def upload_file(self, file_path, object_name):
        total_size = os.path.getsize(file_path)
        progress_bar = tqdm(
            total=total_size,
            unit="B",
            unit_scale=True,
            desc=f"Uploading {os.path.basename(file_path)}",
        )

        # 维护累计发送的字节数
        bytes_uploaded = 0

        def progress_callback(bytes_sent, total_bytes):
            nonlocal bytes_uploaded
            progress_increment = bytes_sent - bytes_uploaded
            progress_bar.update(progress_increment)
            bytes_uploaded = bytes_sent  # 更新累计已发送的字节数
            if self.onUploading:
                self.onUploading(bytes_sent, total_bytes)

        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None,
                self.bucket.put_object_from_file,
                object_name,
                file_path,
                progress_callback,
            )
        except oss2.exceptions.OssError as e:
            logging.error(f"Failed to upload file: {e}")
            raise e
        finally:
            progress_bar.close()

        return f"{self.bucket_name}/{self.region}/{object_name}"

    async def multipart_upload(self, file_path, object_name):
        total_size = os.path.getsize(file_path)
        part_size = oss2.determine_part_size(total_size, preferred_size=1024 * 1024)
        upload_id = self.bucket.init_multipart_upload(object_name).upload_id

        parts = []
        loop = asyncio.get_running_loop()
        with open(file_path, "rb") as f:
            for part_number in range(1, (total_size + part_size - 1) // part_size + 1):
                offset = (part_number - 1) * part_size
                size = min(part_size, total_size - offset)
                result = await loop.run_in_executor(
                    None,
                    self.bucket.upload_part,
                    object_name,
                    upload_id,
                    part_number,
                    f.read(size),
                )
                parts.append(PartInfo(part_number, result.etag))
                logging.debug(f"Uploaded part {part_number} for {object_name}")

        try:
            await loop.run_in_executor(
                None,
                self.bucket.complete_multipart_upload,
                object_name,
                upload_id,
                parts,
            )
        except oss2.exceptions.OssError as e:
            logging.error(f"Failed to complete multipart upload: {e}")
            raise e

        return f"{self.bucket_name}/{self.region}/{object_name}"
