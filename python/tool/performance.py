class PerformanceClas:

    def __init__(self, real_dict, est_dict, th):
        self.real_dict = real_dict
        self.est_dict = est_dict
        self.th = th

    def performance(self):
        # 小于基数th的流控制AAE，否则控制ARE
        aae, are = 0.0, 0.0
        count1, count2 = 0, 0
        for key in self.est_dict.keys():
            if key in self.real_dict.keys():
                if self.real_dict[key] <= self.th:
                    aae += abs(self.est_dict[key] - self.real_dict[key])
                    count1 += 1
                else:
                    are += abs(self.est_dict[key] - self.real_dict[key]) / self.real_dict[key]
                    count2 += 1
        if count1 > 0 and count2 > 0:
            return aae / count1, are / count2
        else:
            if count1 > 0 and count2 == 0:
                return aae / count1, -1
            else:
                return -1, are / count2
