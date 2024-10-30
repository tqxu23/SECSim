import ephem
class InferenceSystem:

    def __init__(self, start_time, power_cost = 10):
        self.power_cost : float = power_cost
        self.cur_time = start_time

        self.date_list : list[float] = []
        self.ison_trace : list[float] = []
        self.power_trace : list[float] = []


    def trace(self,date, ison, power):
        self.date_list.append(date)
        self.ison_trace.append(ison)
        self.power_trace.append(power)

    def step(self, ison, cur_time):
        assert self.cur_time < cur_time, "Current time back in Inference System!"
        step_size = cur_time - self.cur_time
        self.cur_time = cur_time
        power = 0        
        if ison:
            power += self.power_cost

        self.trace(date=cur_time, ison = ison, power = power)
        
        return power
