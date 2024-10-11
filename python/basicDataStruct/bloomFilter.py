import mmh3
import numpy as np

from basicDataStruct.bitmap import Bitmap


class BloomFilter:
    def __init__(self, n, k, seeds):
        self.n = n
        self.k = k
        self.seeds = seeds
        self.bitmap = Bitmap(n)

    def isInBF(self, elem):
        for i in range(self.k):
            pos = mmh3.hash(str(elem), self.seeds[i], False) % self.n
            if self.bitmap.isPosZero(pos):
                return False
        return True

    def insertOneElem(self, elem):
        for i in range(self.k):
            pos = mmh3.hash(str(elem), self.seeds[i], False) % self.n
            self.bitmap.setONE(pos)

    def falsePositive(self):
        v = self.bitmap.numOfONE() / self.bitmap.size()
        p = pow(v, self.k)
        return p

    def showMem(self):
        print("布隆过滤器大小为", self.n / 1024 / 8, "KB")


if __name__ == '__main__':
    seeds = []
    for i in range(5):
        temprand = np.random.randint(11, 99999)
        seeds.append(temprand)
    bf = BloomFilter(1024 * 8, 2, seeds)
    for i in range(200):
        bf.insertOneElem(i)

    print(bf.falsePositive())
