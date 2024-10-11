import numpy as np


class Bitmap():
    def __init__(self, n):
        self.bitmap = np.zeros(shape=n)
        self.len = n
        self.numOfZERO = n

    def setONE(self, pos):
        if (self.bitmap[pos] == 0):
            self.bitmap[pos] = 1
            self.numOfZERO -= 1

    def isPosOne(self, pos):
        return self.bitmap[pos] == 1

    def isPosZero(self, pos):
        return self.bitmap[pos] == 0

    def size(self):
        return self.len

    def numOfZERO(self):
        return self.numOfZERO

    def numOfONE(self):
        return self.len - self.numOfZERO

    def emptyRatio(self):
        return self.numOfZERO / self.len

    def setAllZero(self):
        pass
