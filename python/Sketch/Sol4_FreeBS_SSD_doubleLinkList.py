import time
from collections import defaultdict

from basicDataStruct.freeBS_SSD_doubleLinkList import FreeBS_SSD_doubleLinkList
from tool.myTool import *
from tool.realExp import RealExpGenerateAndReadTXT
from basicDataStruct.doubleLinkList import *


class Cell:
    def __init__(self, flowLabel, counter1):
        self.flowLabel = flowLabel
        self.counter1 = counter1


class Sol4_FreeBS_SSD_doubleLinkList:
    def __init__(self, dirFileName, th1, p, numOfEpoch, sizeOfEpoch, sizeOfBmp1, sizeOfS1, sizeOfS2):
        self.dirFileName = dirFileName
        self.th1 = th1
        self.p = p
        self.numOfEpoch = numOfEpoch
        self.th2 = p * numOfEpoch
        self.sizeOfEpoch = sizeOfEpoch

        self.sizeOfBmp1 = sizeOfBmp1
        self.sizeOfS1 = sizeOfS1
        self.sizeOfS2 = sizeOfS2

        self.n4btmp1 = sizeOfBmp1 * 1024 * 8
        self.freeBS_SSD = FreeBS_SSD_doubleLinkList(self.n4btmp1, int(self.sizeOfS1 * 1024 / 18), th1)

        self.summary2 = []
        self.summary2Size = int(self.sizeOfS2 * 1024 / 6)

    def showMem(self):
        print("Sol3_FreeBS_SSD信息如下：")
        print("测量周期数为{a}，阈值th1为{b}，阈值p为{c}，每个测量周期{d}w个数据包".format(a=self.numOfEpoch, b=self.th1, c=self.p,
                                                                  d=self.sizeOfEpoch))
        self.freeBS_SSD.showMem()
        print("summary2 :", self.summary2Size * 6 / 1024, "KB")
        print("summary2有{}个cell".format(self.summary2Size))

    def insertOneElem(self, srcStr, dstStr):
        self.freeBS_SSD.insertOneElem(srcStr, dstStr)

    def opAfterOneEpoch(self):
        tempSet = self.freeBS_SSD.getEstSet()
        for f in tempSet:
            tempCell = Cell(f, 1)
            self.addIntoSummary2(tempCell)
        print("在这个测量周期，添加到summary的flow数量为", len(tempSet))
        self.freeBS_SSD = FreeBS_SSD_doubleLinkList(self.n4btmp1, int(self.sizeOfS1 * 1024 / 18), th1)

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
    # sizeOfEpoch = 200
    # numOfEpoch = 20
    # th1 = 50
    # p = 0.6
    # th2 = p * numOfEpoch
    #
    # dirFileName = "D:\\a_networkTrace\\CAIDA2019_" + str(sizeOfEpoch) + "wPerTXT\\"
    #
    # sizeOfBmp1 = 20
    # sizeOfS1 = 55
    # sizeOfS2 = 25
    # sol3 = Sol4_FreeBS_SSD_doubleLinkList(dirFileName, th1, p, numOfEpoch, sizeOfEpoch, sizeOfBmp1, sizeOfS1, sizeOfS2)
    # sol3.showMem()
    #
    # time_s = time.time()
    # sol3.work()
    # time_e = time.time()
    # time_cost = time_e - time_s
    # print("总运行时间为", time_cost)
    # print("吞吐量为{a}Mops".format(a=sizeOfEpoch * numOfEpoch / time_cost / 100))
    #
    # est_dict1 = sol3.getEstResult()
    #
    # dirFileName = "D:\\a_networkTrace\\CAIDA2019_600wPerTXT\\"
    # targetDirName = "..\\realExpData\\CAIDA2019\\"
    #
    # regt = RealExpGenerateAndReadTXT(dirFileName, targetDirName, th1, p, numOfEpoch, sizeOfEpoch)
    # real_dict = regt.read()
    #
    # ARE_calculate(real_dict, est_dict1)
    # F1Score_calculate(real_dict, est_dict1)
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

        # if i == 0:
        #     sizeOfBmp1 = 13
        #     sizeOfS1 = 27
        #     sizeOfS2 = 10
        #
        # if i == 1:
        #     sizeOfBmp1 = 20
        #     sizeOfS1 = 55
        #     sizeOfS2 = 25
        #
        # if i == 2 :
        #     sizeOfBmp1 = 60
        #     sizeOfS1 = 60
        #     sizeOfS2 = 30
        #
        # if i == 3:
        #     sizeOfBmp1 = 64
        #     sizeOfS1 = 100
        #     sizeOfS2 = 36

        if i == 0:
            sizeOfBmp1 = 20
            sizeOfS1 = 15
            sizeOfS2 = 15

        if i == 1:
            sizeOfBmp1 = 60
            sizeOfS1 = 20
            sizeOfS2 = 20

        if i == 2 :
            sizeOfBmp1 = 90
            sizeOfS1 = 30
            sizeOfS2 = 30

        if i == 3:
            sizeOfBmp1 = 100
            sizeOfS1 = 50
            sizeOfS2 = 50

        sol3 = Sol4_FreeBS_SSD_doubleLinkList(dirFileName, th1, p, numOfEpoch, sizeOfEpoch, sizeOfBmp1, sizeOfS1,
                                              sizeOfS2)
        sol3.showMem()

        time_s = time.time()
        sol3.work()
        time_e = time.time()
        time_cost = time_e - time_s
        print("总运行时间为", time_cost)
        print("吞吐量为{a}Mops".format(a=sizeOfEpoch * numOfEpoch / time_cost / 100))

        est_dict1 = sol3.getEstResult()

        regt = RealExpGenerateAndReadTXT(dirFileName, targetDirName, th1, p, numOfEpoch, sizeOfEpoch)
        real_dict = regt.read()

        ARE_calculate(real_dict, est_dict1)
        F1Score_calculate(real_dict, est_dict1)
