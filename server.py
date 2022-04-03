from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread

from tasks import QueueTask
from connector import Connector


class ServerConnector(Thread, Connector):
    def __init__(self, connect: socket, task_queue: QueueTask, id: int):
        Thread.__init__(self)
        Connector.__init__(self, connect)
        self.__task_queue = task_queue
        self.__id = id

    def run(self):
        print(f'Client {self.__id} running')
        """
        1. Передать данные и тип задачи на сервер, отобразить идентификатор.
        2. Запросить и вывести статус задачи по идентификатору.
        3. Запросить и вывести результат выполнения задачи по идентификатору.
        4. Пакетное выполнение задачи:
        """
        while True:
            try:
                code_operation: int = self._rcv_integer()
            except RuntimeError:
                break

            if code_operation == 0:
                break

            if code_operation == 1:
                try:
                    type_task: int = self._rcv_integer()
                    arg: str = self._rcv_msg()
                except RuntimeError:
                    break
                id_task: int = self.__task_queue.add_task(type_task, arg)
                self._send_integer(id_task)

            if code_operation == 2:
                try:
                    id_task: int = self._rcv_integer()
                except RuntimeError:
                    break
                try:
                    status: str = self.__task_queue.get_status_task(id_task)
                    self._send_msg(status)
                except ValueError:
                    self._send_msg(f"Task with id {id_task} not found.")

            if code_operation == 3:
                try:
                    id_task: int = self._rcv_integer()
                except RuntimeError:
                    break
                try:
                    value: str = self.__task_queue.get_value_task(id_task)
                    self._send_msg(value)
                except ValueError:
                    self._send_msg(f"Task with id {id_task} not value.")

        self._connection.close()
        print(f'Client {self.__id} closed')


if __name__ == '__main__':
    queue = QueueTask()
    queue.start()
    sock = socket(AF_INET, SOCK_STREAM)
    server_address = ('localhost', 5555)
    sock.bind(server_address)

    sock.listen()
    print(f'Server listen on {server_address}')
    while True:
        try:
            # ждем соединения
            connection, client_address = sock.accept()
            print(f'Connect client from {client_address}')
            client = ServerConnector(connection, queue, client_address[1])
            client.start()
        except KeyboardInterrupt:
            break

    queue.stop()
    sock.close()
    print('Closed server')
