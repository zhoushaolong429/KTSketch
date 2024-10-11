//
// Created by 周少龙 on 2023/8/1.
//

#ifndef KT_1_0_BLOOMFILTER_H
#define KT_1_0_BLOOMFILTER_H

#include "Bitmap.h"
#include "../hashFunc/MurmurHash.h"

class BloomFilter {
public:
    int len;
    int k;
    int *seedArray;
    Bitmap *bitmap;

    BloomFilter(int len, int k, int* seedArray) {
        this->len = len;
        this->k = k;
        this->seedArray = seedArray;
        this->bitmap = new Bitmap(len);
    }

    void insertOneFlow(uint64_t flowLabel) {
        for (int i = 0; i < this->k; ++i) {
            unsigned int pos = hash1(flowLabel, this->seedArray[i]) % this->len;
            this->bitmap->setONE(pos);
        }
    }

    bool isFlowInBF(uint64_t flowLabel) {
        for (int i = 0; i < this->k; ++i) {
            int pos = hash1(flowLabel, this->seedArray[i]) % this->len;
            if (this->bitmap->isPosZERO(pos)) {
                return false;
            }
        }
        return true;
    }
};

#endif //KT_1_0_BLOOMFILTER_H
