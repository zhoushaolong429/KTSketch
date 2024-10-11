//
// Created by 周少龙 on 2023/8/2.
//

#ifndef KT_1_0_FREEBS_SSD_LINKLIST_H
#define KT_1_0_FREEBS_SSD_LINKLIST_H

#include "../hashFunc/hash.h"
#include "Bitmap.h"
#include <cmath>
#include <list>
#include <algorithm>

using namespace std;

class CellOfList {
public:
    uint64_t flowLabel;
    float est = 0;
    float error = 0;

    CellOfList() {
        flowLabel = 0;
        est = 0;
        error = 0;
    }

    CellOfList(uint64_t flowLabel, float est, float error) {
        this->flowLabel = flowLabel;
        this->est = est;
        this->error = error;
    }
};

bool comparePeople(const CellOfList &c1, const CellOfList &c2) {
    return c1.est < c2.est;
}

class FreeBS_SSD_Linklist {
public:
    Bitmap *bitmap;
    list<CellOfList> cellList;
    int sizeOfList;
    int th1 = 50;
    int seed4Bitmap = 10086;

    FreeBS_SSD_Linklist(int bitmapSize, int sizeOfList) {
        this->bitmap = new Bitmap(bitmapSize);
        this->sizeOfList = sizeOfList;
        list<CellOfList> cellList;
    }

    // 自定义插入函数，保持列表的有序性
    void insertSorted(std::list<CellOfList>& myList, const CellOfList& cell) {
        auto it = myList.begin();
        while (it != myList.end() && cell.est > it->est) {
            ++it;
        }
        myList.insert(it, cell);
    }

    // 修改元素的 age 属性并保持有序性
    int modifyEstAndSort(std::list<CellOfList>& myList, const std::uint64_t & flowLabel, float newEst) {
        auto it = std::find_if(myList.begin(), myList.end(), [&flowLabel](const CellOfList& cell) {
            return cell.flowLabel == flowLabel;
        });

        if (it != myList.end()) {
            it->est += newEst;

            CellOfList modifiedPerson = *it;
            myList.erase(it);

            insertSorted(myList, modifiedPerson);
            return 1;
        }
        return 0;
    }

    void insert(uint64_t f, uint64_t e) {
        uint64_t fe = f + e;
//        int hashVal = hash1(fe, this->seed4Bitmap) % this->bitmap->getLen();
        int hashVal = hash1(fe, this->seed4Bitmap) & (this->bitmap->getLen() - 1);
        if (this->bitmap->isPosZERO(hashVal)) {
            float q_B = this->bitmap->getEmptyRatio();
            float est = 1 / q_B;
            int flag = this->modifyEstAndSort(this->cellList, f, est);
            if (flag == 0) {
                if (this->cellList.size() < this->sizeOfList) {
                    insertSorted(this->cellList, CellOfList(f, est, 0));
                } else {
                    float p_t = est / (est + this->cellList.front().est);
                    int randomInt = rand();
                    float randomValue = static_cast<float>(randomInt) / RAND_MAX;
                    if (randomValue <= p_t) {
                        this->cellList.front().flowLabel = f;
                        this->cellList.front().error = this->cellList.front().est;
                        this->cellList.front().est += est;
                        CellOfList temp = cellList.front();
                        cellList.pop_front();
                        insertSorted(this->cellList, temp);
                    } else {
                        this->cellList.front().est += est;
                        CellOfList temp = cellList.front();
                        cellList.pop_front();
                        insertSorted(this->cellList, temp);
                    }
                }
            }
            this->bitmap->setONE(hashVal);
        }
    }

    vector<uint64_t> queryALLElemOVERT() {
        vector<uint64_t> array;
        for (CellOfList &cell: cellList) {
            if (cell.est > this->th1) {
                array.push_back(cell.flowLabel);
            }
        }
        return array;
    }

    void opAfterPerPeriod() {
        this->bitmap->setAllPosZERO();
        this->cellList.clear();
    }

};

#endif //KT_1_0_FREEBS_SSD_LINKLIST_H
