import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.basemap import Basemap
import matplotlib.widgets as widgets

# 生成一些随机数据
np.random.seed(0)
x = np.random.uniform(-180, 180, 100)
y = np.random.uniform(-90, 90, 100)

# 创建 Basemap 及绘图函数
fig, ax = plt.subplots()

def draw_map(intensity):
    ax.clear()
    m = Basemap(projection='cyl', resolution='c', ax=ax)
    m.drawcoastlines()
    m.drawcountries()
    m.drawmapboundary()
    
    # 转换坐标
    x_map, y_map = m(x, y)
    
    # 创建散点图
    color = plt.cm.viridis(intensity)
    scatter = ax.scatter(x_map, y_map, c=color, zorder=5)  # 设置 zorder 确保散点图在上层
    return scatter

# 初始绘制
scatter = draw_map(0.5)

# 创建滑块
color_slider = widgets.FloatSlider(
    value=0.5,
    min=0,
    max=1,
    step=0.01,
    description='Color Intensity:',
    continuous_update=True
)

# 更新 Basemap 和散点图颜色的函数
def update_map(change):
    intensity = color_slider.value
    draw_map(intensity)
    fig.canvas.draw_idle()

# 绑定滑块的变化事件
color_slider.observe(update_map, names='value')


# 显示图表
plt.show()