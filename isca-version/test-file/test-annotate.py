
import matplotlib.pyplot as plt
import numpy as np

# 生成随机数据
np.random.seed(0)
x = np.random.rand(10)
y = np.random.rand(10)

# 生成随机的详细信息
info = [f"Point {i}: ({x[i]:.2f}, {y[i]:.2f})" for i in range(len(x))]

# 创建 scatter plot
fig, ax = plt.subplots()
sc = ax.scatter(x, y)

# 用于显示点击时显示的注释
annot = ax.annotate("", xy=(0,0), xytext=(20,20),
                    textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
annot.set_visible(False)

# 更新注释内容
def update_annot(ind):
    pos = sc.get_offsets()[ind["ind"][0]]
    annot.xy = pos
    text = "\n".join([info[n] for n in ind["ind"]])
    annot.set_text(text)
    annot.get_bbox_patch().set_alpha(0.4)

# 点击事件的回调函数
def on_click(event):
    # 如果点击位置在图形范围内
    if event.inaxes == ax:
        cont, ind = sc.contains(event)
        if cont:
            update_annot(ind)
            annot.set_visible(True)
            fig.canvas.draw_idle()
        else:
            annot.set_visible(False)
            fig.canvas.draw_idle()

# 连接点击事件
fig.canvas.mpl_connect("button_press_event", on_click)

plt.show()