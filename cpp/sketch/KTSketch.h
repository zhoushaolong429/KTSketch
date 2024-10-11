//
// Created by 周少龙 on 2023/8/1.
//

#ifndef KT_1_0_KTSKETCH_H
#define KT_1_0_KTSKETCH_H

#include "../hashFunc/hash.h"
#include "../basicDataStruct/BloomFilter.h"
#include "../../newtest/basicDataStruct/FreeBS_SSD_h2b.h"
#include <cmath>
#include <algorithm>
#include <map>
#include <vector>

using namespace std;

class cellOfH3 {
public:
    uint64_t flowLabel;
    float est;
    int n1;
    int n2;
    int weight;

    cellOfH3() {
        flowLabel = 0;
        est = 0;
        n1 = 0;
        n2 = 0;
        weight = 0;
    }

    cellOfH3(uint64_t flowLabel, float est, int n1, int n2, int weight) {
        this->flowLabel = flowLabel;
        this->est = est;
        this->n1 = n1;
        this->n2 = n2;
        this->weight = weight;
    }
};

class SummaryInPart3 {
public:
    cellOfH3 **bktArray;
    int bktNum;
    int bktSize;
    int seed;
    int *cellNumInBkt;

    SummaryInPart3(int bktNum, int bktSize, int seed) {
        this->bktNum = bktNum;
        this->bktSize = bktSize;
        this->seed = seed;
        this->bktArray = new cellOfH3 *[bktNum];
        for (int i = 0; i < bktNum; i++) {
            this->bktArray[i] = new cellOfH3[bktSize];
        }
        cellNumInBkt = new int[bktNum];
        for (int i = 0; i < bktNum; ++i) {
            cellNumInBkt[i] = 0;
        }
    }

    int posOfFlowInBkt(unsigned int idx4Bkt, uint64_t flowLabel) {
        for (int i = 0; i < this->bktSize; ++i) {
            if (flowLabel == this->bktArray[idx4Bkt][i].flowLabel) {
                return i;
            }
        }
        return -1;
    }

};

class KTSketch {
public:
    BloomFilter *bf;
    FreeBS_SSD_h2b *part2;
    int seed4BitmapInPart3;
    Bitmap *bitmapInPart3;
    SummaryInPart3 *summaryInPart3;
    int th1 = 50;
    double th2 = 0.6;
    int numOfPeriod = 10;
    float lamda = 0.8;
    map<uint64_t, int> stasticMap;

    KTSketch(int lenA, int kA, int *seedArrayA, int bitmapSizeB, int bktNumB, int bktSizeB, int seed4BitmapB,
             int seed4SummaryB,int seed4BitmapInPart3, int lenC, int bktNumC, int bktSizeC, int seedC) {
        bf = new BloomFilter(lenA, kA, seedArrayA);
        part2 = new FreeBS_SSD_h2b(bitmapSizeB, bktNumB, bktSizeB, seed4BitmapB, seed4SummaryB);
        bitmapInPart3 = new Bitmap(lenC);
        summaryInPart3 = new SummaryInPart3(bktNumC, bktSizeC, seedC);
        this->seed4BitmapInPart3 = seed4BitmapInPart3;
    }

    void InsertIntopart3(uint64_t f, uint64_t e) {
        uint64_t fe = f + e;
        int hash4Bitmap = hash1(fe, this->seed4BitmapInPart3) % this->bitmapInPart3->getLen();
//        int hash4Bitmap = hash1(fe, this->seed4BitmapInPart3) & (this->bitmapInPart3->getLen()-1);
        if (this->bitmapInPart3->isPosZERO(hash4Bitmap)) {
            unsigned int idx4Bkt = hash1(f, this->summaryInPart3->seed) % this->summaryInPart3->bktNum;
            int posOfFlowInBkt = this->summaryInPart3->posOfFlowInBkt(idx4Bkt ,f);
            if (posOfFlowInBkt > 0) {
                float q_B = this->bitmapInPart3->getEmptyRatio();
                float est = 1 / q_B;
                this->summaryInPart3->bktArray[idx4Bkt][posOfFlowInBkt].est += est;
                this->bitmapInPart3->setONE(hash4Bitmap);
            } else {
                this->part2->insertAPacket(f, e);
            }
        }
    }

    void work(uint64_t f, uint64_t e) {
        if (this->bf->isFlowInBF(f)) {
            this->InsertIntopart3(f, e);
        } else {
            this->part2->insertAPacket(f ,e);
        }
    }

    void stastics() {
        for (int i = 0; i < this->summaryInPart3->bktNum; i++) {
            for (int j = 0; j < this->summaryInPart3->cellNumInBkt[i]; ++j) {
                if (this->summaryInPart3->bktArray[i][j].n2 > this->th2 * this->numOfPeriod) {
                    this->stasticMap[this->summaryInPart3->bktArray[i][j].flowLabel] = this->summaryInPart3->bktArray[i][j].n2;
                }
            }
        }
    }

    void oprationAfterEachPeriod() {
        for (int i = 0; i < this->summaryInPart3->bktNum; i++) {
            for (int j = 0; j < this->summaryInPart3->cellNumInBkt[i]; ++j) {
                if (this->summaryInPart3->bktArray[i][j].est > this->th1) {
                    this->summaryInPart3->bktArray[i][j].n1++;
                    this->summaryInPart3->bktArray[i][j].n2=0;
                } else {
                    this->summaryInPart3->bktArray[i][j].n2++;
                }
            }
        }

        for (int i = 0; i < this->part2->summary->bktNum; ++i) {
            for (int j = 0; j < this->part2->summary->cellNumInBkt[i]; ++j) {
                if (fabs(this->part2->summary->bktArray[i][j].est - this->part2->summary->bktArray[i][j].error) > this->lamda * this->th1) {
                    uint64_t fTemp = this->part2->summary->bktArray[i][j].flowLabel;
                    this->bf->insertOneFlow(fTemp);
                    int idxOfBkt3 = hash1(fTemp, this->summaryInPart3->seed) % this->summaryInPart3->bktNum;
                    if (this->summaryInPart3->cellNumInBkt[idxOfBkt3] == this->summaryInPart3->bktSize) {
                        this->summaryInPart3->bktArray[idxOfBkt3][this->summaryInPart3->bktSize - 1].flowLabel = fTemp;
                        this->summaryInPart3->bktArray[idxOfBkt3][this->summaryInPart3->bktSize - 1].n1 = 1;
                        this->summaryInPart3->bktArray[idxOfBkt3][this->summaryInPart3->bktSize - 1].n2 = 0;
                    } else{
                        this->summaryInPart3->bktArray[idxOfBkt3][this->summaryInPart3->cellNumInBkt[idxOfBkt3]].flowLabel = fTemp;
                        this->summaryInPart3->bktArray[idxOfBkt3][this->summaryInPart3->cellNumInBkt[idxOfBkt3]].n1 = 1;
                        this->summaryInPart3->bktArray[idxOfBkt3][this->summaryInPart3->cellNumInBkt[idxOfBkt3]].n2 = 0;
                        this->summaryInPart3->cellNumInBkt[idxOfBkt3]++;
                    }
                    sort(this->summaryInPart3->bktArray[idxOfBkt3], this->summaryInPart3->bktArray[idxOfBkt3] + this->summaryInPart3->bktSize,
                         [](const cellOfH3 &c1, const cellOfH3 &c2) {
                             return (c1.n1 - c1.n2) > (c2.n1 - c2.n2);
                         });
                }
            }
        }

        memset(this->part2->bitmap->bitarray, 0, sizeof(int)*this->part2->bitmap->getLen());
        this->part2->bitmap->numOfZERO = this->part2->bitmap->getLen();
        memset(this->bitmapInPart3->bitarray, 0, sizeof(int)*this->bitmapInPart3->getLen());
        this->bitmapInPart3->numOfZERO = this->bitmapInPart3->getLen();
        for (int i = 0; i < this->summaryInPart3->bktNum; i++) {
            for (int j = 0; j < this->summaryInPart3->bktSize; ++j) {
                this->summaryInPart3->bktArray[i][j].est = 0;
            }
        }
        for (int i = 0; i < this->part2->summary->bktNum; ++i) {
            for (int j = 0; j < this->part2->summary->bktSize; ++j) {
                this->part2->summary->bktArray[i][j].est = 0;
                this->part2->summary->bktArray[i][j].flowLabel = 0;
                this->part2->summary->bktArray[i][j].error = 0;
            }
        }
        memset(this->part2->summary->cellNumInBkt, 0, sizeof(int)*this->part2->summary->bktNum);
    }
};

#endif //KT_1_0_KTSKETCH_H
