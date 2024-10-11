from collections import defaultdict
import matplotlib.pyplot as plt
import mmh3
import numpy as np

def readTXTData(txtFileName):
    src_list = []
    dst_list = []
    txtFile = open(txtFileName)
    lines = txtFile.readlines()
    for line in lines:
        temp = line.split()
        src_list.append(temp[0])
        # dst_list.append(temp[1])
    txtFile.close()
    return src_list, dst_list


def count_digits(a):
    # 使用绝对值确保负数也可以正常计算
    a = abs(a)
    # 初始化位数计数为0
    count = 0
    # 循环除以10，每除一次位数计数加1，直到a变为0
    while a > 0:
        a //= 10  # 使用整数除法去掉最右边的一位数字
        count += 1
    return count


class Count_Min():
    def __init__(self, numOfFloor, numOfCounterPerFloor):
        self.numOfFloor = numOfFloor
        self.numOfCounterPerFloor = numOfCounterPerFloor
        seedsArray = []
        for i in range(10):
            temprand = np.random.randint(11, 99999)
            seedsArray.append(temprand)
        self.seeds = seedsArray
        self.countMin = []
        for i in range(0, self.numOfFloor):
            self.countMin.append(np.array([0] * numOfCounterPerFloor))

    def Insert(self, flowLabel):
        for i in range(0, self.numOfFloor):
            pos = mmh3.hash(str(flowLabel), self.seeds[i], False) % len(self.countMin[i])
            self.countMin[i][pos] += 1

    def Query(self, flowLabel):
        res = []
        for i in range(0, self.numOfFloor):
            pos = mmh3.hash(str(flowLabel), self.seeds[i], False) % len(self.countMin[i])
            res.append(self.countMin[i][pos])
        return sorted(res)[0]

    def showMem(self):
        print("Count-Min Sketch各参数信息如下：")
        print("Sketch总内存大小为：{}KB  ".format(self.numOfFloor * self.numOfCounterPerFloor * 4 / 1024))
        print("CountMin层数为：{}".format(self.numOfFloor))
        print("CountMin每层counter数目为：{}".format(self.numOfCounterPerFloor))


class CountMin_UpdateOnce:
    def __init__(self, numOfFloor, numOfCounterPerFloor):
        self.numOfFloor = numOfFloor
        self.numOfCounterPerFloor = numOfCounterPerFloor
        seedsArray = []
        for i in range(10):
            temprand = np.random.randint(11, 99999)
            seedsArray.append(temprand)
        self.seeds = seedsArray
        self.countMin = []
        for i in range(0, self.numOfFloor):
            self.countMin.append(np.array([0] * numOfCounterPerFloor))

    def Insert(self, flowLabel):
        randInt = np.random.randint(0, self.numOfFloor)
        pos = mmh3.hash(str(flowLabel), self.seeds[randInt], False) % len(self.countMin[randInt])
        self.countMin[randInt][pos] += 1

    def Query(self, flowLabel):
        res = []
        for i in range(0, self.numOfFloor):
            pos = mmh3.hash(str(flowLabel), self.seeds[i], False) % len(self.countMin[i])
            res.append(self.countMin[i][pos])
        return sorted(res)[0] * self.numOfFloor

    def showMem(self):
        print("CountMin_UpdateOnce各参数信息如下：")
        print("CountMin_UpdateOnce总内存大小为：{}KB  ".format(self.numOfFloor * self.numOfCounterPerFloor * 4 / 1024))
        print("CountMin_UpdateOnce层数为：{}".format(self.numOfFloor))
        print("CountMin_UpdateOnce每层counter数目为：{}".format(self.numOfCounterPerFloor))

if __name__ == '__main__':
    txtFileName = "D:\\a_networktrace\\CAIDA2019_200wPerTXT\\0.txt"
    src_list, dst_list = readTXTData(txtFileName)
    src_set = set(src_list)
    real_dict = defaultdict(int)
    cm1 = Count_Min(3, 1024*16)
    cm1.showMem()
    for src in src_list:
        cm1.Insert(src)
        real_dict[src] += 1
    est_dict1 = defaultdict(int)
    for src in src_set:
        est_dict1[src] = cm1.Query(src)

    error = [0] * 10
    for src in src_set:
        temp = (real_dict[src] - est_dict1[src])
        error[count_digits(real_dict[src])] += temp
    print("绝对误差：", error)

    print("---------------------------")

    cm2 = CountMin_UpdateOnce(3, 1024*16)
    cm2.showMem()
    for src in src_list:
        cm2.Insert(src)
    est_dict2 = defaultdict(int)
    for src in src_set:
        est_dict2[src] = cm2.Query(src)
    error2 = [0] * 10
    for src in src_set:
        temp = (real_dict[src] - est_dict2[src])
        error2[count_digits(real_dict[src])] += temp
    print("绝对误差：", error2)

    actual_values = []
    estimated_values = []
    for src in src_set:
        actual_values.append(real_dict.get(src))
        estimated_values.append(est_dict2.get(src))

    # 对横坐标和纵坐标进行对数变换
    log_actual_values = np.log10(actual_values)
    log_estimated_values = np.log10(estimated_values)

    # 创建散点图
    plt.scatter(log_actual_values, log_estimated_values, s=5)

    # 设置坐标轴标签
    plt.xlabel('Log(Actual Values)')
    plt.ylabel('Log(Estimated Values)')

    # 设置横坐标和纵坐标刻度为10的幂
    plt.xticks(np.arange(min(log_actual_values), max(log_actual_values) + 1, 1),
               [f'10^{int(x)}' for x in np.arange(min(log_actual_values), max(log_actual_values) + 1, 1)])
    plt.yticks(np.arange(min(log_estimated_values), max(log_estimated_values) + 1, 1),
               [f'10^{int(x)}' for x in np.arange(min(log_estimated_values), max(log_estimated_values) + 1, 1)])

    # 设置图表标题
    plt.title('Scatter Plot with Logarithmic Scale')

    # 添加基准线（对角线）
    plt.plot([min(log_actual_values), max(log_actual_values)], [min(log_actual_values), max(log_actual_values)],
             color='red', linestyle='--')

    # 显示散点图
    plt.show()