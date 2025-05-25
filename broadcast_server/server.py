import asyncio
from asyncio import StreamReader, StreamWriter, Timeout

from utils.logger import get_logger

logger = get_logger(__name__)

END_OF_MESSAGE = b"\r\n"


class Connection:
    def __init__(self, reader: StreamReader, writer: StreamWriter) -> None:
        self.reader = reader
        self.writer = writer
        self.user = "anonymous"

    def __str__(self) -> str:
        peername = self.writer.get_extra_info("peername")
        return f"{self.user}@{peername}"


class BroadcastServer:
    def __init__(self, host: str, port: int, timeout_delta: int = 300) -> None:
        self.host = host
        self.port = port
        self.connections: list[Connection] = []
        self.timeout_delta = timeout_delta

    async def run(self) -> None:
        server = await asyncio.start_server(self._handle_client, self.host, self.port)
        async with server:
            await server.serve_forever()

    async def _handle_client(self, reader: StreamReader, writer: StreamWriter) -> None:
        self._log_info(writer)
        connection = Connection(reader, writer)
        verified = await self._verify_connection(connection)
        if not verified:
            await self._close(connection)
            return
        try:
            async with asyncio.timeout(self.timeout_delta) as timeout:
                await self._handle_messages(connection, timeout)
        except TimeoutError:
            logger.info(f"{connection} timed out. Closing connection")
            await self._close(connection)

    def _log_info(self, writer: StreamWriter) -> None:
        client_address = writer.get_extra_info("peername")
        logger.info(f"Connection request received from {client_address}")

    async def _verify_connection(self, connection: Connection) -> bool:
        logger.debug(f"Verification of client connection started")
        message = await self._read_message(connection)
        if not message:
            return False
        logger.debug(f"Check CONNECT string")
        if message.startswith("CONNECT"):
            logger.debug(f"Message starts with CONNECT")
            message_chunks = message.split(" ")
            if len(message_chunks) == 1:
                logger.debug("Client connection user set to anonymous")
            else:
                user = message_chunks[1]
                connection.user = user
                logger.debug(f"Client connection user set to {user}")
            logger.debug("Client connection verified")
            self.connections.append(connection)
            logger.info(f"Connection {connection} verified and added to connections.")
            logger.debug(f"Number of connections: {len(self.connections)}")
            logger.debug(f"Connections {self.connections}")
            await self._write(connection, "SUCCESS")
            return True
        else:
            logger.info(f"Connection {connection} can not be verified")
            return False

    async def _handle_messages(self, connection: Connection, timeout: Timeout) -> None:
        while True:
            message = await self._read_message(connection)
            if not message:
                break

            if message.startswith("\\"):
                closes_connection = await self._handle_command(message, connection)
                if closes_connection:
                    break
                continue

            timeout.reschedule(asyncio.get_running_loop().time() + self.timeout_delta)
            await self._broadcast(connection, message)

    async def _broadcast(self, this_connection: Connection, message: str) -> None:
        logger.debug(f"Broadcasting message to clients {self.connections}")
        for connection in self.connections:
            logger.debug(f"Check same connection: {connection is not this_connection}")
            if connection is not this_connection:
                logger.debug(f"Broadcasting message to client {connection}")
                await self._write(connection, message)

    async def _handle_command(self, message: str, connection: Connection) -> bool:
        command = message[2:].lower()
        logger.debug(f"Received command: {command}")
        match command:
            case "exit":
                await self._close(connection)
                logger.debug("'exit' command called")
                return True
            case "clients":
                response = str([str(connection) for connection in self.connections])
                await self._write(connection, response)
                logger.debug("'clients' command called")
                return False
            case "ping":
                return False
            case _:
                await self._write(connection, f"UNKNOWN COMMAND: {command}")
                logger.debug(f"Unknown command: {command}")
                return False

    async def _read_message(self, connection: Connection) -> str | None:
        logger.debug(f"Waiting for message")
        try:
            message = (
                (await connection.reader.readuntil(END_OF_MESSAGE)).decode().strip()
            )
        except Exception as e:
            logger.debug(f"Unexpected read error from {connection}: {e}")
            await self._close(connection)
            return
        logger.debug(f"Message received: {message}")
        return message

    def _remove_connection(self, connection: Connection):
        if connection in self.connections:
            logger.debug(f"{connection} removed from connections")
            self.connections.remove(connection)

    async def _write_and_close(self, connection: Connection, message: str):
        await self._write(connection, message)
        await self._close(connection)

    async def _write(self, connection: Connection, message: str):
        logger.debug(f"Sending message: {message} to {connection}")
        try:
            connection.writer.write(message.encode() + END_OF_MESSAGE)
            await connection.writer.drain()
            logger.debug("Message sent")
        except Exception as e:
            logger.warning(f"Failed to send message to {connection}: {e}")

    async def _close(self, connection: Connection):
        logger.debug(f"Closing connection {connection}")
        try:
            connection.writer.close()
            await connection.writer.wait_closed()
            logger.debug("Connection closed")
        except Exception as e:
            logger.warning(f"Failed to close connection: {e}")
        finally:
            self._remove_connection(connection)
