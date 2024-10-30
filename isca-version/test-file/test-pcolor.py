import matplotlib
import numpy as np
import matplotlib.pyplot as plt
Z = np.random.rand(6, 10)

fig, ax = plt.subplots(1, 1)

c = ax.pcolor(Z)
ax.set_title('default: no edges')


fig.tight_layout()
plt.show()