from collections import defaultdict
from matplotlib import pyplot as plt


def readTXTData(txtFileName):
    src_list = []
    dst_list = []
    txtFile = open(txtFileName)
    lines = txtFile.readlines()
    for line in lines:
        temp = line.split()
        src_list.append(temp[0])
        dst_list.append(temp[1])
    txtFile.close()
    return src_list, dst_list


def drawBar(mdict, numOfExpEpoch):
    mdict3 = defaultdict(int)
    for item in mdict.items():
        mdict3[item[1]] += 1
    spreads_x = []
    data_y = []
    for i in range(1, numOfExpEpoch + 1):
        spreads_x.append(i)
        data_y.append(mdict3[i])
    plt.bar(spreads_x, data_y)
    for a, b in zip(spreads_x, data_y):
        plt.text(a, b, (a, b))
    plt.show()


def readRealExpData(txtFileName):
    realDict = dict()
    f_list, value_list = readTXTData(txtFileName)
    for i in range(len(f_list)):
        realDict[f_list[i]] = int(value_list[i])
    return realDict


def ARE_calculate(realDict, estDict):
    are = 0
    tempSet = set(estDict.keys())
    for f in realDict.keys():
        if f in tempSet:
            are += abs(estDict[f] - realDict[f]) / realDict[f]
        else:
            are += 1
    print("ARE:", are / len(realDict.keys()))
    return are / len(realDict.keys())


def F1Score_calculate(realDict, estDict):
    set_real = set(realDict.keys())
    set_est = set(estDict.keys())
    intersection_set = set_real & set_est
    union_set = set_real | set_est
    TP = len(intersection_set)
    FP = len(set_real) - len(intersection_set)
    FN = len(set_est) - len(intersection_set)
    TN = 10000
    print("persistent&bigSpread flow的真实数量为{a}，预测数量为{b}，预测正确的数量为{c}".format(a=len(realDict), b=len(estDict),
                                                                           c=len(intersection_set)))
    # print("预测流数量为", len(estDict), "其中预测正确的数量为", len(intersection_set))
    print("准确率:", len(intersection_set) / len(union_set))
    print("FPR:", FP / (TP + FP))
    print("FNR:", FN / (FN + TN))

    precision = TP / (TP + FP)
    recall = TP / (TP + FN)
    print("precision = ", precision)
    print("recall = ", recall)
    print("F1-Score = ", 2 * precision * recall / (precision + recall))
