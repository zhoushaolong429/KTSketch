# from basicDataStruct.BasicFunc import gen_rand_seed, gen_hash
import math
import mmh3
import random

class VHLL():

    def __init__(self, num_phy_registers, num_registers_for_vhll):
        self.num_phy_registers = num_phy_registers
        self.num_registers_for_vhll = num_registers_for_vhll

        distinct_seeds = set()
        while len(distinct_seeds) < num_registers_for_vhll:
            seed_t = gen_rand_seed()
            if seed_t not in distinct_seeds:
                distinct_seeds.add(seed_t)
        self.seeds = list(distinct_seeds)
        self.range_for_seed_index = math.floor(math.log(self.num_registers_for_vhll, 2))
        self.hash_seed = gen_rand_seed()

        self.phy_registers = [0 for i in range(num_phy_registers)]
        self.flows = set()

        self.spread_of_all_flows = 0
        self.alpha = 0
        if self.num_registers_for_vhll == 16:
            self.alpha = 0.673
        elif self.num_registers_for_vhll == 32:
            self.alpha = 0.697
        elif self.num_registers_for_vhll == 64:
            self.alpha = 0.709
        else:
            self.alpha = (0.7213 / (1 + (1.079 / self.num_registers_for_vhll)))

    def set(self, flow_id, ele_id):
        self.flows.add(flow_id)

        ele_hash_value = gen_hash(ele_id, self.hash_seed)
        p_part = ele_hash_value >> (32 - self.range_for_seed_index)
        q_part = ele_hash_value - (p_part << (32 - self.range_for_seed_index))

        leftmost_index = 0
        while q_part:
            leftmost_index += 1
            q_part >>= 1
        leftmost_index = 32 - self.range_for_seed_index - leftmost_index + 1

        index_for_register = gen_hash(flow_id ^ self.seeds[p_part], self.hash_seed) % self.num_phy_registers
        if leftmost_index > self.phy_registers[index_for_register]:
            self.phy_registers[index_for_register] = leftmost_index
            return 1
        else:
            self.phy_registers[index_for_register] = self.phy_registers[index_for_register]
            return -1

    def update_para(self):
        fraction_zeros = 0
        sum_registers = 0
        for register in self.phy_registers:
            sum_registers += 2 ** (-register)
            if register == 0:
                fraction_zeros += 1
        fraction_zeros = fraction_zeros / self.num_phy_registers
        spread_of_all_flows = (0.7213 / (1 + (1.079 / self.num_phy_registers))) * (
                self.num_phy_registers ** 2) / sum_registers
        if spread_of_all_flows < 2.5 * self.num_phy_registers:
            if fraction_zeros != 0:
                self.spread_of_all_flows = - self.num_phy_registers * math.log(fraction_zeros)
        elif spread_of_all_flows > 2 ** 32 / 30:
            self.spread_of_all_flows = - 2 ** 32 * math.log(1 - spread_of_all_flows / 2 ** 32)

    def estimate(self, flow_id):
        fraction_zeros_for_vhll = 0
        sum_registers_for_vhll = 0
        for seed in self.seeds:
            index_for_vhll = gen_hash(flow_id ^ seed, self.hash_seed) % self.num_phy_registers
            sum_registers_for_vhll += 2 ** (- self.phy_registers[index_for_vhll])
            if self.phy_registers[index_for_vhll] == 0:
                fraction_zeros_for_vhll += 1
        fraction_zeros_for_vhll = fraction_zeros_for_vhll / self.num_registers_for_vhll
        spread_of_the_flow = self.alpha * (self.num_registers_for_vhll ** 2) / sum_registers_for_vhll

        if spread_of_the_flow < 2.5 * self.num_registers_for_vhll:
            if fraction_zeros_for_vhll != 0:
                spread_of_the_flow = - self.num_registers_for_vhll * math.log(fraction_zeros_for_vhll) - \
                                     (self.num_registers_for_vhll * self.spread_of_all_flows / self.num_phy_registers)
            else:
                spread_of_the_flow = spread_of_the_flow - \
                                     (self.num_registers_for_vhll * self.spread_of_all_flows / self.num_phy_registers)
        elif spread_of_the_flow > 2 ** 32 / 30:
            spread_of_the_flow = - 2 ** 32 * math.log(1 - spread_of_the_flow / 2 ** 32) - \
                                 (self.num_registers_for_vhll * self.spread_of_all_flows / self.num_phy_registers)
        else:
            spread_of_the_flow = spread_of_the_flow - \
                                 (self.num_registers_for_vhll * self.spread_of_all_flows / self.num_phy_registers)

        return spread_of_the_flow

    def get_all_spread(self):
        self.update_para()
        all_spread = {}
        for flow_id in self.flows:
            all_spread[flow_id] = self.estimate(flow_id)
            # print(all_spread[flow_id])
        return all_spread


def gen_rand_seed():
    return random.randint(0, 2 ** 32)


def gen_hash(key, seed=None):
    if seed is None:
        seed = gen_rand_seed()
    hash_value = mmh3.hash(str(key), seed, False) % (2 ** 32)
    return hash_value
