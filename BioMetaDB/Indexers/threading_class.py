import threading


class ThreadClass(threading.Thread):
    def __init__(self, queue, data, has_header, header, na_rep, _id):
        threading.Thread.__init__(self)
        self.queue = queue
        self.data = data
        self.has_header = has_header
        self.header = header
        self.na_rep = na_rep
        self._id = _id

    def run(self):
        while True:
            line, line_len = self.queue.get()
            for i in range(1, line_len):
                if line[i] == self.na_rep:
                    line[i] = None
                if self.has_header:
                    self.data[line[0]].setattr(self.header[i], line[i])
                else:
                    self.data[line[0]].setattr(self.header + str(i), line[i])
            self.queue.task_done()

    def get(self):
        return self.data
