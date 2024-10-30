import ephem
import datetime
from ephem import degree
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider
from map import Map
from satellite import Satellite
from ground_station import GroundStation
from tle import get_sat_from_tle
from ground import Ground
# 创建 Basemap 及绘图函数
fig = plt.figure(figsize=(8, 6))
ax = fig.add_axes([0.05, 0.2, 0.5, 0.7])  # 设置 Basemap 占据的区域
start = datetime.datetime(2024, 10, 23, 14, 55, 18)

map = Map(ax,"cyl")
satellites = get_sat_from_tle(start, "tle.log")
# sat = Satellite()

m = map.update_view(start)
plt.subplots_adjust(right=0.50)
ax.set_title(f'Time: {start.strftime("%Y-%m-%d %H:%M:%S")}')
ax_slider = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor='lightgoldenrodyellow')
sfreq = Slider(ax_slider, 'Time', 0, 300, valinit=0)

ax_info = fig.add_axes([0.64, 0.2, 0.35, 0.7])  # 设置右边注释栏位置和大小


# ax_info = fig.add_axes([0.78, 0.1, 0.2, 0.8])：这行代码创建了注释栏，其中：
# 0.78：注释栏从图形的 78% 宽度处开始（从左向右）。
# 0.1：注释栏从图形的底部 10% 开始（从下向上）。
# 0.2：注释栏的宽度为图形宽度的 20%。
# 0.8：注释栏的高度为图形高度的 80%。

# ax_info.axis("off")  # 不显示坐标轴
ax_info.spines['top'].set_visible(False)    # 顶部外框线可见
ax_info.spines['right'].set_visible(False)  # 右侧外框线可见
ax_info.spines['bottom'].set_visible(False) # 底部外框线可见
ax_info.spines['left'].set_visible(True)   # 左侧外框线可见
ax_info.set_xticks([])
ax_info.set_yticks([])
text_box = ax_info.text(0, 1, "", verticalalignment="top", fontsize=12)

g = Ground()
g.tasks.append(g.generate_task())
g.tasks.append(g.generate_task())
g.tasks.append(g.generate_task())
g.tasks.append(g.generate_task())
g.tasks.append(g.generate_task())

g.tasks[1].completed = True
for sat in satellites:
    sat.update_view(start,m,g.ground_stations,ax,fig,text_box)

g.update_view(m)

def update(val):
    time = start + datetime.timedelta(minutes=1) * val
    ax.set_title(f'Time: {time.strftime("%Y-%m-%d %H:%M:%S")}')
    # 更新 Basemap 和晨昏线
    m = map.update_view(time)
    g.update_view(m)
    for sat in satellites:
        sat.update_view(time,m,g.ground_stations,ax,fig,text_box)

sfreq.on_changed(update)


plt.subplots_adjust(left=0.25, bottom=0.25)
plt.show()