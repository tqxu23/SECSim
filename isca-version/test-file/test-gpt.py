import ephem
import datetime
from ephem import degree
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider

# 创建 Basemap 及绘图函数
fig, ax = plt.subplots()

def get_sun_position(date_time):
    observer_lat = 0
    observer_lon = 0
    observer = ephem.Observer()
    observer.date = date_time
    observer.lat = str(observer_lat)
    observer.lon = str(observer_lon)
    
    sun = ephem.Sun(observer)
    
    dec = sun.dec
    tau = observer.sidereal_time() - sun.ra
    
    dec_deg = dec * 180.0 / ephem.pi
    tau_deg = tau * 180.0 / ephem.pi

    return dec_deg, tau_deg

def get_sat_position(time):
    tle_rec.compute(time)
    sublong = float(tle_rec.sublong) / degree
    sublat = float(tle_rec.sublat) / degree
    return sublong, sublat, tle_rec.eclipsed

def update_map(date_time, ax):
    ax.clear()
    def terminator(dec, tau, nlons):
        dg2rad = np.pi / 180.
        lons = np.linspace(-180, 180, nlons)
        longitude = lons + tau
        lats = np.arctan(-np.cos(longitude * dg2rad) / np.tan(dec * dg2rad)) / dg2rad
        return lons, lats

    dec, tau = get_sun_position(date_time)
    nlons = 1441
    nlats = ((nlons - 1) / 2) + 1
    lons, lats = terminator(dec, tau, nlons)

    map = Basemap(projection='cyl', llcrnrlat=-90, urcrnrlat=90,
                  llcrnrlon=-180, urcrnrlon=180, resolution='c', ax=ax)
    x, y = map(lons, lats)
    map.plot(x, y, 'r', linewidth=2)
    map.drawcoastlines(color='gray')
    map.drawparallels(np.arange(-90, 90, 30), labels=[1, 0, 0, 0])
    map.drawmeridians(np.arange(-180, 180, 60), labels=[0, 0, 0, 1])

    lons2 = np.linspace(-180, 180, nlons)
    lats2 = np.linspace(-90, 90, int(nlats))
    lons2, lats2 = np.meshgrid(lons2, lats2)
    daynight = np.ones(lons2.shape)
    for nlon in range(nlons):
        daynight[:, nlon] = np.where(lats2[:, nlon] < lats[nlon], 0, daynight[:, nlon])
    x2, y2 = map(lons2, lats2)
    map.contourf(x2, y2, daynight, 1, colors=['w', '0.7'])
    return map

name = "CUTE-1.7+APD II (CO-65)"
line1 = "1 32785U 08021C   24296.87218741  .00011176  00000+0  91222-3 0  9991"
line2 = "2 32785  97.7753 261.4604 0007500 265.2874  94.7493 14.99573185894597"
tle_rec = ephem.readtle(name, line1, line2)
start = datetime.datetime(2024, 10, 23, 14, 55, 18)

m = update_map(start, ax)

sublong, sublat, eclipsed = get_sat_position(start)

ax.set_title(f'Time: {start.strftime("%Y-%m-%d %H:%M:%S")}')
sc = m.scatter([sublong], [sublat], latlon=True, cmap='Reds', alpha=0.7, zorder=5)
ax_slider = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor='lightgoldenrodyellow')
sfreq = Slider(ax_slider, 'Time', 0, 300, valinit=0)

sc.set_offsets(np.c_[[sublong], [sublat]])
if eclipsed:
    sc.set_color('blue')
else:
    sc.set_color('green')

def update(val):
    time = start + datetime.timedelta(minutes=1) * val
    ax.set_title(f'Time: {time.strftime("%Y-%m-%d %H:%M:%S")}')
    
    # 更新 Basemap 和晨昏线
    m = update_map(time, ax)
    
    # 更新卫星位置
    sublong, sublat, eclipsed = get_sat_position(time)
    sc = m.scatter([sublong], [sublat], latlon=True, cmap='Reds', alpha=0.7, zorder=5)
    
    if eclipsed:
        sc.set_color('blue')
    else:
        sc.set_color('green')

sfreq.on_changed(update)

plt.subplots_adjust(left=0.25, bottom=0.25)
plt.show()