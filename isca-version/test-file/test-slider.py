import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import numpy as np
from mpl_toolkits.basemap import Basemap

# 创建一个图形和轴
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.25, bottom=0.25)

# 创建Basemap对象
m = Basemap(projection='merc', llcrnrlat=-60, urcrnrlat=60,
            llcrnrlon=-180, urcrnrlon=180, resolution='c', ax=ax)

# 绘制地图
m.drawcoastlines()
m.drawcountries()
m.drawmapboundary()

# 创建初始的散点图
x = np.random.rand(10) * 360 - 180  # 经度范围 [-180, 180]
y = np.random.rand(10) * 120 - 60   # 纬度范围 [-60, 60]

# 将地理坐标转换为地图投影坐标
x_proj, y_proj = m(x, y)
sc = m.scatter(x_proj, y_proj, marker='o', color='r')

# 创建一个滑块的轴
ax_slider = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor='lightgoldenrodyellow')

# 创建滑块
sfreq = Slider(ax_slider, 'Time', 0, 300, valinit=0)

# 定义滑块的更新函数
def update(val):
    # 获取滑块的当前值
    time = sfreq.val
    
    # 根据滑块的值更新散点图的位置
    new_x = x + time * 0.01  # 这里简单地将 x 坐标随着时间线性增加
    new_y = y + time * 0.01  # 这里简单地将 y 坐标随着时间线性增加
    
    # 将新的地理坐标转换为地图投影坐标
    new_x_proj, new_y_proj = m(new_x, new_y)
    
    # 更新散点图的数据
    sc.set_offsets(np.c_[new_x_proj, new_y_proj])
    
    # 重新绘制图形
    fig.canvas.draw_idle()

# 将更新函数与滑块的事件绑定
sfreq.on_changed(update)

# 显示图形
plt.show()