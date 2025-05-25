import asyncio
import sys
from asyncio import StreamReader, StreamWriter, Timeout

from utils.logger import get_logger

logger = get_logger(__name__)

END_OF_MESSAGE = b"\r\n"


class BroadcastClient:
    def __init__(self, host: str, port: int, user: str, heartbeat: int = 5) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.heartbeat = heartbeat
        self.reader: StreamReader
        self.writer: StreamWriter

    async def run(self):
        logger.debug(f"Connecting to server")
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

        verified_connection = await self._send_verification_request()
        if not verified_connection:
            await self._close()

        server_writer = asyncio.create_task(self._write_to_server())
        server_reader = asyncio.create_task(self._read_from_server())
        heartbeat = asyncio.create_task(self._heartbeat())

        done, pending = await asyncio.wait(
            [server_writer, server_reader, heartbeat],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()
        await asyncio.gather(*pending, return_exceptions=True)

    async def _send_verification_request(self) -> bool:
        await self._write("CONNECT " + self.user)
        message = await self._read_message()
        if message != "SUCCESS":
            print("Can not initialize connection.")
            return False
        print("Connection initialized.")
        return True

    async def _write_to_server(self) -> None:
        while True:
            message = (await self._ainput()).strip()
            await self._write(message)
            if message == "\\exit":
                break

    async def _read_from_server(self) -> None:
        while True:
            message = await self._read_message()
            if not message:
                break
            print(f">> {message}")

    async def _heartbeat(self):
        while True:
            await asyncio.sleep(self.heartbeat)
            await self._write("\\\\ping")

    async def _read_message(self) -> str | None:
        logger.debug(f"Waiting for message")
        try:
            message = (await self.reader.readuntil(END_OF_MESSAGE)).decode().strip()
        except Exception as e:
            logger.debug(f"Unexpected read error from broadcast server: {e}")
            await self._close()
            return
        logger.debug(f"Message received: {message}")
        return message

    async def _write_and_close(self, message: str):
        await self._write(message)
        await self._close()

    async def _write(self, message: str):
        logger.debug(f"Sending message: {message} to the broadcast server")
        try:
            self.writer.write(message.encode() + END_OF_MESSAGE)
            await self.writer.drain()
            logger.debug("Message sent")
        except Exception as e:
            logger.warning(f"Failed to send message to the broadcast server: {e}")

    async def _close(self):
        logger.debug(f"Closing connection")
        try:
            self.writer.close()
            await self.writer.wait_closed()
            logger.debug("Connection closed")
        except Exception as e:
            logger.warning(f"Failed to close connection: {e}")

    async def _ainput(self) -> str:
        # NOTE:
        # This method uses run_in_executor to perform blocking input from stdin.
        # It cannot be cancelled directly and will block until input is received.
        print(f"", end="", flush=True)
        return await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
