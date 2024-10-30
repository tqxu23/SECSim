import ephem
import datetime
from ephem import degree
import numpy as np
from map import Map
from satellite import Satellite
from ground_station import GroundStation
from tle import get_sat_from_tle
import matplotlib.pyplot as plt
import random
from ground import Ground
import multiprocessing


start = datetime.datetime(2024, 10, 23, 14, 55, 18)

satellites: list[Satellite] = get_sat_from_tle(start,"tle.log")
g = Ground()

task_amount_trace:list[int] = []


def step(val):
    step_size = datetime.timedelta(minutes=1) 
    time = start + step_size * val    
    print(time)
    # time = start + datetime.timedelta(seconds=1) * val
    g.step(satellites, step_size)
    for sat in satellites:
        sat.step(time,g.ground_stations)
    task_amount_trace.append(len(g.tasks)-100)

for i in range(60*24*7+1):
    step(i+1)
k = 0


pcolor_matrix0 = np.empty((0,len(satellites[0].energy_system.date_trace)))
pcolor_matrix1 = np.empty((0,len(satellites[0].energy_system.date_trace)))
pcolor_matrix2 = np.empty((0,len(satellites[0].energy_system.date_trace)))
pcolor_matrix3 = np.empty((0,len(satellites[0].energy_system.date_trace)))
pcolor_matrix4 = np.empty((0,len(satellites[0].energy_system.date_trace)))
    
arr = np.empty((0, 4))  # 例如，每行有 4 个元素

for sat in satellites:
    energy_trace = sat.energy_system.energy_trace
    pcolor_matrix0 = np.vstack([pcolor_matrix0,energy_trace])
    solar_trace = np.array(sat.energy_system.eclipse_trace)
    solar_trace = ~solar_trace
    pcolor_matrix1 = np.vstack([pcolor_matrix1,solar_trace])

    # commu_trace = np.array(sat.communication_system.ison_trace)
    # pcolor_matrix2 = np.vstack([pcolor_matrix2,commu_trace])
  
    task_trace = np.array(sat.task_trace)
    pcolor_matrix2 = np.vstack([pcolor_matrix2,task_trace])

    visible_trace = np.array(sat.communication_system.visible_trace)
    pcolor_matrix3 = np.vstack([pcolor_matrix3,visible_trace])

    # axes[k].plot(date_list, energy_trace, linestyle='-', linewidth=1.0)
    # # axes[k].plot(date_list, energy_trace, label=f'Satellite {k + 1}', linestyle='-', linewidth=1.0)
    
    # # axes[k].set_title(f'Satellite {k + 1}')
    # # axes[k].set_xlabel('Date')
    # axes[k].set_ylabel('Energy/Eclipse Trace')
    # axes[k].legend()
    # axes[k].grid(True)
    # k+=1

task_complete_trace = np.array(task_amount_trace)
pcolor_matrix4 = np.vstack([pcolor_matrix4,task_complete_trace])

fig, [[ax0,ax1,ax2],[ax3,ax4,ax5]] = plt.subplots(2,3, figsize=(10,5))
x_interval = 60*8

def get_pcolor(ax, matrix, name):
    c = ax.pcolor(matrix)
    # print(len(satellites[0].energy_system.date_trace))
    ax.set_title(name)
    fig.colorbar(c, ax=ax)
    ax.set_xticks(range(len(satellites[0].energy_system.date_trace))[::x_interval], minor=False)
    ax.set_yticks(np.arange(matrix.shape[0]) + 0.5, minor=False)

    ax.set_xticklabels([date.strftime('%H:%M') for date in satellites[0].energy_system.date_trace][::x_interval])
    ax.set_yticklabels([f'Y{i}' for i in range(matrix.shape[0])])

get_pcolor(ax0,pcolor_matrix0,"Energy Trace")

get_pcolor(ax1,pcolor_matrix1,"Solar Trace")

get_pcolor(ax2,pcolor_matrix2,"Task Trace")

get_pcolor(ax3,pcolor_matrix3,"Visible Trace")

get_pcolor(ax4,pcolor_matrix4,"Task Amount Trace")

pcolor_matrix5 = None

# for sat in satellites:
#     print(f"Battery Trace for satellite {sat.name}")
#     t,time = sat.energy_system.battery_exp()
#     if not isinstance(pcolor_matrix5, np.ndarray):
#         pcolor_matrix5 = np.empty((0,len(time)))
#     battery_trace = np.array(t)
#     print(battery_trace)
#     pcolor_matrix5 = np.vstack([pcolor_matrix5,battery_trace])

# def get_bat_pcolor(ax, matrix, name,t):
#     c = ax.pcolor(matrix)
#     # print(len(satellites[0].energy_system.date_trace))
#     ax.set_title(name)
#     fig.colorbar(c, ax=ax)
#     ax.set_xticks(range(len(t))[::x_interval], minor=False)
#     ax.set_yticks(np.arange(matrix.shape[0]) + 0.5, minor=False)

#     ax.set_xticklabels(t[::x_interval])
#     ax.set_yticklabels([f'Y{i}' for i in range(matrix.shape[0])])

# get_bat_pcolor(ax5,pcolor_matrix5,"Battery Trace",t)

plt.tight_layout()
plt.show()