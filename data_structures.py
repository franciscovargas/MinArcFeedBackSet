

class Node:
    """
    Asistant node class for inverted index
    """

    def __init__(self, data):
        self.data = None
        self.next = None


class InvertedLinkedList:
    """
    This class implments the augmentation of a linked list with an inverted index
    in order to remove/move elements between the buckets of the GR-FAS algorithm
    in O(1)

    Note this is at the expense that the inverted index just marks removed as None
    without deleting therm and resizing
    """

    def __init__(self, iterator = [], capacity = 100000):

        self.capacity = capacity
        self.inverted_index = dict.fromkeys(range(capacity))
        self._length = 0
        self.linked_list = Node(None)
        self.head = self.linked_list

    def _append_node(self, data):
        if not self.linked_list.data:
            self.linked_list.data = data
        else:
            self.linked_list.next = Node(data)
            self.linked_list = self.linked_list.next

    def append(self, data):

        self.inverted_index[data] =  self.linked_list # parent node of node to be created (old_tail)
        self._append_node(data) # create and insert new node at the tail of the list (new_tail)

    def remove(self, data):
        """
        Remove an item with value data in O(1)
        """
        parent_node = self.inverted_index[data] # get parent of the node to be removed
        self.inverted_index[data] = None
        removed_node = parent_node.next
        if removed_node:
            parent_node.next = removed_node.next
        return removed_node.data # will crash when searching for a node that has already been removed (or never inserted)

    def pop(self, dummy):
        """O(1)
        Pops head of queue (deque not pop tbh ... )
        """
        tmp = self.head
        self.head = self.head.next
        return tmp

    def __getitem__(self, i):
        """
        Indexes into the ith item of the queue. Does so in O(N) (could be done in O(1) augmenting the inverted index)
        but only ever used to peek (i=0) which is O(1)
        """

        tmp = self.head
        for j in xrange(i):
            if not tmp: raise IndexError()
            tmp = tmp.next

        if not tmp: raise IndexError()

        return tmp.data

