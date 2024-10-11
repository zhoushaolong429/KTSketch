//
// Created by 周少龙 on 2023/7/31.
//

#ifndef KT_1_0_BITMAP_H
#define KT_1_0_BITMAP_H

#include <string.h>
#include <iostream>

using namespace std;

class Bitmap{
public:
    int * bitarray;
    int len;
    int numOfZERO;

    Bitmap(int len) {
        this->len = len;
        this->bitarray = new int[this->len];
        this->numOfZERO = len;
        memset(bitarray, 0, sizeof(int)*len);
//        for (int i = 0; i < len; ++i) {
//            bitarray[i] = 0;
//        }
    }
    ~Bitmap();
    void setONE(int);
    bool isPosONE(int);
    bool isPosZERO(int);
    int getLen() const;
    int getNumOfZERO();
    int getNumOfONE();
    float getEmptyRatio();
    void setAllPosZERO();
};


Bitmap::~Bitmap() {
    delete bitarray;
}

void Bitmap::setONE(int idx) {
    if (this->bitarray[idx] == 0) {
        this->bitarray[idx] = 1;
        this->numOfZERO--;
    }
}

bool Bitmap::isPosONE(int idx) {
    return this->bitarray[idx] == 1;
}

bool Bitmap::isPosZERO(int idx) {
    return this->bitarray[idx] == 0;
}

int Bitmap::getLen() const {
    return this->len;
}

int Bitmap::getNumOfONE() {
    return (this->len - this->numOfZERO);
}

int Bitmap::getNumOfZERO() {
    return this->numOfZERO;
}

float Bitmap::getEmptyRatio() {
    return ((float)this->numOfZERO/ this->len);
}

void Bitmap::setAllPosZERO() {
    memset(this->bitarray, 0, sizeof(int)* this->len);
    this->numOfZERO = this->len;
}

#endif //KT_1_0_BITMAP_H
