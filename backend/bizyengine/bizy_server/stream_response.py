import asyncio
import json
import ssl
from typing import Any, Dict, List, Optional


class ConnectionState:
    """连接状态枚举"""

    INIT = "初始化"
    CONNECTING = "连接中"
    CONNECTED = "已连接"
    READING = "读取中"
    CLOSING = "关闭中"
    CLOSED = "已关闭"
    ERROR = "错误"


class StreamResponse:
    """自定义流式响应类，支持状态管理和错误处理"""

    def __init__(self, request_data: Dict[str, Any], timeout: int = 60):
        # 请求和连接数据
        self.request_data = request_data
        self.reader = None
        self.writer = None
        self.timeout = timeout

        # 连接状态管理
        self.state = ConnectionState.INIT
        self.state_lock = asyncio.Lock()  # 状态修改锁
        self.connection_event = asyncio.Event()
        self.error = None

        # 数据相关
        self.content = self
        self.buffer = b""
        self.chunks_received = 0
        self.done_received = False

        # 调试信息
        self.debug_id = id(self)  # 用于日志区分不同实例

    async def _set_state(self, new_state: str, error: Exception = None) -> None:
        """线程安全地设置连接状态"""
        async with self.state_lock:
            self.state = new_state
            if error:
                self.error = error

            # 如果状态为已连接，触发连接事件
            if new_state == ConnectionState.CONNECTED:
                self.connection_event.set()

            # 如果状态为错误，也触发连接事件，让等待连接的代码继续执行并处理错误
            if new_state == ConnectionState.ERROR:
                self.connection_event.set()

    async def connect_and_request(self, api_key: str):
        """建立连接并发送请求，包含严格的状态管理"""
        # 设置状态为连接中
        await self._set_state(ConnectionState.CONNECTING)

        try:
            # 建立SSL连接，添加超时控制
            connect_coro = asyncio.open_connection("api.siliconflow.cn", 443, ssl=True)
            self.reader, self.writer = await asyncio.wait_for(
                connect_coro, timeout=self.timeout
            )

            # 准备HTTP请求
            json_data = json.dumps(self.request_data)
            request = (
                f"POST /v1/chat/completions HTTP/1.1\r\n"
                f"Host: api.siliconflow.cn\r\n"
                f"Authorization: Bearer {api_key}\r\n"
                f"Accept: text/event-stream\r\n"
                f"Content-Type: application/json\r\n"
                f"Content-Length: {len(json_data)}\r\n"
                f"Connection: keep-alive\r\n"
                f"\r\n"
                f"{json_data}"
            )

            # 检查是否仍在连接状态
            async with self.state_lock:
                if self.state != ConnectionState.CONNECTING:
                    raise Exception(f"连接状态已变更为 {self.state}，无法发送请求")

            # 发送请求
            self.writer.write(request.encode("utf-8"))
            await asyncio.wait_for(self.writer.drain(), timeout=self.timeout)

            # 读取HTTP响应头
            response_line = await asyncio.wait_for(
                self.reader.readline(), timeout=self.timeout
            )
            if not response_line:
                raise Exception("服务器关闭了连接")

            status_line = response_line.decode("utf-8").strip()

            if not status_line.startswith("HTTP/1.1 200"):
                raise Exception(f"API请求失败: {status_line}")

            # 读取响应头
            headers = {}
            while True:
                # 再次检查状态
                async with self.state_lock:
                    if self.state != ConnectionState.CONNECTING:
                        raise Exception(
                            f"连接状态已变更为 {self.state}，停止读取响应头"
                        )

                line = await asyncio.wait_for(
                    self.reader.readline(), timeout=self.timeout
                )
                if line == b"\r\n" or not line:
                    break

                try:
                    header_line = line.decode("utf-8").strip()
                    if ":" in header_line:
                        key, value = header_line.split(":", 1)
                        headers[key.strip()] = value.strip()
                except Exception:
                    pass

            # 成功连接
            await self._set_state(ConnectionState.CONNECTED)

        except asyncio.TimeoutError as e:
            await self._set_state(ConnectionState.ERROR, e)
            await self.release()
            raise Exception(f"连接超时 (>{self.timeout}秒)") from e

        except Exception as e:
            await self._set_state(ConnectionState.ERROR, e)
            await self.release()
            raise Exception(f"连接失败: {str(e)}") from e

    async def iter_any(self):
        """模拟aiohttp的iter_any方法"""
        # 等待连接完成
        if not self.connection_event.is_set():
            try:
                await asyncio.wait_for(
                    self.connection_event.wait(), timeout=self.timeout
                )
            except asyncio.TimeoutError as e:
                await self._set_state(ConnectionState.ERROR, e)
                await self.release()
                raise Exception(f"等待连接超时 (>{self.timeout}秒)") from e

        # 检查连接状态
        async with self.state_lock:
            if self.state == ConnectionState.ERROR:
                error_msg = f"连接发生错误: {str(self.error)}"
                raise Exception(error_msg) from self.error

            if self.state != ConnectionState.CONNECTED:
                error_msg = f"连接状态为 {self.state}，无法读取数据"
                raise Exception(error_msg)

            # 设置状态为读取中
            self.state = ConnectionState.READING

        # 读取数据
        try:
            max_empty_chunks = 3  # 连续空块计数，防止无限循环
            empty_chunk_count = 0

            while True:
                # 检查状态
                async with self.state_lock:
                    if self.state != ConnectionState.READING:
                        break

                try:
                    # 读取一段数据，添加超时控制
                    chunk = await asyncio.wait_for(
                        self.reader.read(1024), timeout=self.timeout
                    )

                    # 检测连续空块，防止无限循环
                    if not chunk:
                        empty_chunk_count += 1
                        if empty_chunk_count >= max_empty_chunks:
                            break
                        # 给个短暂的休息，避免CPU过度使用
                        await asyncio.sleep(0.05)
                        continue
                    else:
                        empty_chunk_count = 0

                    # 更新计数并生成数据
                    self.chunks_received += 1
                    yield chunk

                    # 检查是否接收到了结束标记 [DONE]
                    if b"data: [DONE]" in chunk:
                        self.done_received = True
                        break

                except asyncio.TimeoutError as e:
                    await self._set_state(ConnectionState.ERROR, e)
                    break

                except (ConnectionError, OSError) as e:
                    await self._set_state(ConnectionState.ERROR, e)
                    break

        except Exception as e:
            await self._set_state(ConnectionState.ERROR, e)
            error_msg = f"读取数据失败: {str(e)}"
            raise
        finally:
            # 关闭连接
            await self.release()

    async def release(self):
        """安全关闭连接并释放资源"""
        async with self.state_lock:
            # 检查是否已经在关闭或已关闭状态
            if self.state in [ConnectionState.CLOSING, ConnectionState.CLOSED]:
                return

            # 设置状态为关闭中
            self.state = ConnectionState.CLOSING

        # 关闭写入端
        if self.writer:
            writer = self.writer
            self.writer = None  # 清除引用
            self.reader = None  # 清除引用

            try:
                # 尝试优雅关闭
                if not writer.is_closing():
                    # 先确保发送所有数据
                    try:
                        await asyncio.wait_for(writer.drain(), timeout=1.0)
                    except (asyncio.TimeoutError, ConnectionError, OSError):
                        # 忽略drain错误
                        pass

                    # 写入EOF标记
                    try:
                        writer.write_eof()
                    except (OSError, RuntimeError):
                        # 忽略无法写入EOF的错误
                        pass

                    # 关闭连接
                    writer.close()

                # 等待连接关闭完成
                try:
                    await asyncio.wait_for(writer.wait_closed(), timeout=2.0)
                except (asyncio.TimeoutError, ConnectionError, OSError, RuntimeError):
                    # 忽略等待关闭的错误
                    pass
            except Exception:
                pass

        # 设置为已关闭状态
        await self._set_state(ConnectionState.CLOSED)
