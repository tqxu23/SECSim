import ephem
import datetime
from ephem import degree
import numpy as np
from satellite_energy import EnergySystem
from satellite_communication import CommunicationSystem
from satellite_sensor import SensorSystem
from satellite_inference import InferenceSystem
import time
from task import Task
# https://celestrak.org/NORAD/elements/
class Satellite:
    
    static_power = 1

    def __init__(self, name = "CUTE-1.7+APD II (CO-65)", 
                 line1 = "1 32785U 08021C   24296.87218741  .00011176  00000+0  91222-3 0  9991",
                 line2 = "2 32785  97.7753 261.4604 0007500 265.2874  94.7493 14.99573185894597",
                 start_time = time.time(),
                 energy_system = EnergySystem(time.time(), 0.1, 10),
                 communication_system = CommunicationSystem(time.time(), 10),
                 inference_system = InferenceSystem(time.time(), 10),
                 sensor_system = SensorSystem(time.time(), 5)):
        # 静态信息
        self.cur_time = start_time
        self.name:str = name.strip()
        self.line1:str = line1.strip()
        self.line2:str = line2.strip()
        self.tle_rec = ephem.readtle(self.name, self.line1, self.line2)
        self.scatter_on_map = None
        self.visible:bool = False
        self.tasks: list[Task] = []

        # 前端显示用，是否textbox显示的是这个卫星
        self.on_text_box:bool = False

        # 动态信息
        self.energy_system = energy_system
        self.communication_system = communication_system
        self.inference_system = inference_system
        self.sensor_system = sensor_system


        # trace
        self.date_trace : list[float] = []
        self.task_trace : list[float] = []

    
    def get_connectable(self,ground_stations, time):
        self.visible = False
        for gs in ground_stations:
            gs.observer.date = time
            self.tle_rec.compute(gs.observer)
            altitude = self.tle_rec.alt * 180.0 / ephem.pi
            # print(altitude)
            if altitude > 0:
                # print(f"{time}: Satellite is visible with altitude {altitude:.2f} degrees")
                self.visible = True
                return True
            else:
                pass
    
    def get_can_see_target(self, task_observer:ephem.Observer, time):
        self.visible = False
        task_observer.date = time
        self.tle_rec.compute(task_observer)
        altitude = self.tle_rec.alt * 180.0 / ephem.pi
        # print(altitude)
        
        # https://www.sohu.com/a/385105492_120405555 高度角不能小于60°
        if altitude > 0:
            # print(f"{time}: Satellite is visible with altitude {altitude:.2f} degrees")
            return True
        else:
            return False

    def get_task_from_ground(self, task:Task):
        assert not task.completed, "Task completed!"
        assert not task.on_sat, "Task already on satellite!"
        task.on_sat = True
        self.tasks.append(task)
        
    def can_accept_task(self) -> bool:
        return True
        # return self.energy_system.energy / self.energy_system.storage >= 0.8
        # count = 0
        # for t in self.tasks:
        #     if not t.completed:
        #         count += 1
        # return count<=10

    def step_task_communication(self, cur_time):
        if self.energy_system.energy <= 0:
            return self.communication_system.step(False,cur_time,self.visible)
        step_size = (cur_time - self.cur_time).total_seconds()
        if self.visible:
            for t in self.tasks:
                if not t.completed and (t.sensor_left<=t.communication_left-t.communication_throughput*step_size) or (t.sensor_left==0 and t.communication_left!=0):
                    t.perform_communication(t.communication_throughput*step_size)
                    print(f"{self.name}: I am sending the info of Id{t.id}, SenseLeft:{t.sensor_left}, InferLeft:{t.inference_left}, CommuLeft: {t.communication_left}")
                    return self.communication_system.step(True,cur_time,self.visible)
        return self.communication_system.step(False,cur_time,self.visible)

    def step_task_inference(self, cur_time):
        if self.energy_system.energy < 0:
            return self.inference_system.step(False,cur_time)
        step_size = (cur_time - self.cur_time).total_seconds()
        for t in self.tasks:
            if (not t.completed):
                if t.inference_left > 0:
                    t.perform_inference(t.inference_throughput*step_size)
                    print(f"{self.name}: I am doing inference the info of Id{t.id}, SenseLeft:{t.sensor_left}, InferLeft:{t.inference_left}, CommuLeft: {t.communication_left}")
                    return self.inference_system.step(True,cur_time)
        return self.inference_system.step(False,cur_time)



    def step_task_sensing(self, cur_time):
        if self.energy_system.energy < 0:
            return self.sensor_system.step(False,cur_time)
        step_size = (cur_time - self.cur_time).total_seconds()
        for t in self.tasks:
            if (not t.completed) and self.get_can_see_target(t.observer,cur_time):
                if (t.sensor_left>0):
                    t.perform_sensing(t.sensing_throughput*step_size)
                    print(f"{self.name}: I can see the target from Id{t.id}, SenseLeft:{t.sensor_left}, InferLeft:{t.inference_left}, CommuLeft: {t.communication_left}")
                    return self.sensor_system.step(True,cur_time)
        return self.sensor_system.step(False,cur_time)


    def trace(self,date):
        self.date_trace.append(date)
        self.task_trace.append(len(self.tasks))

    # step时更新卫星的时序信息
    def step(self, cur_time, ground_stations):
        assert self.cur_time < cur_time, "Current time back in Energy System!"
        
        # step_size = (cur_time - self.cur_time).total_seconds()

        self.update(cur_time, ground_stations)
        eclipsed = self.tle_rec.eclipsed
        power = 0
        
        power += self.step_task_communication(cur_time)
        power += self.step_task_inference(cur_time)
        power += self.step_task_sensing(cur_time)
        power += self.static_power
        self.energy_system.step(eclipsed, power, cur_time)

        self.cur_time = cur_time

        self.trace(date=cur_time)

    # update时不调用任何前端，只更新卫星当前位置的静态信息
    def update(self, time, ground_stations):
        self.tle_rec.compute(time)
        self.get_connectable(ground_stations=ground_stations,time=time)


    def update_view(self, time, map, ground_stations,ax,fig,text_box):
        self.update(time, ground_stations)
        sublong = float(self.tle_rec.sublong) / degree
        sublat = float(self.tle_rec.sublat) / degree
        eclipsed = self.tle_rec.eclipsed
        if self.scatter_on_map==None:
            self.scatter_on_map = map.scatter([sublong], [sublat], latlon=True, cmap='Reds', alpha=0.7, zorder=5, marker='o')
            self.scatter_on_map.set_sizes([40])
            self.set_annotate_view(ax,fig,text_box)
        else:
            self.scatter_on_map.set_offsets(np.c_[[sublong],[sublat]])
        if eclipsed:
            self.scatter_on_map.set_color('blue')
        else:
            self.scatter_on_map.set_color('green')
        if self.visible:
            self.scatter_on_map.set_color('red')
        if self.on_text_box:
            self.update_annot_view(text_box)

    # def update_annot_view(self):
    #     pos = self.scatter_on_map.get_offsets()[self.ind["ind"][0]]
    #     self.annot.xy = pos
    #     text = f"Name:{self.name}\n"
    #     text += "Eclipsed " if self.tle_rec.eclipsed else ""
    #     text += "Visible " if self.visible else ""
    #     self.annot.set_text(text)
    #     self.annot.get_bbox_patch().set_alpha(0.4)


    def format_text(self,text):
        text = "  "+text
        return text.replace('\n', '\n  ')
    

    def update_annot_view(self,text_box):
        sublong = float(self.tle_rec.sublong) / degree
        sublat = float(self.tle_rec.sublat) / degree
        text = f"Name:{self.name}\n"
        text += f"Lon: {sublong:.2f}  "
        text += f"Lat: {sublat:.2f}\n"
        text += "Eclipsed " if self.tle_rec.eclipsed else ""
        text += "Visible " if self.visible else ""
        text = self.format_text(text)
        text_box.set_text(text)



    def set_annotate_view(self,ax,fig,text_box):

        # self.annot = ax.annotate("", xy=(0,0), xytext=(20,20),
        #                     textcoords="offset points",
        #                     bbox=dict(boxstyle="round", fc="w"),
        #                     arrowprops=dict(arrowstyle="->,head_length=0.6,head_width=0.4",connectionstyle="arc3,rad=-1"))
        # self.annot.set_visible(False)

        # 点击事件的回调函数
        def on_click(event):
            if event.inaxes == ax:
                cont, ind = self.scatter_on_map.contains(event)
                if cont:
                    self.update_annot_view(text_box)
                    self.scatter_on_map.set_sizes([160])
                    fig.canvas.draw_idle()
                    self.on_text_box = True
                else:
                    self.scatter_on_map.set_sizes([40])
                    self.on_text_box = False
        fig.canvas.mpl_connect("button_press_event", on_click)

            # if event.inaxes == ax:
            #     # 因为只有一个点，所以ind直接写死了
            #     cont, ind_no_need = self.scatter_on_map.contains(event)
            #     if cont:
            #         self.update_annot_view(text_box)
            #         self.annot.set_visible(True)
            #         fig.canvas.draw_idle()
            #     else:
            #         self.annot.set_visible(False)
            #         fig.canvas.draw_idle()
