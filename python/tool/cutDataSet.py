from tool.myTool import readTXTData


def writeIntoTXT(src_list, dst_lst, txtFileName):
    f = open(txtFileName, mode='w')
    for i in range(len(src_list)):
        strTemp = str(src_list[i]) + " " + str(dst_lst[i]) + "\n"
        f.write(strTemp)
    f.close()


if __name__ == '__main__':
    sizeOfEpoch = 600
    n = sizeOfEpoch
    dirName = "D:\\a_networkTrace\\CAIDA2016_" + str(n) + "wPerTXT\\"
    txtName = "D:\\a_networktrace\\CAIDA2016\\03.txt"
    # dirName = "D:\\a_networktrace\\Stack Overflow_trace_200wPerTXT\\"
    # txtName = "D:\\a_networktrace\\Stack Overflow_trace\\sx-Stack Overflow-c2q.txt"
    # dirName = "D:\\b_networkTrace\\CAIDA2019_" + str(n) + "wPerTXT\\"
    # txtName = "D:\\a_networktrace\\CAIDA2019\\16.txt"
    # dirName = "D:\\a_networkTrace\\MAWI2022_" + str(n) + "wPerTXT\\"
    # txtName = "D:\\a_networktrace\\MAWI2022\\00.txt"
    src_list, dst_list = readTXTData(txtName)
    print(len(src_list))
    j = 0
    for i in range(15,20):
        txtFileName = dirName + str(i) + ".txt"
        writeIntoTXT(src_list[j * n * 10000:(j + 1) * n * 10000], dst_list[j * n * 10000:(j + 1) * n * 10000],
                     txtFileName)
        j += 1
        print(i, "已完成...")

