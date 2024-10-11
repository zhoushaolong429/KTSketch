//
// Created by 周少龙 on 2023/8/3.
//

#ifndef KT_1_0_VHLL_H
#define KT_1_0_VHLL_H
#include <iostream>
#include <vector>
#include <unordered_map>
#include <cmath>
#include <algorithm>
#include "../hashFunc/hash.h"
using namespace std;

class HyperLogLog {
public:
    int m; // Number of registers (bits)
    std::vector<int> registers;

public:
    HyperLogLog(int precision) {
        m = 1 << precision; // Number of registers is 2^precision
        registers.resize(m, 0);
    }

    HyperLogLog(vector<int> registers) {
        this->registers = registers;
        this->m = this->registers.size();
    }

    void add(int value) {
        // Calculate hash value
        std::hash<int> hash1;
        int hash = hash1(value);

        // Extract index and leading zeros
        int index = hash & (m - 1);
        int leadingZeros = __builtin_clz(hash) + 1;

        // Update the register
        registers[index] = std::max(registers[index], leadingZeros);
    }

    double estimate() {
        double alpha = 0.7213 / (1 + 1.079 / m);
        double sum = 0.0;
        for (int reg: registers) {
            sum += 1.0 / (1 << reg);
        }
        double estimate = alpha * m * m / sum;

        // Apply correction for small cardinalities
        if (estimate <= 5.0 / 2.0 * m) {
            int zeros = std::count(registers.begin(), registers.end(), 0);
            if (zeros != 0) {
                estimate = m * std::log(static_cast<double>(m) / zeros);
            }
        } else if (estimate > 1.0 / 30.0 * 4294967296.0) { // 2^32, 32-bit int
            estimate = -4294967296.0 * std::log(1 - estimate / 4294967296.0);
        }

        return estimate;
    }
};

class VHLL {
public:
    int num_phy_registers;
    int num_vitual_registers_for_a_flow;
    vector<int> seedArray;
    int seed4vhll_fe = 9982;
    vector<int> pyh_registers;


    VHLL(int num_phy_registers, int num_vitual_registers_for_a_flow) {
        this->num_phy_registers = num_phy_registers;
        this->num_vitual_registers_for_a_flow = num_vitual_registers_for_a_flow;
        for (int i = 1000; i < 1256; ++i) {
            this->seedArray.push_back(i);
        }
        this->pyh_registers.resize(this->num_phy_registers, 0);
    }

    int insert(uint64_t f, uint64_t e) {
        uint64_t fe = f + e;
        int hashfe = hash1(fe, this->seed4vhll_fe);
        // virtual pos and rank
        int v_pos = hashfe & (this->num_vitual_registers_for_a_flow - 1);
        int rank = __builtin_clz(hashfe) + 1;
        int phy_pos = hash1(f, this->seedArray[v_pos]) & (this->num_phy_registers - 1);
        if (rank > this->pyh_registers[phy_pos]) {
            this->pyh_registers[phy_pos] = rank;
            return 1;
        } else {
            return 0;
        }
    }

    double query(uint64_t f) {
        vector<int> phy_registers_4f;
        for (int i = 0; i < this->num_vitual_registers_for_a_flow; ++i) {
            int phy_pos = hash1(f, this->seedArray[i]) & (this->num_phy_registers - 1);
            phy_registers_4f.push_back(this->pyh_registers[phy_pos]);
        }
        HyperLogLog *hll = new HyperLogLog(phy_registers_4f);
        return hll->estimate();
    }

};

class CellInVHLL {
public:
    uint64_t flowLabel;
    float est;

    CellInVHLL() {
        this->flowLabel = 0;
        this->est = 0;
    }

    CellInVHLL(uint64_t flowLabel, float est) {
        this->flowLabel = flowLabel;
        this->est = est;
    }

    bool operator<(const CellInVHLL &other) const {
        return est < other.est;
    }
};

class VHLLithSummary1 {
public:
    VHLL *vhll;
    vector<CellInVHLL> cellList;
    int cellListSize;
    float th1 = 50;

    VHLLithSummary1(int num_phy_registers, int num_vitual_registers_for_a_flow, int cellListSize) {
        this->vhll = new VHLL(num_phy_registers, num_vitual_registers_for_a_flow);
        this->cellListSize = cellListSize;
    }

    void insert(uint64_t f, uint64_t e) {
        if (this->vhll->insert(f, e)) {
            float est = this->vhll->query(f);
            int flag = 0;
            for(CellInVHLL& cell : cellList) {
                if (cell.flowLabel==f) {
                    cell.est = est;
                    flag = 1;
                    sort(cellList.begin(), cellList.end());
                    break;
                }
            }
            if (flag == 0) {
                if(cellList.size() < cellListSize) {
                    cellList.push_back(CellInVHLL(f, est));
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
        for(CellInVHLL& cell : cellList) {
            if (cell.est > this->th1) {
                array.push_back(cell.flowLabel);
            }
        }
        return array;
    }

    void opAfterPerPeriod() {

        this->vhll->pyh_registers.resize(this->vhll->num_phy_registers, 0);

        this->cellList.clear();

    }
};



#endif //KT_1_0_VHLL_H
