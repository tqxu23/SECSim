from ground_station import GroundStation
import ephem
import random
import math
from ephem import degree
import numpy as np
from task import Task
from satellite import Satellite
import copy
import datetime

class Info:
    def __init__(self,sat,content,size,slice,all):
        self.sat = sat
        self.content = content
        self.size = size
        self.slice = slice
        self.all = all
    def __str__(self):
        return f"{self.sat},{self.content}"

class Ground:
    def __init__(self):
        self.task_id_top:int = 0
        self.ground_stations : list[GroundStation] = []    
        self.ground_stations.append(GroundStation(name="Boston", observer=ephem.city('Boston')))
        self.ground_stations.append(GroundStation(name="Shanghai", observer=ephem.city('Shanghai')))
        self.ground_stations.append(GroundStation(name="Beijing", observer=ephem.city('Beijing')))
        self.tasks : list[Task] = []

    # def __init__(self,ground_stations):
    #     self.ground_stations = ground_stations

# https://satsearch.co/products/simera-sense-triscape100
# 按~5m精度计算，1000就是1.25k平方公里，差不多在一个城市大小
    def generate_task(self, maxsize = 5000):
        lon = random.uniform(-math.pi,math.pi)
        lat = random.uniform(-math.pi/2,math.pi/2)
        observer = ephem.Observer()
        observer.lon = ephem.degrees(lon)
        observer.lat = ephem.degrees(lat)
        size = random.randint(maxsize/2,maxsize)
        task = Task(self.task_id_top, observer,size)
        self.task_id_top +=1
        return task
    
    def send_task(self, task:Task, sat:Satellite):
        assert sat.visible, "not visible! send task failed..."
        assert not task.completed, "task is completed! failed..."
        assert not task.on_sat, "task is already on satellite! failed..."
        print(f"send task {task} to satellite {sat}")
        sat.get_task_from_ground(task)       

    def send_random_task(self,sat:Satellite):
        if not sat.can_accept_task():
            return
        task:Task = self.generate_task(maxsize = 1000)
        self.tasks.append(task)
        self.send_task(task,sat)
        # for t in self.tasks:
        #     if t.completed == False and t.on_sat == False:
        #         self.send_task(t,sat)
        #         break

    def step_task_pool(self, task_size: int, sats: list[Satellite], step:int,max_lat:int):
        count = 0
        for t in self.tasks:
            if not t.completed:
                count = count + 1
        while count < task_size:
            best_sat = None
            min_lat = datetime.timedelta(seconds=max_lat)
            while best_sat == None:
                t = self.generate_task(maxsize=5000)
                for s in sats:
                    [suitable, cur_lat] = self.task_e2e_lat_min(t, s, step, max_lat)
                    if suitable and cur_lat < min_lat:
                        min_lat = cur_lat
                        best_sat = s
            self.tasks.append(t)
            count+=1
            print(t)
            t.sat = best_sat.name

    # 判断当前task是不是应该给当前satellite
    def is_task_suitable_for_sat(self, task:Task, sat:Satellite):
        return task.sat == sat.name
        # if not suitable:
        #     return False
        # for s in sats:    
        #     [suitable, cur_lat] = self.task_e2e_lat_min(task, s, step, min_lat)
        #     if cur_lat < min_lat:
        #         return False
        # return True

    # 判断当前的task最快的感知时延
    def task_sensing_lat_min(self, task:Task, sat:Satellite, step:int,max_lat:int):
        start_time = sat.cur_time
        cur_time = start_time
        end_time = cur_time + datetime.timedelta(seconds=max_lat)
        while cur_time<end_time:
            if sat.get_can_see_target(task.observer,cur_time):
                return [True, (cur_time-start_time).total_seconds()]
            cur_time = cur_time + step
        return [False, float('inf')]
    
    def task_connection_lat_min(self, task:Task, sat:Satellite, step:int,max_lat:int):
        start_time = sat.cur_time
        cur_time = start_time
        end_time = cur_time + datetime.timedelta(seconds=max_lat)
        while cur_time<end_time:
            if sat.get_connectable(self.ground_stations,cur_time):
                return [True, (cur_time-start_time).total_seconds()]
            cur_time = cur_time + step
        return [False, float('inf')]
    
    # 判断当前的task最快的端到端时延
    def task_e2e_lat_min(self, task:Task, sat:Satellite, step:int,max_lat:int):
        start_time = sat.cur_time
        cur_time = start_time
        end_time = cur_time + datetime.timedelta(seconds=max_lat)
        can_connect1, connect_complete_time1 = self.task_connection_lat_min(task, sat, step,max_lat)
        if not can_connect1:
            return [False, float('inf')]
        
        cur_time = cur_time + datetime.timedelta(seconds=connect_complete_time1)
        can_sense, sense_complete_time = self.task_sensing_lat_min(task, sat, step, (end_time - cur_time).total_seconds())
        if not can_sense:
            return [False, float('inf')]

        cur_time = cur_time + datetime.timedelta(seconds=sense_complete_time)
        can_connect2, connect_complete_time2 = self.task_connection_lat_min(task, sat, step, (end_time - cur_time).total_seconds())
        if not can_connect2:
            return [False, float('inf')]
        
        return [True, datetime.timedelta(seconds=connect_complete_time1 + connect_complete_time2 + sense_complete_time)]

    def endless_random_task(self, satellites:list[Satellite]):
        for sat in satellites:
            if sat.visible and sat.can_accept_task():
                self.send_random_task(sat)

    def endless_attribute_task(self, satellites:list[Satellite],step_size:int):
        # for sat in satellites:
        #     if sat.visible and sat.can_accept_task():
        #         for t in self.tasks:
        #             if t.completed or t.on_sat:
        #                 continue
        #             if self.is_task_suitable_for_sat(t, sat, satellites, step_size, max_lat=60*60*24):
        #                 self.send_task(t,sat)
        for sat in satellites:
            if sat.visible and sat.can_accept_task():
                for t in self.tasks:
                    if not t.on_sat and not t.completed and t.sat==sat.name:
                        self.send_task(t,sat)

    def clear_satellite_tasks(self, satellites:list[Satellite]):
        for sat in satellites:
            for t in sat.tasks:
                self.from_sat_update_task(t)

    def step(self, satellites:list[Satellite], step_size: int):
        self.step_task_pool(task_size=100, sats=satellites, step=step_size,max_lat=60*60*24)
        # self.endless_random_task(satellites)
        self.endless_attribute_task(satellites, step_size)
        self.clear_satellite_tasks(satellites)

    def from_sat_update_task(self, task:Task):
        for index, t in enumerate(self.tasks):
            if t.id ==task.id:
                self.tasks[index] = task
            break
                
    def update_view(self,map):
        for gs in self.ground_stations:
            gs.update_view(map)
        for t in self.tasks:
            t.update_view(map)