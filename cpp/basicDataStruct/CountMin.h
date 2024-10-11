//
// Created by 周少龙 on 2023/8/2.
//

#ifndef KT_1_0_COUNTMIN_H
#define KT_1_0_COUNTMIN_H

#include "../hashFunc/hash.h"
#include <cstring>
#include <algorithm>
using namespace std;
class CountMin{
public:
    int **array;
    int floorNum = 3;
    int floorSize = 0;
    int seedArray[5] ={857,858,859,860,861};
    CountMin(int floorNum, int floorSize) {
        this->floorNum = floorNum;
        this->floorSize = floorSize;
        this->array = new int* [floorNum];
        for (int i = 0; i < floorNum; ++i) {
            this->array[i] = new int[floorSize];
            memset(this->array[i], 0, sizeof(int)*floorSize);
        }
    }

    void insert(uint64_t flowLabel) {
        for (int i = 0; i < floorNum; ++i) {
            int pos = hash1(flowLabel, seedArray[i])%floorSize;
            this->array[i][pos] += 1;
        }
    }

    int query(uint64_t flowLabel) {
        int res[] = {0,0,0};
        for (int i = 0; i < floorNum; ++i) {
            int pos = hash1(flowLabel, seedArray[i])%floorSize;
            res[i] = this->array[i][pos];
        }
        sort(res, res+3);
        return res[0];
    }

    void setAllPosZERO() {
        for (int i = 0; i < this->floorNum; ++i) {
            for (int j = 0; j < this->floorSize; ++j) {
                this->array[i][j] = 0;
            }
        }
    }
};

#endif //KT_1_0_COUNTMIN_H
