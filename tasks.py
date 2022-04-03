from time import sleep
from threading import Lock, Thread


def reverse(word: str) -> str:
    """
    Выполнить разворот строки. (пример -> ремирп). Задержка 2 сек.
    """
    reverse_word = word[-1:: -1]
    sleep(2)
    return reverse_word


def permutation(word: str) -> str:
    """
    Выполнить попарно перестановку четных и нечетных символов в строке
    ( пример -> рпмире, кот -> окт). Задержка 5 сек.
    """
    mutate_word = ''
    for i in range(len(word) // 2):
        mutate_word += word[2 * i + 1] + word[2 * i]
    if len(word) % 2:
        mutate_word += word[-1]
    sleep(5)
    return mutate_word


def repeat(word: str) -> str:
    """
    Выполнить повтор символа в строке согласно его позиции
    (пример -> прриииммммееееерррррр). Задержка 7 сек.
    """
    repeat_word = ''
    for i in range(len(word)):
        repeat_word += word[i] * (i + 1)
    sleep(7)
    return repeat_word


all_tasks = {
    1: reverse,
    2: permutation,
    3: repeat,
}


class QueueTask(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.__queue = list()
        self.__current_task = 0
        self.__index = 0
        self.__mutex = Lock()
        self.__shutdown: bool = False

    def add_task(self, code: int, arg: str) -> int:
        """
        Метод добавляет задание в очередь на выполнение.
        Принимается код задачи и аргумент к ней.
        Возвращается номер задачи в списке
        """
        task = {
                'task': all_tasks.get(code, None),
                'arg': arg,
                'status': 'sleep',
                'value': '',
            }
        if task['task'] is None:
            return -1
        self.__mutex.acquire()

        self.__queue.append(task)
        index = self.__index
        self.__index += 1
        self.__mutex.release()
        return index

    def get_status_task(self, index: int) -> str:
        """
        Метод проверки статуса задачи.
        На вход принимается индекс задачи, возвращается статус задачи:
        sleep - если задача еще не взята на выполнение
        work  - если задача в данный момент выполняется
        done  - если задача уже выполнена
        """
        self.__mutex.acquire()
        try:
            task = self.__queue[index]
        except:
            self.__mutex.release()
            raise ValueError
        self.__mutex.release()
        return task['status']

    def get_value_task(self, index: int) -> str:
        """
        Метод проверки результат работы задачи.
        Принимает индекс задачи, возвращает результат работы, если задача была выполнена.
        Если задание еще не выполнен, то кидается исключение
        """
        self.__mutex.acquire()
        try:
            task = self.__queue[index]
        except:
            self.__mutex.release()
            raise ValueError
        if task['value'] == '':
            self.__mutex.release()
            raise ValueError
        self.__mutex.release()
        return task['value']

    def run(self):
        """
        Метод запуска обработки очереди заданий.
        Будет ждать пока не появится задание, запустит его, результат тоже добавит в очередь.
        """
        while not self.__shutdown:
            self.__mutex.acquire()
            if self.__current_task == self.__index:
                # Нет заданий к выполнению
                self.__mutex.release()
                sleep(0.05)
            else:
                task = self.__queue[self.__current_task]
                self.__queue[self.__current_task]['status'] = 'work'
                self.__mutex.release()
                value = task['task'](task['arg'])
                self.__mutex.acquire()
                self.__queue[self.__current_task]['status'] = 'done'
                self.__queue[self.__current_task]['value'] = value
                self.__current_task += 1
                self.__mutex.release()

    def stop(self):
        self.__shutdown = True
