import time
from collections import defaultdict
from functools import total_ordering

import mmh3
import numpy as np

from basicDataStruct.bloomFilter import BloomFilter
from basicDataStruct.countMin import Count_Min
from basicDataStruct.doubleLinkList import *
from tool.realExp import RealExpGenerateAndReadTXT
from tool.myTool import *


@total_ordering
class Cell1:
    def __init__(self, flowLabel, est):
        self.flowLabel = flowLabel
        self.est = est

    def __gt__(self, other):
        return self.est > other.est


class Cell2:
    def __init__(self, flowLabel, counter1):
        self.flowLabel = flowLabel
        self.counter1 = counter1


class Sol1_BFCM:
    def __init__(self, dirFileName, th1, p, numOfEpoch, sizeOfEpoch, sizeOfBF, sizeOfCM, sizeOfS1, sizeOfS2):
        self.dirFileName = dirFileName
        self.th1 = th1
        self.p = p
        self.numOfEpoch = numOfEpoch
        self.th2 = p * numOfEpoch
        self.sizeOfEpoch = sizeOfEpoch
        self.sizeOfBF = sizeOfBF
        self.sizeOfCM = sizeOfCM
        self.sizeOfS1 = sizeOfS1
        self.sizeOfS2 = sizeOfS2

        self.seeds = [2350, 2351, 2352, 2353, 2354]
        self.bf_size = self.sizeOfBF * 8 * 1024
        self.bf = BloomFilter(self.bf_size, 2, self.seeds)
        self.cm_numOfFloor = 3
        self.cm_sizeOfFloor = int(self.sizeOfCM * 1024 / 4 / self.cm_numOfFloor)
        self.cm = Count_Min(self.cm_numOfFloor, self.cm_sizeOfFloor)

        self.sizeOfSummary = sizeOfS1 * 1024 / 10
        self.summaryLinkList = DoubleLinkList(self.sizeOfSummary)

        self.summary2 = []
        self.summary2Size = int(self.sizeOfS2 * 1024 / 6)

    def showMem(self):
        print("Sol1_BFCM信息如下：")
        print("测量周期数为{a}，阈值th1为{b}，阈值p为{c}，每个测量周期{d}w个数据包".format(a=self.numOfEpoch, b=self.th1, c=self.p,
                                                                  d=self.sizeOfEpoch))
        self.bf.showMem()
        self.cm.showMem()
        print("topkSummary的大小为：", self.sizeOfSummary * 10 / 1024, "KB")
        print("topkSummary有{}个cell".format(self.sizeOfSummary))
        print("summary2的大小为：", self.summary2Size * 6 / 1024, "KB")
        print("summary2有{}个cell".format(self.summary2Size))

    def insertOneElem(self, srcStr, dstStr):
        elemStr = srcStr + dstStr
        if not self.bf.isInBF(elemStr):
            self.bf.insertOneElem(elemStr)
            self.cm.Insert(srcStr)
            tempEst = self.cm.Query(srcStr)
            tempCell1 = CellOfTopKSummary(srcStr, tempEst, 0)
            self.insertIntoTopkSummary(tempCell1)

    def opAfterOneEpoch(self):
        num = 0
        for node in self.summaryLinkList:
            tempEst = abs(node.est - node.error)
            if tempEst > self.th1:
                num += 1
                tempCell2 = Cell2(node.flowLabel, 1)
                self.addIntoSummary2(tempCell2)
        print("在这个测量周期，添加到summary2的flow数量为：", num)
        self.bf = BloomFilter(self.bf_size, 2, self.seeds)
        self.cm = Count_Min(self.cm_numOfFloor, self.cm_sizeOfFloor)
        self.summaryLinkList = DoubleLinkList(self.sizeOfSummary)

    def insertIntoTopkSummary(self, tempCell):
        tempNode = self.summaryLinkList.is_contain(tempCell)
        if tempNode is not None:
            tempNode.item.est += tempCell.est
            self.summaryLinkList.sort4Node(tempNode)
        else:
            if self.summaryLinkList.size > self.summaryLinkList.lenth:
                self.summaryLinkList.add(Node(tempCell))
                self.summaryLinkList.sort4Node(self.summaryLinkList._head.next)
            else:
                if tempCell.est > self.summaryLinkList._head.next.item.est:
                    self.summaryLinkList._head.next.item.flowLabel = tempCell.flowLabel
                    self.summaryLinkList._head.next.item.est = tempCell.est
                    self.summaryLinkList.sort4Node(self.summaryLinkList._head.next)

    def addIntoSummary2(self, tempCell2):
        for cell in self.summary2:
            if cell.flowLabel == tempCell2.flowLabel:
                cell.counter1 += 1
                return
        if len(self.summary2) < self.summary2Size:
            self.summary2.append(tempCell2)

    def work(self):
        for i in range(numOfEpoch):
            print("周期", i, " 开始处理...")
            txtFileName = self.dirFileName + str(i) + ".txt"
            src_list, dst_list = readTXTData(txtFileName)
            for i in range(len(src_list)):
                if i % (200 * 10000) == 0:
                    print("已处理行数：", i)
                self.insertOneElem(src_list[i], dst_list[i])
            self.opAfterOneEpoch()
        print("...处理完毕...")

    def getEstResult(self):
        est_dict = dict()
        for cell in self.summary2:
            if cell.counter1 > self.th2:
                est_dict[cell.flowLabel] = cell.counter1
        return est_dict


if __name__ == '__main__':
    for i in range(4):
        print("----------------------------------------------------")
        print("----------------------------------------------------")

        sizeOfEpoch = 1200
        numOfEpoch = 8
        th1 = 10
        p = 0.9
        th2 = p * numOfEpoch

        dirFileName = "D:\\a_networktrace\\univ2_trace_1200wPerTXT\\"
        targetDirName = "..\\realExpData\\univ2_trace\\"

        if i == 0:
            sizeOfBF = 30
            sizeOfCM = 10
            sizeOfS1 = 5
            sizeOfS2 = 5

        if i == 1:
            sizeOfBF = 65
            sizeOfCM = 25
            sizeOfS1 = 5
            sizeOfS2 = 5

        if i == 2:
            sizeOfBF = 100
            sizeOfCM = 40
            sizeOfS1 = 5
            sizeOfS2 = 5

        if i == 3:
            sizeOfBF = 130
            sizeOfCM = 60
            sizeOfS1 = 5
            sizeOfS2 = 5

        sol1 = Sol1_BFCM(dirFileName, th1, p, numOfEpoch, sizeOfEpoch, sizeOfBF, sizeOfCM, sizeOfS1, sizeOfS2)
        sol1.showMem()

        time_s = time.time()
        sol1.work()
        time_e = time.time()
        time_cost = time_e - time_s
        print("总运行时间为", time_cost)
        print("吞吐量为{a}Mops".format(a=sizeOfEpoch * numOfEpoch / time_cost / 100))

        est_dict1 = sol1.getEstResult()

        regt = RealExpGenerateAndReadTXT(dirFileName, targetDirName, th1, p, numOfEpoch, sizeOfEpoch)
        real_dict = regt.read()

        ARE_calculate(real_dict, est_dict1)
        F1Score_calculate(real_dict, est_dict1)
