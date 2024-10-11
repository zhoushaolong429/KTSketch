from basicDataStruct.bloomFilter import BloomFilter
from basicDataStruct.freeBS_SSD_hash2bkt import *
from tool.myTool import *
from tool.realExp import RealExpGenerateAndReadTXT


@total_ordering
class CellOfSummary2:
    def __init__(self, flowLabel, est, counter1, counter2):
        self.flowLabel = flowLabel
        self.est = est
        self.counter1 = counter1
        self.counter2 = counter2

    def __eq__(self, other):
        return self.est == other.est and \
               self.counter1 - self.counter2 == other.counter1 - other.counter2

    def __gt__(self, other):
        if (self.counter1 - self.counter2 > other.counter1 - other.counter2):
            return True
        elif (self.counter1 - self.counter2 == other.counter1 - other.counter2):
            return self.est > other.est
        else:
            return False


class MyNewSketch_BS_h2b:
    def __init__(self, dirFileName, th1, p, numOfEpoch, sizeOfEpoch, sizeOfBmp1, sizeOfBmp2, sizeOfS1, sizeOfS2):
        seeds = [2343, 2344, 2345, 2346, 2347]
        self.bloomFilter = BloomFilter(1024 * 8, 2, seeds)

        self.n4btmp1 = sizeOfBmp1 * 1024 * 8
        self.s4bkt = 4
        self.n4bkt = int(sizeOfS1 * 1024 / self.s4bkt / 10)
        self.freeBS_SSD = FreeBS_SSD_hash2bkt(self.n4btmp1, self.n4bkt, self.s4bkt, 0.8 * th1)

        self.sizeOfS2 = sizeOfS2
        self.sizeOfBmp2 = sizeOfBmp2
        self.n4btmp2 = sizeOfBmp2 * 1024 * 8
        self.bitmap2 = Bitmap(self.n4btmp2)
        self.seedOfBitmap2 = 2348
        self.s4bkt2 = 16
        self.n4bkt2 = int(sizeOfS2 * 1024 / self.s4bkt2 / 8)
        self.bkt2Array = []
        for i in range(self.n4bkt2):
            tempBkt = Bkt(self.s4bkt2)
            self.bkt2Array.append(tempBkt)
        randseed = np.random.randint(1, 9999)
        self.seed4ChoosingBkt2 = randseed

        self.th1 = th1
        self.p = p
        self.numOfEpoch = numOfEpoch
        self.th2 = p * numOfEpoch
        self.dirFileName = dirFileName
        self.sizeOfEpoch = sizeOfEpoch

    def showMem(self):
        print("mySketch信息如下：")
        print("测量周期数为{a}，阈值th1为{b}，阈值p为{c}，每个测量周期{d}w个数据包".format(a=self.numOfEpoch, b=self.th1, c=self.p,
                                                                  d=self.sizeOfEpoch))
        print("BloomFilter : 1KB")
        self.freeBS_SSD.showMem()
        print("freeBS_SSD.Summary cell数量为", self.n4bkt * self.s4bkt)
        print("bitmap2 :", self.n4btmp2 / 1024 / 8, "KB")
        print("summary2 :", self.n4bkt2 * self.s4bkt2 * 8 / 1024, "KB")  # flowlabel(2B) counter(1B) * 2 counter(4B)
        print("summary2 cell数量为", self.n4bkt2 * self.s4bkt2)

    def insertOneElem(self, srcStr, dstStr):
        if self.bloomFilter.isInBF(srcStr):
            idxOfBkt = mmh3.hash(srcStr, self.seed4ChoosingBkt2, signed=False) % self.n4bkt2
            posInBkt = self.bkt2Array[idxOfBkt].posOfFlowInBkt(srcStr)
            elem = srcStr + dstStr
            pos4Bmp2 = mmh3.hash(elem, self.seedOfBitmap2) % self.bitmap2.size()
            q_B = self.bitmap2.emptyRatio()
            if posInBkt > -1:
                if self.bitmap2.isPosZero(pos4Bmp2):
                    self.bkt2Array[idxOfBkt].cellArray[posInBkt].est += 1 / q_B
                    # self.bkt2Array[idxOfBkt].sortBkt()
                    self.bitmap2.setONE(pos4Bmp2)
            else:
                self.freeBS_SSD.insertOneElem(srcStr, dstStr)
        else:
            self.freeBS_SSD.insertOneElem(srcStr, dstStr)

    def opAfterOneEpoch(self):
        # 先对summary2和bitmap2进行操作
        for bkt2 in self.bkt2Array:
            for cell in bkt2.cellArray:
                if cell.est > self.th1:
                    cell.counter1 += 1
                    cell.counter2 = 0
                else:
                    cell.counter2 += 1
                cell.est = 0
        self.bitmap2 = Bitmap(self.n4btmp2)
        # 再对freeBS_SSD操作
        tempSet = self.freeBS_SSD.getEstSet()
        for f in tempSet:
            tempCell = CellOfSummary2(f, 0, 1, 0)
            self.bloomFilter.insertOneElem(f)
            idxOfBkt = mmh3.hash(f, self.seed4ChoosingBkt2, signed=False) % self.n4bkt2
            if len(self.bkt2Array[idxOfBkt].cellArray) == self.s4bkt2:
                self.bkt2Array[idxOfBkt].sortBkt()
                self.bkt2Array[idxOfBkt].cellArray[0] = tempCell
            else:
                self.bkt2Array[idxOfBkt].cellArray.append(tempCell)
        print("在这个测量周期，添加到summary2的flow数量为", len(tempSet))
        self.freeBS_SSD = FreeBS_SSD_hash2bkt(self.n4btmp1, self.n4bkt, self.s4bkt, 0.8 * self.th1)

    def work(self):
        timeCount = 0

        for i in range(numOfEpoch):
            print("周期", i, " 开始处理...")
            txtFileName = self.dirFileName + str(i) + ".txt"
            src_list, dst_list = readTXTData(txtFileName)

            time_s = time.time()

            for i in range(len(src_list)):
                if i % (200 * 10000) == 0:
                    print("已处理行数：", i)
                self.insertOneElem(src_list[i], dst_list[i])
            self.opAfterOneEpoch()

            time_e = time.time()
            time_cost = time_e - time_s
            timeCount += time_cost
        print("...处理完毕...")
        return timeCount

    def getEstResult(self):
        est_dict = dict()
        for bkt2 in self.bkt2Array:
            for cell in bkt2.cellArray:
                if cell.counter1 > self.th2:
                    est_dict[cell.flowLabel] = cell.counter1
        return est_dict


if __name__ == '__main__':
    for i in range(4):
        print("----------------------------------------------------")
        print("----------------------------------------------------")
        if i == 0:
            wholeMem = 50 - 1
        if i == 1:
            wholeMem = 100 - 1
        if i == 2:
            wholeMem = 150 - 1
        if i == 3:
            wholeMem = 200 - 1

        print("总size", wholeMem + 1)

        sizeOfEpoch = 600
        numOfEpoch = 20
        th1 = 30
        p = 0.6
        th2 = p * numOfEpoch

        dirFileName = "D:\\a_networktrace\\CAIDA2019_600wPerTXT\\"
        targetDirName = "..\\realExpData\\CAIDA2019\\"

        for j in range(5):
            if j == 0:
                ratioOfPart2 = 0.3
                print("-------------------------------------")
                print("ratioOfPart2 :", ratioOfPart2)
                sizeOfBmp1 = int(ratioOfPart2 * wholeMem * 0.3)
                sizeOfBmp2 = int((1 - ratioOfPart2) * wholeMem * 0.3)
                sizeOfS1 = int(ratioOfPart2 * wholeMem * 0.7)
                sizeOfS2 = int((1 - ratioOfPart2) * wholeMem * 0.7)
            if j == 1:
                ratioOfPart2 = 0.4
                print("-------------------------------------")
                print("ratioOfPart2 :", ratioOfPart2)
                sizeOfBmp1 = int(ratioOfPart2 * wholeMem * 0.3)
                sizeOfBmp2 = int((1 - ratioOfPart2) * wholeMem * 0.3)
                sizeOfS1 = int(ratioOfPart2 * wholeMem * 0.7)
                sizeOfS2 = int((1 - ratioOfPart2) * wholeMem * 0.7)
            if j == 2:
                ratioOfPart2 = 0.5
                print("-------------------------------------")
                print("ratioOfPart2 :", ratioOfPart2)
                sizeOfBmp1 = int(ratioOfPart2 * wholeMem * 0.3)
                sizeOfBmp2 = int((1 - ratioOfPart2) * wholeMem * 0.3)
                sizeOfS1 = int(ratioOfPart2 * wholeMem * 0.7)
                sizeOfS2 = int((1 - ratioOfPart2) * wholeMem * 0.7)
            if j == 3:
                ratioOfPart2 = 0.6
                print("-------------------------------------")
                print("ratioOfPart2 :", ratioOfPart2)
                sizeOfBmp1 = int(ratioOfPart2 * wholeMem * 0.3)
                sizeOfBmp2 = int((1 - ratioOfPart2) * wholeMem * 0.3)
                sizeOfS1 = int(ratioOfPart2 * wholeMem * 0.7)
                sizeOfS2 = int((1 - ratioOfPart2) * wholeMem * 0.7)
            if j == 4:
                ratioOfPart2 = 0.7
                print("-------------------------------------")
                print("ratioOfPart2 :", ratioOfPart2)
                sizeOfBmp1 = int(ratioOfPart2 * wholeMem * 0.3)
                sizeOfBmp2 = int((1 - ratioOfPart2) * wholeMem * 0.3)
                sizeOfS1 = int(ratioOfPart2 * wholeMem * 0.7)
                sizeOfS2 = int((1 - ratioOfPart2) * wholeMem * 0.7)

            myNewSketch_BS = MyNewSketch_BS_h2b(dirFileName, th1, p, numOfEpoch, sizeOfEpoch, sizeOfBmp1, sizeOfBmp2,
                                                sizeOfS1, sizeOfS2)
            myNewSketch_BS.showMem()

            time_s = time.time()
            alltime = myNewSketch_BS.work()
            time_e = time.time()
            time_cost = time_e - time_s
            print("总运行时间为", alltime)
            print("吞吐量为{a}Mops".format(a=sizeOfEpoch * numOfEpoch / alltime / 100))

            est_dict0 = myNewSketch_BS.getEstResult()

            regt = RealExpGenerateAndReadTXT(dirFileName, targetDirName, th1, p, numOfEpoch, sizeOfEpoch)
            real_dict = regt.read()

            ARE_calculate(real_dict, est_dict0)
            F1Score_calculate(real_dict, est_dict0)

