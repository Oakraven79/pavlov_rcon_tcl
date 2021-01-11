import asyncio
import hashlib
import json
import logging

logging.getLogger("async-pavlov").addHandler(logging.NullHandler())


class InvalidPassword(Exception):
    pass


class PavlovRCON:
    def __init__(self, ip, port, password, timeout=5):
        self.ip = ip
        self.port = port
        self.password = hashlib.md5(password.encode()).hexdigest()
        self.timeout = timeout
        self.reader, self.writer = None, None
        self._recv_lock = asyncio.Lock()
        self._drain_lock = asyncio.Lock()

    async def open(self):
        if not self.is_connected():
            await self._connect()

    async def close(self):
        if self.is_connected():
            await self._disconnect()

    def is_connected(self):
        if self.writer and not self.writer.is_closing():
            return True
        return False

    async def send(self, command, wait_response=True, auto_close=False):
        if not self.is_connected():
            await self._connect()
        await self._send(command)
        data = None
        if wait_response:
            data = await self._recv()
        if auto_close:
            await self._disconnect()
        return data

    async def _flush_reader(self):
        async with self._recv_lock:
            try:
                await asyncio.wait_for(self.reader.read(512), 0.1)
            except asyncio.exceptions.TimeoutError:
                pass

    async def _send(self, data):
        logging.info(f"{self.port} - RCON _send {data=}")
        await self._flush_reader()
        self.writer.write(data.encode())
        async with self._drain_lock:
            await asyncio.wait_for(self.writer.drain(), self.timeout)

    async def _auth(self):
        await self._send(self.password)
        data = await self._recv()
        if "Authenticated=1" not in data:
            raise InvalidPassword

    async def _connect(self):
        self.reader, self.writer = await asyncio.wait_for(
            asyncio.open_connection(self.ip, self.port), self.timeout
        )
        data = await self._recv()
        if "Password" in data:
            await self._auth()

    async def _disconnect(self):
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

    async def _recv(self):
        async with self._recv_lock:
            data = await asyncio.wait_for(self.reader.read(2048), self.timeout)
        data = data.decode()
        logging.info(f"{self.port} - RCON _recv {data=}")
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            pass
        return data
