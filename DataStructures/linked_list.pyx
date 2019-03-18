# cython: language_level=3


class Node:
    __slots__ = ['value', 'next_node']

    def __init__(self, value):
        self.value = value
        self.next_node = None


class LinkedList:
    __slots__ = ['length', 'node', 'initial']

    def __init__(self, *args):
        """ Initializer

        :param args:
        """
        self.length = 0
        self.node = None
        self.initial = None
        if args:
            if len(args) == 1:
                for data in args[0]:
                    self.append(data)
            else:
                for data in args:
                    self.append(data)

    def append(self, value):
        """ Add to end of LinkedList

        :param value:
        :return:
        """
        cdef object new_node = Node(value)
        if not self.initial:
            self.initial = new_node
        else:
            self.node.next_node = new_node
        self.node = new_node
        self.length += 1

    def insert(self, int index, value):
        """ Insert at given index

        :param index:
        :param value:
        :return:
        """
        assert index < self.length, "Index must be less that length"
        cdef object new_node = Node(value)
        self.node = self.initial
        cdef int i = 0
        if index == 0:
            self.node = new_node
            self.node.next_node = self.initial
            self.initial = self.node
            self.length += 1
            self._move_to_end(0)
            return
        elif index < 0:
            index = index + self.length
        while i < index - 1:
            self.__next__()
            i += 1
        cdef object old_next_node = self.node.next_node
        self.node.next_node = new_node
        self.__next__()
        self.node.next_node = old_next_node
        self.length += 1
        self._move_to_end(i)

    def to_list(self):
        """ Creates and returns python list of values

        :return:
        """
        cdef int i = 0
        cdef list to_return = []
        self.node = self.initial
        while i < self.length:
            to_return.append(self.node.value)
            self.__next__()
            i += 1
        return to_return

    def pop(self):
        """ Remove and return last value in LinkedList

        :return:
        """
        cdef int i = 0
        self.node = self.initial
        while i < self.length - 2:
            self.__next__()
            i += 1
        cdef object to_return = self.node.next_node.value
        self.node.next_node = None
        self.length -= 1
        return to_return

    def __len__(self):
        """ Return length property

        :return:
        """
        return self.length

    def __next__(self):
        """ Sets node as next node's value, if available

        :return:
        """
        if self.node.next_node:
            self.node = self.node.next_node
            return self

    def __iter__(self):
        """ Creates iterator that yields values of nodes

        :return:
        """
        self.node = self.initial
        while self.node:
            yield self.node.value
            self.node = self.node.next_node
        self.node = self.initial
        self._move_to_end(0)

    def __iadd__(self, other):
        """ Overload method for combining 2 LinkedLists

        :param other: LinkedList
        :return:
        """
        cdef int old_length
        if isinstance(other, list) or isinstance(other, tuple) or isinstance(other, set):
            for value in other:
                self.append(value)
            return self
        elif isinstance(other, LinkedList):
            self.node.next_node = other.initial
            self.length += other.length
            self.node = self.initial
            self._move_to_end(0)
            return self
        else:
            raise TypeError, "Invalid type passed"

    def __isub__(self, other):
        """ Overload method for removing an iterable of values from LinkedList

        :param other:
        :return:
        """
        for value in other:
            self.remove(value)
        return self

    def __contains__(self, value):
        """ Determines if value in list
        Returns bool based on search

        :param value:
        :return:
        """
        self.node = self.initial
        cdef int i = 0
        while i < self.length:
            if self.node.value == value:
                self._move_to_end(i)
                return True
            self.__next__()
            i += 1
        self._move_to_end(i)
        return False

    def remove(self, value):
        """ Removes first occurrence of value
        Looks for value and calls __delitem__ if found

        :param value:
        :return:
        """
        self.node = self.initial
        cdef int i = 0
        while i < self.length:
            if self.node.value == value:
                break
            self.__next__()
            i += 1
        if i == self.length and self.node.value != value:
            raise ValueError, "Value not found"
        self.__delitem__(i)

    def __getitem__(self, item):
        """ Returns value at location or slice
        Passing a slice creates list and returns given slice of list

        :param item:
        :return:
        """
        cdef object to_return = None
        self.node = self.initial
        cdef int i = 0
        if isinstance(item, slice):
            return self.to_list()[item.start : item.stop : item.step]
        elif isinstance(item, int):
            assert item < self.length, "Index must be less that length"
            if item == 0:
                return self.initial.value
            elif item < 0:
                item = item + self.length
            while i < item:
                self.node = self.node.next_node
                i += 1
            to_return = self.node.value
            self._move_to_end(i)
            return to_return
        raise TypeError, "Item must be int or slice"

    def __setitem__(self, int index, value):
        """ Sets value at index

        :param index:
        :param value:
        :return:
        """
        assert index < self.length, "Index must be less that length"
        self.node = self.initial
        cdef int i = 0
        if index == 0:
            self.node.value = value
            self._move_to_end(i)
            return
        if index < 0:
            index = index + self.length
        while i < index:
            self.__next__()
            i += 1
        self.node.value = value
        self._move_to_end(i)

    def __delitem__(self, int index):
        """ Deletes value at index

        :param index:
        :return:
        """
        assert index < self.length, "Index must be less that length"
        cdef int i = 0
        if index == 0:
            self.initial = self.initial.next_node
            self.node = self.initial
            self.length -= 1
            self._move_to_end(0)
            return
        elif index == self.length - 1:
            self.pop()
        elif index < 0:
            index = index + self.length
        self.node = self.initial
        while i < index - 1:
            self.__next__()
            i += 1
        self.node.next_node = self.node.next_node.next_node
        self.length -= 1
        self._move_to_end(i)

    def __repr__(self):
        """ Creates list and returns string representation

        :return:
        """
        return self.to_list().__repr__()

    def _move_to_end(self, int i):
        """ Protected member for moving pointer to end of list, starting at index i

        :param i:
        :return:
        """
        while i < self.length:
            self.__next__()
            i += 1
