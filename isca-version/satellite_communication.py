class CommunicationSystem:

    def __init__(self, start_time, power_cost = 1):
        self.power_cost = power_cost
        self.cur_time = start_time

    
        self.date_list : list[float] = []
        self.ison_trace : list[float] = []
        self.power_trace : list[float]= []
        self.visible_trace : list[float]= []


    def trace(self,date, visible, ison, power):
        self.date_list.append(date)
        self.ison_trace.append(ison)
        self.power_trace.append(power)
        self.visible_trace.append(visible)

        
    def step(self, ison, cur_time, visible):
        assert self.cur_time < cur_time, "Current time back in Communication System!"
        step_size = cur_time - self.cur_time
        self.cur_time = cur_time
        power = 0        
        if ison:
            power += self.power_cost

        self.trace(date=cur_time, visible=visible, ison = ison, power = power)

        return power