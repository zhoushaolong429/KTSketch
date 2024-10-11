from basicDataStruct.freeBS_SSD_hash2bkt import *
from basicDataStruct.vHLL import VHLL
from tool.myTool import *
from tool.realExp import RealExpGenerateAndReadTXT


@total_ordering
class Cell1:
    def __init__(self, flowLabel, est):
        self.flowLabel = flowLabel
        self.est = est

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


class Cell2:
    def __init__(self, flowLabel, counter1):
        self.flowLabel = flowLabel
        self.counter1 = counter1


class Sol2_vHLL:
    def __init__(self, dirFileName, th1, p, numOfEpoch, sizeOfEpoch, sizeOfVHLL, sizeOfS1, sizeOfS2):
        self.dirFileName = dirFileName
        self.th1 = th1
        self.p = p
        self.numOfEpoch = numOfEpoch
        self.th2 = p * numOfEpoch
        self.sizeOfEpoch = sizeOfEpoch

        self.sizeOfVHLL = sizeOfVHLL
        self.sizeOfS1 = sizeOfS1
        self.sizeOfS2 = sizeOfS2

        self.num_registers_for_vhll = 256
        self.num_phy_registers = int(self.sizeOfVHLL * 1024 * 8 / 5)
        self.vhll_instance = VHLL(self.num_phy_registers, self.num_registers_for_vhll)

        self.sizeOfBkt = 8
        self.numOfBkt = int(self.sizeOfS1 * 1024 / 6 / self.sizeOfBkt)
        self.bktArray = []
        for i in range(self.numOfBkt):
            tempBkt = Bkt(self.sizeOfBkt)
            self.bktArray.append(tempBkt)
        self.seed4ChoosingBkt = 2360

        self.summary2 = []
        self.summary2Size = int(self.sizeOfS2 * 1024 / 6)

    def showMem(self):
        print("Sol2_vHLL信息如下：")
        print("测量周期数为{a}，阈值th1为{b}，阈值p为{c}，每个测量周期{d}w个数据包".format(a=self.numOfEpoch, b=self.th1, c=self.p,
                                                                  d=self.sizeOfEpoch))
        print("vHLL大小为：", self.num_phy_registers * 5 / 1024 / 8, "KB")
        print("topkSummary的大小为：", self.sizeOfBkt * self.numOfBkt * 6 / 1024, "KB")
        print("topkSummary有{}个cell".format(self.sizeOfBkt * self.numOfBkt))
        print("summary2的大小为：", self.summary2Size * 6 / 1024, "KB")
        print("summary2有{}个cell".format(self.summary2Size))

    def insertOneElem(self, srcStr, dstStr):
        sss1 = 1234
        sss2 = 4321
        f = mmh3.hash(srcStr, sss1)
        e = mmh3.hash(dstStr, sss2)
        flag = self.vhll_instance.set(f, e)
        if flag == 1:
            est = self.vhll_instance.estimate(f)
            tempCell1 = Cell1(srcStr, est)
            self.insertIntoTopkSummary(tempCell1)

    def opAfterOneEpoch(self):
        num = 0
        for bkt in self.bktArray:
            for cell in bkt.cellArray:
                if cell.est > self.th1:
                    num += 1
                    tempCell2 = Cell2(cell.flowLabel, 1)
                    self.addIntoSummary2(tempCell2)
        print("在这个测量周期加入到summary2的流数量为：", num)
        self.vhll_instance = VHLL(self.num_phy_registers, self.num_registers_for_vhll)

    def insertIntoTopkSummary(self, tempCell1):
        idxOfBkt = mmh3.hash(tempCell1.flowLabel, self.seed4ChoosingBkt, signed=False) % self.numOfBkt
        tempPos = self.bktArray[idxOfBkt].posOfFlowInBkt(tempCell1.flowLabel)
        if tempPos > -1:
            self.bktArray[idxOfBkt].cellArray[tempPos] = tempCell1
            self.bktArray[idxOfBkt].sortBkt()
        else:
            if len(self.bktArray[idxOfBkt].cellArray) == self.sizeOfBkt:
                if tempCell1.est > self.bktArray[idxOfBkt].cellArray[0].est:
                    self.bktArray[idxOfBkt].cellArray[0] = tempCell1
                self.bktArray[idxOfBkt].sortBkt()
            else:
                self.bktArray[idxOfBkt].cellArray.append(tempCell1)
                self.bktArray[idxOfBkt].sortBkt()

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
    for i in range(4) :
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
            sizeOfVHLL = 30
            sizeOfS1 = 10
            sizeOfS2 = 10
        if i == 1:
            sizeOfVHLL = 80
            sizeOfS1 = 10
            sizeOfS2 = 10
        if i == 2 :
            sizeOfVHLL = 130
            sizeOfS1 = 10
            sizeOfS2 = 10
        if i == 3:
            sizeOfVHLL = 180
            sizeOfS1 = 10
            sizeOfS2 = 10


        sol1 = Sol2_vHLL(dirFileName, th1, p, numOfEpoch, sizeOfEpoch, sizeOfVHLL, sizeOfS1, sizeOfS2)
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