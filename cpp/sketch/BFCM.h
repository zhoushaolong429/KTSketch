//
// Created by 周少龙 on 2023/8/2.
//

#ifndef KT_1_0_BFCM_H
#define KT_1_0_BFCM_H

#include "../basicDataStruct/CountMin.h"
#include "../basicDataStruct/BloomFilter.h"
#include <vector>

class BFCM {
public:
    BloomFilter *bf;
    CountMin *cm;

    BFCM(int bfLen, int bfK, int *bfSeedArray, int floorNum, int floorSize) {
        this->bf = new BloomFilter(bfLen, bfK, bfSeedArray);
        this->cm = new CountMin(floorNum, floorSize);
    }

    int insert(uint64_t f, uint64_t e) {
        uint64_t fe = f + e;
        if (!this->bf->isFlowInBF(fe)) {
            this->bf->insertOneFlow(fe);
            this->cm->insert(f);
            return 1;
        }
        return 0;
    }

    int query(uint64_t flowLabel) {
        return this->cm->query(flowLabel);
    }
};

class CellInBFCM {
public:
    uint64_t flowLabel;
    float est;

    CellInBFCM() {
        this->flowLabel = 0;
        this->est = 0;
    }

    CellInBFCM(uint64_t flowLabel, float est) {
        this->flowLabel = flowLabel;
        this->est = est;
    }

    bool operator<(const CellInBFCM &other) const {
        return est < other.est;
    }
};

class BFCMWithSummary1 {
public:
    BFCM *bfcm;
    vector<CellInBFCM> cellList;
    int cellListSize;
    float th1 = 50;

    BFCMWithSummary1(int bfLen, int bfK, int *bfSeedArray, int floorNum, int floorSize, int cellListSize) {
        this->bfcm = new BFCM(bfLen, bfK, bfSeedArray, floorNum, floorSize);
        this->cellListSize = cellListSize;
    }

    void insert(uint64_t f, uint64_t e) {
        if (this->bfcm->insert(f, e)) {
            float est = this->bfcm->query(f);
            int flag = 0;
            for(CellInBFCM& cell : cellList) {
                if (cell.flowLabel==f) {
                    cell.est = est;
                    flag = 1;
                    sort(cellList.begin(), cellList.end());
                    break;
                }
            }
            if (flag == 0) {
                if(cellList.size() < cellListSize) {
                    cellList.push_back(CellInBFCM(f, est));
                    sort(cellList.begin(), cellList.end());
                } else {
                    if(est > cellList.front().est) {
                        cellList.front().flowLabel = f;
                        cellList.front().est = est;
                        sort(cellList.begin(), cellList.end());
                    }
                }
            }
        }
    }

    vector<uint64_t> queryALLElemOVERT() {
        vector<uint64_t> array;
        for(CellInBFCM& cell : cellList) {
            if (cell.est > this->th1) {
                array.push_back(cell.flowLabel);
            }
        }
        return array;
    }

    void opAfterPerPeriod() {
        cout << endl << "hello, here!" << endl;

        this->bfcm->bf->bitmap->setAllPosZERO();
        cout << endl << "hello, here22!" << endl;

        this->bfcm->cm->setAllPosZERO();
        cout << endl << "hello, 333!" << endl;

        this->cellList.clear();

    }
};



#endif //KT_1_0_BFCM_H
