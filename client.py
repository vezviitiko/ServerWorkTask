from argparse import ArgumentParser
from socket import AF_INET, SOCK_STREAM, socket
from time import sleep

from connector import Connector


class ClientConnector(Connector):
    def __init__(self, connect: socket):
        Connector.__init__(self, connect)

    def _call_task(self, code: int, arg: str) -> int:
        self._send_integer(1)
        self._send_integer(code)
        self._send_msg(arg)
        id_task: int = self._rcv_integer()
        return id_task

    def _get_status_task(self, id_task: int) -> str:
        self._send_integer(2)
        self._send_integer(id_task)
        status: str = self._rcv_msg()
        return status

    def _get_value_task(self, id_task: int) -> str:
        self._send_integer(3)
        self._send_integer(id_task)
        value: str = self._rcv_msg()
        return value


class CallClientConnector(ClientConnector):
    def __init__(self, connect: socket, code: int, arg: str, packet: bool = False):
        ClientConnector.__init__(self, connect)
        self.__code = code
        self.__arg = arg
        self.__packet = packet

    def run(self):
        id_task: int = self._call_task(self.__code, self.__arg)
        if id_task == -1:
            print(f'Task with type {self.__code} not found')
            return

        print(f'Id of task - {id_task}')
        if not self.__packet:
            self._send_integer(0)
            return

        while True:
            try:
                sleep(0.5)
                status: str = self._get_status_task(id_task)
                if status == 'done':
                    break
            except KeyboardInterrupt:
                return

        value: str = self._get_value_task(id_task)
        print(f'Value {value} of packet task')
        self._send_integer(0)


class GetClientConnector(ClientConnector):
    def __init__(self, connect: socket, id_task: int, is_status: bool = False):
        print('Create GetClientConnector')
        ClientConnector.__init__(self, connect)
        self.__id_task = id_task
        self.__is_status = is_status

    def run(self):
        if self.__is_status:
            status: str = self._get_status_task(self.__id_task)
            print(f'Status task {self.__id_task}: {status}')
        else:
            value: str = self._get_value_task(self.__id_task)
            print(f'Value task {self.__id_task}: {value}')
        self._send_integer(0)


if __name__ == '__main__':
    parser = ArgumentParser(description='Works with server.')
    parser.add_argument('--port', type=int, dest='port', default=5555, help='port of server')
    subparsers = parser.add_subparsers(title='subcommands',
                                       dest='command',
                                       description='valid subcommands',
                                       help='description')

    call_parser = subparsers.add_parser('call', help='call task')
    call_parser.add_argument('-c', '--code', dest='code', type=int, help='type of task')
    call_parser.add_argument('-a', '--arg', dest='arg', type=str, help='argument for task')
    call_parser.add_argument('-p', '--packet', dest='packet', action='store_true', help='it is packet task?')

    get_parser = subparsers.add_parser('get', help='get info from queue task')
    get_parser.add_argument('-i', '--id', dest='id', type=int, help='id of task')
    get_parser.add_argument('-s', '--status', dest='status', action='store_true', help='get status for task')
    get_parser.add_argument('-v', '--value', dest='value', action='store_true', help='get value for task')

    args = parser.parse_args()
    print(args)
    sock = socket(AF_INET, SOCK_STREAM)
    # Подключаем сокет к порту, через который прослушивается сервер
    server_address = ('localhost', args.port)
    sock.connect(server_address)

    if args.command == 'call':
        client = CallClientConnector(sock, args.code, args.arg, args.packet)
        client.run()

    if args.command == 'get':
        client = GetClientConnector(sock, args.id, args.status)
        client.run()
