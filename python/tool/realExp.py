# RealExpGenerateTXT读取数据集，根据输入的th1、th2、测量周期数来生成真实的测量结果，并写入相应txt文件中
from collections import defaultdict

from tool.myTool import readTXTData, drawBar


def realSpread4OneEpoch(src_list, dst_list, th1):
    flow_table = defaultdict(list)
    dict_flowSpreadGTth1 = dict()
    for i in range(len(src_list)):
        flow_table[src_list[i]].append(dst_list[i])
    for f in flow_table.keys():
        tempLen = len(set(flow_table[f]))
        if tempLen > th1:
            dict_flowSpreadGTth1[f] = tempLen
    return dict_flowSpreadGTth1


class RealExpGenerateAndReadTXT:
    def __init__(self, expDirName, targetDirName, th1, p, numOfEpoch, sizeOfEpoch):
        self.expDirName = expDirName
        self.targetDirName = targetDirName
        self.th1 = th1
        self.p = p
        self.th2 = int(p * numOfEpoch)
        self.numOfEpoch = numOfEpoch
        self.realDict = defaultdict(int)
        self.sizeOfEpoch = sizeOfEpoch

    def generate(self):
        for i in range(self.numOfEpoch):
        # for i in range(1, self.numOfEpoch + 1):
            txtFileName = self.expDirName + str(i) + ".txt"
            src_list, dst_list = readTXTData(txtFileName)
            tempDict = realSpread4OneEpoch(src_list, dst_list, self.th1)
            tempSet = set(tempDict.keys())
            print("测量周期", i, "(真实值) spread大于阈值的流数目", len(tempSet))
            for f in tempSet:
                self.realDict[f] += 1
        tempName = self.targetDirName + str(th1) + "_" + str(p) + "_" + str(self.numOfEpoch) + "_" + str(
            self.sizeOfEpoch) + "w.txt"
        tempf = open(tempName, mode='w')
        for f in self.realDict.keys():
            if self.realDict[f] > self.p * self.numOfEpoch:
                strTemp = str(f) + " " + str(self.realDict[f]) + "\n"
                tempf.write(strTemp)
        tempf.close()
        print("在所有测量周期中，基数大于阈值th1的流数量为", len(self.realDict))
        drawBar(self.realDict, self.numOfEpoch)

    def read(self):
        tempName = self.targetDirName + str(self.th1) + "_" + str(self.p) + "_" + str(self.numOfEpoch) + "_" + str(
            self.sizeOfEpoch) + "w.txt"
        f_list, v_list = readTXTData(tempName)
        tempDict = dict()
        for i in range(len(f_list)):
            tempDict[f_list[i]] = int(v_list[i])
        return tempDict


if __name__ == '__main__':
    sizeOfEpoch = 600
    numOfEpoch = 20
    th1 = 30
    p = 0.6
    th2 = p * numOfEpoch

    # dirFileName = "D:\\a_networkTrace\\CAIDA2016_" + str(sizeOfEpoch) + "wPerTXT\\"
    # targetDirName = "..\\realExpData\\CAIDA2016\\"

    # dirFileName = "D:\\a_networktrace\\Stack Overflow_trace_200wPerTXT\\"
    # targetDirName = "..\\realExpData\\Stack Overflow\\"

    # dirFileName = "D:\\a_networktrace\\univ2_trace_1200wPerTXT\\"
    # targetDirName = "..\\realExpData\\univ2_trace\\"

    dirFileName = "D:\\b_networkTrace\\CAIDA2019_" + str(sizeOfEpoch) + "wPerTXT\\"
    targetDirName = "..\\realExpData\\CAIDA2019\\"

    # dirFileName = "D:\\a_networkTrace\\MAWI2022_" + str(sizeOfEpoch) + "wPerTXT\\"
    # targetDirName = "..\\realExpData\\MAWI\\"

    regt = RealExpGenerateAndReadTXT(dirFileName, targetDirName, th1, p, numOfEpoch, sizeOfEpoch)
    regt.generate()

    # a = regt.read()
    # print(len(a))
