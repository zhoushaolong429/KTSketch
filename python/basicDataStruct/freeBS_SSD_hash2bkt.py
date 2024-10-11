import time
from functools import total_ordering
from collections import defaultdict

import mmh3
import numpy as np

from basicDataStruct.bitmap import Bitmap

from tool.myTool import readTXTData
from tool.performance import PerformanceClas
from tool.realExp import realSpread4OneEpoch


@total_ordering
class CellOfBkt:
    def __init__(self, flowLabel, est, error):
        self.flowLabel = flowLabel
        self.est = est
        self.error = error

    def __gt__(self, other):
        return self.est > other.est


class Bkt:
    def __init__(self, sizeOfBkt):
        self.sizeOfBkt = sizeOfBkt
        self.cellArray = []

    def sortBkt(self):
        self.cellArray.sort()

    def posOfFlowInBkt(self, flowLabel):
        for idx, cells in enumerate(self.cellArray):
            if (cells.flowLabel == flowLabel):
                return idx
        return -1

    def isBktFull(self):
        return len(self.cellArray) == self.sizeOfBkt


class FreeBS_SSD_hash2bkt:
    def __init__(self, n, numOfBkt, sizeOfBkt, th1):
        self.seedOfFreeBS = 2340
        self.n = n
        self.bitmap = Bitmap(n)
        # self.summary = []
        # self.sizeOfSummary = sizeOfSummary
        self.numOfBkt = numOfBkt
        self.sizeOfBkt = sizeOfBkt
        self.th1 = th1
        self.bktArray = []
        for i in range(numOfBkt):
            tempBkt = Bkt(sizeOfBkt)
            self.bktArray.append(tempBkt)
        self.seed4ChoosingBkt = np.random.randint(1, 9999)
        self.estDict = dict()
        self.estSet = set()

    def showMem(self):
        memeryOfFreeBS = (self.n / 1024 / 8)
        memeryOfSummary = (10 * self.numOfBkt * self.sizeOfBkt) / 1024  # flowlabel(2B) counter(4B) * 2
        print("freeBS_SSD.bitmap :", memeryOfFreeBS, "KB")
        print("freeBS_SSD.Summary :", memeryOfSummary, "KB")

    def insertOneElem(self, srcStr, dstStr):
        elemStr = srcStr + dstStr
        pos = mmh3.hash(elemStr, self.seedOfFreeBS) % self.bitmap.size()
        if self.bitmap.isPosZero(pos):
            q_B = self.bitmap.emptyRatio()
            idxOfBkt = mmh3.hash(srcStr, self.seed4ChoosingBkt, signed=False) % self.numOfBkt
            tempPos = self.bktArray[idxOfBkt].posOfFlowInBkt(srcStr)
            if tempPos > -1:
                self.bktArray[idxOfBkt].cellArray[tempPos].est += 1 / q_B
                # self.summary.sort()  # 用升序存储，cellArray[0]即summary[0]是最“小”的cell
                self.bktArray[idxOfBkt].sortBkt()
            else:
                if len(self.bktArray[idxOfBkt].cellArray) == self.sizeOfBkt:
                    p_t = (1 / q_B) / (self.bktArray[idxOfBkt].cellArray[0].est + 1 / q_B)
                    r = np.random.random()
                    if r <= p_t:
                        tempCell = CellOfBkt(srcStr, self.bktArray[idxOfBkt].cellArray[0].est + 1 / q_B,
                                             self.bktArray[idxOfBkt].cellArray[0].est)
                        self.bktArray[idxOfBkt].cellArray[0] = tempCell
                        # self.summary.sort()
                        self.bktArray[idxOfBkt].sortBkt()
                    else:
                        self.bktArray[idxOfBkt].cellArray[0].est += 1 / q_B
                        # self.summary.sort()
                        self.bktArray[idxOfBkt].sortBkt()
                else:
                    tempCell = CellOfBkt(srcStr, 1 / q_B, 0)
                    self.bktArray[idxOfBkt].cellArray.append(tempCell)
                    # self.summary.sort()
                    self.bktArray[idxOfBkt].sortBkt()
            self.bitmap.setONE(pos)

    def update4OneEpoch(self, src_list, dst_list):
        for i in range(len(src_list)):
            if i % (100 * 10000) == 0:
                print("freeBS-SSD已处理行数：", i)
            self.insertOneElem(src_list[i], dst_list[i])

    def getEstDict(self):
        for bkt in self.bktArray:
            for cell in bkt.cellArray:
                tempEst = abs(cell.est - cell.error)
                if tempEst > self.th1:
                    self.estDict[cell.flowLabel] = tempEst
        return self.estDict

    def getEstSet(self):
        for bkt in self.bktArray:
            for cell in bkt.cellArray:
                tempEst = abs(cell.est - cell.error)
                if tempEst > self.th1:
                    self.estSet.add(cell.flowLabel)
        return self.estSet


if __name__ == '__main__':
    startTime = time.time()

    txtFileName = "D:\\a_networkTrace\\CAIDA2019_600wPerTXT\\0.txt"
    src_list, dst_list = readTXTData(txtFileName)

    th = 50

    mem = 40


    realDict = realSpread4OneEpoch(src_list, dst_list, th)

    for i in range(5) :
        print("------------------------------------------------------------")
        print("------------------------------------------------------------")
        startTime = time.time()
        if i == 0 :
            n4Bkt = 4
            freeBS_SSD_h2b = FreeBS_SSD_hash2bkt(int(0.3 * mem * 1024 * 8), int(0.7 * mem * 1024 / 10 / n4Bkt), n4Bkt, th)
        if i == 1 :
            n4Bkt = 8
            freeBS_SSD_h2b = FreeBS_SSD_hash2bkt(int(0.3 * mem * 1024 * 8), int(0.7 * mem * 1024 / 10 / n4Bkt), n4Bkt, th)
        if i == 2:
            n4Bkt = 16
            freeBS_SSD_h2b = FreeBS_SSD_hash2bkt(int(0.3 * mem * 1024 * 8), int(0.7 * mem * 1024 / 10 / n4Bkt), n4Bkt, th)
        if i == 3:
            n4Bkt = 32
            freeBS_SSD_h2b = FreeBS_SSD_hash2bkt(int(0.3 * mem * 1024 * 8), int(0.7 * mem * 1024 / 10 / n4Bkt), n4Bkt, th)
        if i == 4:
            n4Bkt = 64
            freeBS_SSD_h2b = FreeBS_SSD_hash2bkt(int(0.3 * mem * 1024 * 8), int(0.7 * mem * 1024 / 10 / n4Bkt), n4Bkt, th)
        if i == 5:
            freeBS_SSD_h2b = FreeBS_SSD_hash2bkt(int(0.3 * mem * 1024 * 8), int(0.7 * mem * 1024 / 10 / n4Bkt), n4Bkt, th)


        freeBS_SSD_h2b.showMem()
        freeBS_SSD_h2b.update4OneEpoch(src_list, dst_list)
        endTime = time.time()
        estDict = freeBS_SSD_h2b.getEstDict()

        print(len(realDict), len(estDict))
        myP = PerformanceClas(realDict, estDict, 100)
        aae, are = myP.performance()
        # print("aae:", aae)
        print("are", are)

        set_est = set(estDict.keys())
        set_real = set(realDict.keys())
        # print("真实值 spread大于阈值的流数目", len(set_real))
        # print("估计值 spread大于阈值的流数目", len(set_est))
        intersection_set = set_real & set_est
        union_set = set_real | set_est
        # print("对于spread大于阈值的流估计：")
        # print("预测正确个数：", len(intersection_set))
        # print("准确率:", len(intersection_set) / len(union_set))
        # print("FPR:", (len(set_est) - len(intersection_set)) / len(set_real))
        # print("FNR:", (len(set_real) - len(intersection_set)) / len(set_real))

        endTime = time.time()
        print("总运行时长为", endTime - startTime)

        print("-------------------")
        TP = len(intersection_set)
        FP = len(set_est) - len(intersection_set)
        FN = len(set_real) - len(intersection_set)
        PR = TP / (TP + FP)
        RR = TP / (TP + FN)
        F1SCORE = 2 * PR * RR / (PR + RR)
        print("PR:", PR)
        print("RR:", RR)
        print("F1SCORE:", F1SCORE)
