from socket import socket
from struct import pack, unpack


class Connector:
    def __init__(self, connect: socket):
        self._connection: socket = connect

    def __send_bytes(self, raw_msg: bytes, size: int):
        count_send_bytes = self._connection.send(raw_msg)
        while count_send_bytes < size:
            count_send_bytes += self._connection.send(raw_msg[count_send_bytes:])

    def __rcv_bytes(self, count: int) -> bytes:
        data: bytes = bytes()
        count_rcv_bytes = 0

        while count_rcv_bytes < count:
            part = self._connection.recv(count - count_rcv_bytes)
            if not part:
                raise RuntimeError
            data += part
            count_rcv_bytes = len(data)

        return data

    def _send_msg(self, msg: str):
        raw_msg: bytes = msg.encode('utf-8')
        size: int = len(raw_msg)
        self._send_integer(size)
        self.__send_bytes(raw_msg, size)

    def _rcv_msg(self) -> str:
        size = self._rcv_integer()
        raw_msg: bytes = self.__rcv_bytes(size)
        return raw_msg.decode('utf-8')

    def _send_integer(self, value: int):
        raw_msg = pack("@i", value)
        self.__send_bytes(raw_msg, 4)

    def _rcv_integer(self) -> int:
        raw_msg: bytes = self.__rcv_bytes(4)
        value = unpack("@i", raw_msg)[0]
        return value
