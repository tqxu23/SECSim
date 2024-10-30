
import ephem
from ephem import degree
import numpy as np
class Task:


# https://satsearch.co/products/simera-sense-triscape100
# 拍摄throughput  = 150*4096*3072/512/512 = 9000 (张/s)
# 传输throughput(原始) = 2*10^6 / (512*512*3) ~ 2.5431 (张/s)
    sensing_throughput = 9000
    communication_throughput = 2.54
    # communication_throughput = 0.54

    inference_throughput = 4
    # size代表处理遥感图片的块数,默认512*512为一块
    def __init__(self, id:int, observer:ephem.Observer, size:int):
        self.observer:ephem.Observer = observer
        self.id:int = id
        self.size:int = size
        self.scatter_on_map = None
        self.completed:bool = False
        self.on_sat:bool = False
        self.sensor_left:int = size
        self.inference_left:int = 0
        self.communication_left:int = 0

        self.sat = ""

    def __str__(self):
        return f"TaskInfo: {self.id}, {self.observer}"

    def get_position(self):
        return self.observer.lon / degree, self.observer.lat / degree


    def perform_sensing(self,amount:int):
        # assert self.sensor_left >= amount, "Perform too many sensing tasks!"
        if self.sensor_left < amount:
            self.inference_left+=self.sensor_left
            self.sensor_left = 0
        else:
            self.sensor_left-=amount
            self.inference_left+=amount

    def perform_inference(self,amount:int):
        # assert self.sensor_left >= amount, "Perform too many sensing tasks!"
        if self.inference_left < amount:
            self.communication_left+=self.inference_left
            self.inference_left = 0
        else:
            self.inference_left-=amount
            self.communication_left+=amount

    def perform_communication(self,amount:int):
        # assert self.sensor_left >= amount, "Perform too many sensing tasks!"
        self.communication_left -=amount
        if self.communication_left < 0:
            self.communication_left = 0
        if self.sensor_left==0 and self.inference_left==0 and self.communication_left==0:
            self.completed = True
            self.on_sat = False
            print(f"Task {self.id} finished!")

    def update_view(self, map):
        sublong, sublat = self.get_position()
        if self.scatter_on_map==None:
            self.scatter_on_map = map.scatter([sublong], [sublat], latlon=True, alpha=0.9, zorder=5, marker='^',s=50, c='black')
            if self.completed:
                self.scatter_on_map.set_alpha(0.2)
            elif self.on_sat: 
                self.scatter_on_map.set_alpha(0.5)
            else:
                self.scatter_on_map.set_alpha(0.9)
        else:
            self.scatter_on_map.set_offsets(np.c_[[sublong],[sublat]])
            if self.completed:
                self.scatter_on_map.set_alpha(0.2)
            elif self.on_sat: 
                self.scatter_on_map.set_alpha(0.5)
            else:
                self.scatter_on_map.set_alpha(0.9)

