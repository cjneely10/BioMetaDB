import threading
from queue import Queue
from BioMetaDB.Accessories.update_data import UpdateData


class ThreadClass(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.data = UpdateData()

    def run(self):
        while True:
            host = self.queue.get()

            self.queue.task_done()
