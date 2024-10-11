class CellOfTopKSummary:
    def __init__(self, flowLabel, est, error):
        self.flowLabel = flowLabel
        self.est = est
        self.error = error

    def __str__(self):
        return "flowLable = {a}  est = {b}  error = {c}".format(a=self.flowLabel, b=self.est, c=self.error)


class Node(object):
    def __init__(self, item: CellOfTopKSummary):
        self.item = item
        self.next = None
        self.prev = None


class DoubleLinkList(object):
    """双向链表"""

    def __init__(self, size):
        self.lenth = 0
        self.size = size
        self._head = Node(None)


    def is_empty(self):
        """判断链表是否为空"""
        return self._head.next is None

    def travel(self):
        """遍历链表"""
        cur = self._head.next
        while cur.next is not None:
            print(cur.next.item)
            cur = cur.next
        print("")

    def add(self, node: Node):
        self.lenth += 1
        """头部插入元素"""
        if self.is_empty():
            self._head.next = node
            node.prev = self._head
        else:
            node.next = self._head.next
            node.prev = self._head
            self._head.next = node
            node.next.prev = node

    def is_contain(self, item: CellOfTopKSummary):
        """查找流标签是否存在，若存在，则返回其标识"""
        cur = self._head.next
        while cur is not None:
            if cur.item.flowLabel == item.flowLabel:
                return cur
            cur = cur.next
        return None

    def sort4Node(self, cur: Node):
        p = cur
        while (p.next is not None and cur.item.est > p.next.item.est):
            p = p.next
        if p != cur:
            if p.next is not None:
                cur.prev.next = cur.next
                cur.next.prev = cur.prev
                cur.next = p.next
                cur.prev = p
                p.next = cur
                cur.next.prev = cur
            else:
                cur.prev.next = cur.next
                cur.next.prev = cur.prev
                cur.next = p.next
                cur.prev = p
                p.next = cur

    def clear(self):
        """清空链表"""
        self._head = None

    def __iter__(self):
        """可以使用循环遍历链表"""
        cur = self._head.next
        while cur is not None:
            value = cur.item
            cur = cur.next
            yield value


# 测试数据

if __name__ == "__main__":
    c1 = CellOfTopKSummary("c1", 3, 5)
    c2 = CellOfTopKSummary("c2", 8, 5)
    c3 = CellOfTopKSummary("c3", 6, 5)
    c4 = CellOfTopKSummary("c4", 10, 5)
    c5 = CellOfTopKSummary("c5", 1, 5)
    c6 = CellOfTopKSummary("c6", 9, 5)
    c7 = CellOfTopKSummary("c7", 45, 5)

    print("------创建链表------")
    dl_list = DoubleLinkList(10)
    dl_list.add(Node(c1))
    dl_list.sort4Node(dl_list._head.next)

    dl_list.add(Node(c2))
    dl_list.sort4Node(dl_list._head.next)
    dl_list.travel()


    dl_list.add(Node(c3))
    dl_list.sort4Node(dl_list._head.next)
    dl_list.travel()

    dl_list.add(Node(c4))
    dl_list.sort4Node(dl_list._head.next)
    dl_list.travel()

    dl_list.add(Node(c5))
    dl_list.sort4Node(dl_list._head.next)
    dl_list.add(Node(c6))
    dl_list.sort4Node(dl_list._head.next)
    dl_list.add(Node(c7))
    dl_list.sort4Node(dl_list._head.next)

    dl_list.travel()

    # print(dl_list.is_contain(c2))
    # dl_list.sort4Node(dl_list.is_contain(c2))
    # dl_list.insert(2, 4)
    # dl_list.insert(4, 5)
    # dl_list.insert(0, 6)
    # print("length:", len(dl_list))
    # dl_list.travel()
    # print(dl_list.is_contain(3))
    # print(dl_list.is_contain(8))
    # print(3 in dl_list)
    # print(8 in dl_list)
    # dl_list.remove(1)
    # print("length:", len(dl_list))

    print("------循环遍历------")
    for i in dl_list:
        print(i)
