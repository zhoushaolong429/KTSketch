import time
from functools import total_ordering
from collections import defaultdict

import mmh3
import numpy as np

from basicDataStruct.bitmap import Bitmap

from tool.myTool import readTXTData
from tool.performance import PerformanceClas
from tool.realExp import realSpread4OneEpoch

from basicDataStruct.doubleLinkList import *


class FreeBS_SSD_doubleLinkList:
    def __init__(self, n, sizeOfSummary, th1):
        self.seedOfFreeBS = 2340
        self.n = n
        self.bitmap = Bitmap(n)
        self.th1 = th1
        self.sizeOfSummary = sizeOfSummary
        self.summaryLinkList = DoubleLinkList(sizeOfSummary)
        self.estDict = dict()
        self.estSet = set()

    def showMem(self):
        memeryOfFreeBS = (self.n / 1024 / 8)
        memeryOfSummary = (18 * self.sizeOfSummary) / 1024  # flowlabel(2B) counter(4B) * 2 address(4B) * 2
        print("freeBS_SSD共有{}个cell".format(self.sizeOfSummary))
        print("freeBS_SSD.bitmap :", memeryOfFreeBS, "KB")
        print("freeBS_SSD.Summary :", memeryOfSummary, "KB")

    def insertOneElem(self, srcStr, dstStr):
        elemStr = srcStr + dstStr
        pos = mmh3.hash(elemStr, self.seedOfFreeBS) % self.bitmap.size()
        if self.bitmap.isPosZero(pos):
            q_B = self.bitmap.emptyRatio()
            tempCell = CellOfTopKSummary(srcStr, 1 / q_B, 0)
            tempNode = self.summaryLinkList.is_contain(tempCell)
            if tempNode is not None:
                tempNode.item.est += tempCell.est
                self.summaryLinkList.sort4Node(tempNode)
            else:
                if self.summaryLinkList.size > self.summaryLinkList.lenth:
                    self.summaryLinkList.add(Node(tempCell))
                    self.summaryLinkList.sort4Node(self.summaryLinkList._head.next)
                else:
                    p_t = (1 / q_B) / (self.summaryLinkList._head.next.item.est + 1 / q_B)
                    r = np.random.random()
                    if r <= p_t:
                        self.summaryLinkList._head.next.item.flowLabel = tempCell.flowLabel
                        self.summaryLinkList._head.next.item.error = self.summaryLinkList._head.next.item.est
                        self.summaryLinkList._head.next.item.est += 1 / q_B
                        self.summaryLinkList.sort4Node(self.summaryLinkList._head.next)
                    else:
                        self.summaryLinkList._head.next.item.est += 1 / q_B
                        self.summaryLinkList.sort4Node(self.summaryLinkList._head.next)
            self.bitmap.setONE(pos)

    def update4OneEpoch(self, src_list, dst_list):
        for i in range(len(src_list)):
            if i % (100 * 10000) == 0:
                print("freeBS-SSD已处理行数：", i)
            self.insertOneElem(src_list[i], dst_list[i])

    def getEstDict(self):
        for node in self.summaryLinkList:
            tempEst = abs(node.est - node.error)
            if tempEst > self.th1:
                self.estDict[node.flowLabel] = tempEst
        return self.estDict

    def getEstSet(self):
        for node in self.summaryLinkList:
            tempEst = abs(node.est - node.error)
            if tempEst > self.th1:
                self.estSet.add(node.flowLabel)
        return self.estSet


if __name__ == '__main__':
    startTime = time.time()

    txtFileName = "D:\\a_networkTrace\\CAIDA2019_600wPerTXT\\0.txt"
    src_list, dst_list = readTXTData(txtFileName)

    realDict = realSpread4OneEpoch(src_list, dst_list, 200)

    freeBS_SSD_h2b = FreeBS_SSD_doubleLinkList(30 * 1024 * 8, int(30 * 1024 / 18 ), 200)
    freeBS_SSD_h2b.showMem()
    freeBS_SSD_h2b.update4OneEpoch(src_list, dst_list)
    estDict = freeBS_SSD_h2b.getEstDict()

    print(len(realDict), len(estDict))
    myP = PerformanceClas(realDict, estDict, 100)
    aae, are = myP.performance()
    print("aae:", aae)
    print("are", are)

    set_est = set(estDict.keys())
    set_real = set(realDict.keys())
    print("真实值 spread大于阈值的流数目", len(set_real))
    print("估计值 spread大于阈值的流数目", len(set_est))
    intersection_set = set_real & set_est
    union_set = set_real | set_est
    print("对于spread大于阈值的流估计：")
    print("预测正确个数：", len(intersection_set))
    print("准确率:", len(intersection_set) / len(union_set))
    print("FPR:", (len(set_est) - len(intersection_set)) / len(set_real))
    print("FNR:", (len(set_real) - len(intersection_set)) / len(set_real))

    endTime = time.time()
    print("总运行时长为", endTime - startTime)
