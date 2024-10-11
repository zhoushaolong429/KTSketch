//
// Created by 周少龙 on 2023/8/2.
//

#ifndef KT_1_0_SUMMARY2_H
#define KT_1_0_SUMMARY2_H

#include "../hashFunc/hash.h"
#include <cstring>
#include <algorithm>

using namespace std;

class Cellhere {
public:
    uint64_t flowLabel;
    int n1;
    int n2;
    int n3;

    Cellhere() {
        this->flowLabel = 0;
        this->n1 = 0;
        this->n2 = 0;
        this->n3 = 1;
    }

    Cellhere(uint64_t flowLabel, int n1, int n2, int n3) {
        this->flowLabel = flowLabel;
        this->n1 = n1;
        this->n2 = n2;
        this->n3 = n3;
    }

    bool operator<(const Cellhere &other) const {
        return n1 - n2 < (other.n1 - other.n2);
    }

};


class Summary2 {
public:
//    vector<Cellhere> cellListArray[100];
    vector<Cellhere> cellList;
    int size;

    Summary2(int size) {
        this->size = size;
    }

    void insertAVector(vector<uint64_t> array) {
        for (int i = 0; i < array.size(); ++i) {
            int flag = 0;
            for (int j = 0; j < cellList.size(); ++j) {
                if (cellList[j].flowLabel == array[i]) {
                    cellList[j].n1++;
                    cellList[j].n2 = 0;
                    cellList[j].n3 = 0;
                    flag = 1;
                    sort(cellList.begin(), cellList.end());
                }
            }
            if (flag == 0) {
                if (cellList.size() < this->size) {
                    cellList.push_back(Cellhere(array[i], 1, 0, 0));
                    sort(cellList.begin(), cellList.end());
                } else {
                    cellList[0].flowLabel = array[i];
                    cellList[0].n1 = 1;
                    cellList[0].n2 = 0;
                    cellList[0].n3 = 0;
                }
            }

        }
        for (int i = 0; i < cellList.size(); ++i) {
            cellList[i].n2 += cellList[i].n3;
            cellList[i].n3 = 1;
        }
    }
};

#endif //KT_1_0_SUMMARY2_H
