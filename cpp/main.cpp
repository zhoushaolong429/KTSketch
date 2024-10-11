#include <iostream>
#include <algorithm>
#include "basicDataStruct/Bitmap.h"
#include "hashFunc/hash.h"
#include "../newtest/basicDataStruct/FreeBS_SSD_h2b.h"
#include "basicDataStruct/BloomFilter.h"
#include <cstdlib>
#include <fstream>
#include <vector>
#include <string>
#include <chrono>
#include <io.h>
//<fstream>
#include <iostream>
#include <vector>
#include <cstdint> // For uint64_t
#include <sstream>
#include "sketch/KTSketch.h"
#include "basicDataStruct//CountMin.h"
#include "sketch/BFCM.h"
#include "basicDataStruct/Summary2.h"
#include "basicDataStruct/FreeBS_SSD_Linklist.h"
#include "sketch/VHLL.h"

using namespace std;

uint64_t ipv4ToUInt64(const std::string &ipString);


void readTwoColumnsFromFile(const std::string &filename, std::vector<std::string> &column1,
                            std::vector<std::string> &column2) {
    std::ifstream file(filename);

    if (!file.is_open()) {
        std::cerr << "Failed to open the file: " << filename << std::endl;
        return;
    }

    std::string line;
    while (std::getline(file, line)) {
        size_t pos = line.find(' ');
        if (pos != std::string::npos) {
            column1.push_back(line.substr(0, pos));
            column2.push_back(line.substr(pos + 1));
        }
    }

    file.close();
}

// 函数定义，用于将IPv4地址中的点号去除，并转换为uint64_t类型的数值
uint64_t ipv4ToUInt64(const std::string &ipString) {
    std::string ipv4String = ipString;

    // 使用 std::remove_if 结合 lambda 函数删除字符串中的 '.'
    ipv4String.erase(std::remove_if(ipv4String.begin(), ipv4String.end(), [](char c) {
        return c == '.';
    }), ipv4String.end());

    std::istringstream iss(ipv4String);
    uint64_t ipv4UInt64;
    iss >> ipv4UInt64;

    return ipv4UInt64;
}

uint64_t stringToUint64(const std::string& str) {
    uint64_t result = 0;

    std::istringstream iss(str);
    if (!(iss >> result)) {
        // Handle conversion failure here
        // For example, you could throw an exception or return a default value
        throw std::invalid_argument("Conversion failed");
    }

    return result;
}

// 1.KTSketch
int main() {
    int lenA = 1024 * 8;
    int kA = 2;
    int seedArrayA[] = {100, 101};
    int bitmapSizeB = 32 * 1024 * 8;
    int bktSizeB = 8;   // 一个cell 10B
    int bktNumB = 40 * 1024 / bktSizeB / 10;
    int seed4BitmapB = 110;
    int seed4SummaryB = 111;
    int seed4BitmapInPart3 = 110;
    int lenC = 64 * 1024 * 8;
    int bktSizeC = 8;
    int bktNumC = 40 * 1024 / bktSizeC / 10;
    int seedC = 111;

    KTSketch *ktSketch = new KTSketch(lenA, kA, seedArrayA, bitmapSizeB, bktNumB, bktSizeB, seed4BitmapB, seed4SummaryB,
                                      seed4BitmapInPart3, lenC, bktNumC, bktSizeC, seedC);
    int64_t timeCount = 0;
    int allPacketNum = 10 * 6;

    int wholeMem = 100;

    for (int k = 0; k < 10; ++k) {
        string kStr = to_string(k);
        string filename = "D:\\a_networktrace\\CAIDA2019_600wPerTXT\\" + kStr + ".txt";
//        string filename = "D:\\a_networktrace\\Stack Overflow_trace_200wPerTXT\\" + kStr + ".txt";

        std::vector<std::string> column1;
        std::vector<std::string> column2;
        readTwoColumnsFromFile(filename, column1, column2);

        std::vector<uint64_t> ipv4UInt64Vec1;
        std::vector<uint64_t> ipv4UInt64Vec2;

        // 遍历column中的所有字符串
        for (const std::string &ipString: column1) {
            // 检查是否是IPv4地址，有点号即为IPv4地址
            if (ipString.find('.') != std::string::npos) {
                uint64_t ipv4UInt64 = ipv4ToUInt64(ipString);
                ipv4UInt64Vec1.push_back(ipv4UInt64);
            }
        }
        for (const std::string &ipString: column2) {
            // 检查是否是IPv4地址，有点号即为IPv4地址
            if (ipString.find('.') != std::string::npos) {
                uint64_t ipv4UInt64 = ipv4ToUInt64(ipString);
                ipv4UInt64Vec2.push_back(ipv4UInt64);
            }
        }

//        // 遍历column中的所有字符串
//        for (const std::string &ipString: column1) {
//            uint64_t ipv4UInt64 = stringToUint64(ipString);
//            ipv4UInt64Vec1.push_back(ipv4UInt64);
//        }
//        for (const std::string &ipString: column2) {
//            uint64_t ipv4UInt64 = stringToUint64(ipString);
//            ipv4UInt64Vec2.push_back(ipv4UInt64);
//        }

        // 记录开始时间点
        auto start_time = std::chrono::high_resolution_clock::now();

        // 在这里执行你的程序
        for (int i = 0; i < column1.size(); i++) {
            if (i % 1000000 == 0) {
                cout << i << " has done!" << " ";
//            cout<<"fb->bitmap->numOfZERO:"<<fb->bitmap->numOfZERO<<endl;
//            cout<<"fb->bitmap->getEmptyRatio():"<<fb->bitmap->getEmptyRatio()<<endl;
            }
            ktSketch->work(ipv4UInt64Vec1[i], ipv4UInt64Vec2[i]);
//        fb->insertAPacket(ipv4UInt64Vec1[i], ipv4UInt64Vec2[i]);
        }
        ktSketch->oprationAfterEachPeriod();
        // 记录结束时间点
        auto end_time = std::chrono::high_resolution_clock::now();
        // 计算程序执行时间（以毫秒为单位）
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
        timeCount += duration.count();
        std::cout << "time: " << duration.count() << " ms" << std::endl;
        cout << "period " << k << " has done!!!"<<endl;
    }
    ktSketch->stastics();

    // 将map写入文件中
    std::ofstream outputFile("output.txt");
    if (outputFile.is_open()) {
        // 遍历map的所有键值对，并将它们写入文件
        for (const auto& pair : ktSketch->stasticMap) {
            outputFile << pair.first << " " << pair.second << "\n";
        }
        // 关闭文件
        outputFile.close();
        std::cout << "good!! output.txt" << std::endl;
    } else {
        std::cerr << "bad......" << std::endl;
        return 1;
    }

    cout<< "th2: "<<ktSketch->th2;
    cout<< "numOfPeriod: "<<ktSketch->numOfPeriod;

    cout << "------------------------------"<<endl;
    cout<<"whole mem: "<<wholeMem<<endl;
    cout << "whole time: " << timeCount << " ms" << std::endl;
    cout <<"throughput"<<allPacketNum*1000.0/timeCount<<" Mpps"<<endl;
    return 0;
}

////2.BF+CM
//int main() {
//    int bfSeedArray[] = {857, 858, 859, 860, 861};
//    BFCMWithSummary1 *bfcmWithSummary1 = new BFCMWithSummary1(60*1024 * 8, 2, bfSeedArray, 3, 1706*1024 * 8, 1024);
//    Summary2 *summary2 = new Summary2(1706);
//
//    int64_t timeCount = 0;
//    int allPacketNum = 20 * 6;
//    int wholeMem = 100;
//
//    for (int k = 0; k < 20; ++k) {
//        string kStr = to_string(k);
//        string filename = "D:\\a_networktrace\\CAIDA2019_200wPerTXT\\" + kStr + ".txt";
//        std::vector<std::string> column1;
//        std::vector<std::string> column2;
//        readTwoColumnsFromFile(filename, column1, column2);
//
//        std::vector<uint64_t> ipv4UInt64Vec1;
//        std::vector<uint64_t> ipv4UInt64Vec2;
//
//
//        // 遍历column中的所有字符串
//        for (const std::string &ipString: column1) {
//            // 检查是否是IPv4地址，有点号即为IPv4地址
//            if (ipString.find('.') != std::string::npos) {
//                uint64_t ipv4UInt64 = ipv4ToUInt64(ipString);
//                ipv4UInt64Vec1.push_back(ipv4UInt64);
//            }
//        }
//        for (const std::string &ipString: column2) {
//            // 检查是否是IPv4地址，有点号即为IPv4地址
//            if (ipString.find('.') != std::string::npos) {
//                uint64_t ipv4UInt64 = ipv4ToUInt64(ipString);
//                ipv4UInt64Vec2.push_back(ipv4UInt64);
//            }
//        }
//
//        // 记录开始时间点
//        auto start_time = std::chrono::high_resolution_clock::now();
//
//        // 在这里执行你的程序
//        for (int i = 0; i < column1.size(); i++) {
//            if (i % 2000000 == 0) {
//                cout << i << " has done!" << " ";
//            }
//            bfcmWithSummary1->insert(ipv4UInt64Vec1[i], ipv4UInt64Vec2[i]);
//        }
//        vector<uint64_t> tempArray = bfcmWithSummary1->queryALLElemOVERT();
//
//        summary2->insertAVector(tempArray);
//
//        bfcmWithSummary1->opAfterPerPeriod();
//        // 记录结束时间点
//        auto end_time = std::chrono::high_resolution_clock::now();
//        // 计算程序执行时间（以毫秒为单位）
//        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
//        timeCount += duration.count();
//        std::cout << "time: " << duration.count() << " ms" << std::endl;
//        cout << "period " << k << " has done!!!" << endl;
//    }
//
//    cout << "------------------------------" << endl;
//    cout << "whole mem: " << wholeMem << endl;
//    cout << "whole time: " << timeCount << " ms" << std::endl;
//    cout << "throughput" << allPacketNum * 1000.0 / timeCount << " Mpps" << endl;
//    return 0;
//}

////3.VHLL
//int main() {
////    VHLLithSummary1 * vhlLithSummary1 =new  VHLLithSummary1(1024*256, 128, 1076);
////    Summary2 *summary2 = new Summary2(1706);
//
//    VHLLithSummary1 * vhlLithSummary1 =new  VHLLithSummary1(1024*8*8, 16, 853);
//    Summary2 *summary2 = new Summary2(853);
//
//    int64_t timeCount = 0;
//    int allPacketNum = 20 * 6;
//    int wholeMem = 100;
//
//    for (int k = 0; k < 20; ++k) {
//        string kStr = to_string(k);
//        string filename = "D:\\a_networktrace\\CAIDA2019_600wPerTXT\\" + kStr + ".txt";
////        string filename = "D:\\a.txt";
//
//        std::vector<std::string> column1;
//        std::vector<std::string> column2;
//        readTwoColumnsFromFile(filename, column1, column2);
//
//        std::vector<uint64_t> ipv4UInt64Vec1;
//        std::vector<uint64_t> ipv4UInt64Vec2;
//
//
//        // 遍历column中的所有字符串
//        for (const std::string &ipString: column1) {
//            // 检查是否是IPv4地址，有点号即为IPv4地址
//            if (ipString.find('.') != std::string::npos) {
//                uint64_t ipv4UInt64 = ipv4ToUInt64(ipString);
//                ipv4UInt64Vec1.push_back(ipv4UInt64);
//            }
//        }
//        for (const std::string &ipString: column2) {
//            // 检查是否是IPv4地址，有点号即为IPv4地址
//            if (ipString.find('.') != std::string::npos) {
//                uint64_t ipv4UInt64 = ipv4ToUInt64(ipString);
//                ipv4UInt64Vec2.push_back(ipv4UInt64);
//            }
//        }
//
//        // 记录开始时间点
//        auto start_time = std::chrono::high_resolution_clock::now();
//
//        // 在这里执行你的程序
//        for (int i = 0; i < column1.size(); i++) {
//            if (i % 2000000 == 0) {
//                cout << i << " has done!" << " ";
//            }
//            vhlLithSummary1->insert(ipv4UInt64Vec1[i], ipv4UInt64Vec2[i]);
//        }
//        vector<uint64_t> tempArray = vhlLithSummary1->queryALLElemOVERT();
//
//        summary2->insertAVector(tempArray);
//
//        vhlLithSummary1->opAfterPerPeriod();
//        // 记录结束时间点
//        auto end_time = std::chrono::high_resolution_clock::now();
//        // 计算程序执行时间（以毫秒为单位）
//        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
//        timeCount += duration.count();
//        std::cout << "time: " << duration.count() << " ms" << std::endl;
//        cout << "period " << k << " has done!!!" << endl;
//    }
//
//    cout << "------------------------------" << endl;
//    cout << "whole mem: " << wholeMem << endl;
//    cout << "whole time: " << timeCount << " ms" << std::endl;
//    cout << "throughput" << allPacketNum * 1000.0 / timeCount << " Mpps" << endl;
//    return 0;
//}


//// 4.FreeBS-SSD-DOUBLELINKLIST
//int main() {
//    FreeBS_SSD_Linklist * fsl = new FreeBS_SSD_Linklist(16*1024*8, 3128);
//    Summary2 *summary2 = new Summary2(4266);
//
//    int64_t timeCount = 0;
//    int allPacketNum = 20 * 6;
//    int wholeMem = 100;
//
//    for (int k = 0; k < 20; ++k) {
//        string kStr = to_string(k);
//        string filename = "D:\\a_networktrace\\CAIDA2019_600wPerTXT\\" + kStr + ".txt";
//        std::vector<std::string> column1;
//        std::vector<std::string> column2;
//        readTwoColumnsFromFile(filename, column1, column2);
//
//        std::vector<uint64_t> ipv4UInt64Vec1;
//        std::vector<uint64_t> ipv4UInt64Vec2;
//
//
//        // 遍历column中的所有字符串
//        for (const std::string &ipString: column1) {
//            // 检查是否是IPv4地址，有点号即为IPv4地址
//            if (ipString.find('.') != std::string::npos) {
//                uint64_t ipv4UInt64 = ipv4ToUInt64(ipString);
//                ipv4UInt64Vec1.push_back(ipv4UInt64);
//            }
//        }
//        for (const std::string &ipString: column2) {
//            // 检查是否是IPv4地址，有点号即为IPv4地址
//            if (ipString.find('.') != std::string::npos) {
//                uint64_t ipv4UInt64 = ipv4ToUInt64(ipString);
//                ipv4UInt64Vec2.push_back(ipv4UInt64);
//            }
//        }
//
//        // 记录开始时间点
//        auto start_time = std::chrono::high_resolution_clock::now();
//
//        // 在这里执行你的程序
//        for (int i = 0; i < column1.size(); i++) {
//            if (i % 200000 == 0) {
//                cout << i << " has done!" << " ";
//            }
//            fsl->insert(ipv4UInt64Vec1[i], ipv4UInt64Vec2[i]);
//        }
//        vector<uint64_t> tempArray = fsl->queryALLElemOVERT();
//
//        summary2->insertAVector(tempArray);
//
//        fsl->opAfterPerPeriod();
//        // 记录结束时间点
//        auto end_time = std::chrono::high_resolution_clock::now();
//        // 计算程序执行时间（以毫秒为单位）
//        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
//        timeCount += duration.count();
//        std::cout << "time: " << duration.count() << " ms" << std::endl;
//        cout << "period " << k << " has done!!!" << endl;
//    }
//
//    cout << "------------------------------" << endl;
//    cout << "whole mem: " << wholeMem << endl;
//    cout << "whole time: " << timeCount << " ms" << std::endl;
//    cout << "throughput" << allPacketNum * 1000.0 / timeCount << " Mpps" << endl;
//    return 0;
//}