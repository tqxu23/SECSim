import ephem
import datetime
from ephem import degree
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import datetime
import numpy as np
from matplotlib.widgets import Slider, Button, RadioButtons


## [...]
# https://celestrak.org/NORAD/elements/

name = "STARLINK-32389          "
line1 = "1 61549C 24184T   24297.41923611 -.01092600  00000+0 -37235-2 0  2977"
line2 = "2 61549  53.1617 198.4553 0000978  99.9337 344.7070 15.90166460    13"

# name = "STARLINK-3004"
# line1 = "1 48880U 21059B   24297.33000598  .00008598  00000+0  67285-3 0  9997"
# line2 = "2 48880  97.6591  59.8295 0001725  84.1770 275.9651 15.01278815183428"
# name = "CUTE-1.7+APD II (CO-65)"
# line1 = "1 32785U 08021C   24296.87218741  .00011176  00000+0  91222-3 0  9991"
# line2 = "2 32785  97.7753 261.4604 0007500 265.2874  94.7493 14.99573185894597"
tle_rec = ephem.readtle(name, line1, line2)
start = datetime.datetime(2024, 10, 23, 14, 55, 18)

date = []

def get_sun_position(date_time):
    # 创建观察者对象
    observer_lat = 0
    observer_lon = 0
    observer = ephem.Observer()
    observer.date = date_time
    observer.lat = str(observer_lat)
    observer.lon = str(observer_lon)
    
    # 创建太阳对象
    sun = ephem.Sun(observer)
    
    # 获取太阳的赤纬（单位：弧度）
    dec = sun.dec
    
    # 获取太阳的时角（单位：弧度）
    tau = observer.sidereal_time() - sun.ra
    
    # 转换为度数
    dec_deg = dec * 180.0 / ephem.pi
    tau_deg = tau * 180.0 / ephem.pi
    

    return dec_deg, tau_deg

def get_sat_position(time):
    tle_rec.compute(time)
    print(float(tle_rec.sublong), float(tle_rec.sublat))
    sublong = float(tle_rec.sublong)/degree
    sublat = float(tle_rec.sublat)/degree
    return sublong, sublat, tle_rec.eclipsed
def get_map(date_time):
    def terminator(dec,tau,nlons):
        # tau is "hour angle"
        # dec is "declination"
        dg2rad = np.pi/180.
        lons = np.linspace(-180,180,nlons)
        longitude = lons + tau
        lats = np.arctan(-np.cos(longitude*dg2rad)/np.tan(dec*dg2rad))/dg2rad
        return lons, lats


    dec,tau = get_sun_position(date_time)

    # # these can be computed from Julian Day.
    # dec = 19.73
    # tau = 25.89

    # compute lons and lats of day/night terminator.
    nlons = 1441; nlats = ((nlons-1)/2)+1
    lons, lats = terminator(dec,tau,nlons)

    # setup map projection
    # map = Basemap(projection='mill',lon_0=0)
    map = Basemap(projection='cyl', llcrnrlat=-90, urcrnrlat=90,
                llcrnrlon=-180, urcrnrlon=180, resolution='c')
    # map = Basemap(projection='ortho',lon_0=-105,lat_0=40)
    # compute day/night terminator in projection coords
    x,y = map(lons, lats)
    # plot terminator as red line
    map.plot(x,y,'r',linewidth=2)
    # plot coastlines, draw label meridians and parallels.
    map.drawcoastlines(color='gray')
    # map.drawmapboundary(fill_color='white') 
    # map.fillcontinents(color='gray',lake_color='white')
    map.drawparallels(np.arange(-90,90,30),labels=[1,0,0,0])
    map.drawmeridians(np.arange(-180,180,60),labels=[0,0,0,1])
    # create grid of day=1, night=0
    lons2 = np.linspace(-180,180,nlons)
    lats2 = np.linspace(-90,90,int(nlats))
    lons2, lats2 = np.meshgrid(lons2,lats2)
    daynight = np.ones(lons2.shape)
    for nlon in range(nlons):
        daynight[:,nlon] = np.where(lats2[:,nlon]<lats[nlon],0,daynight[:,nlon])
    x2, y2 = map(lons2,lats2)
    # contour this grid with 1 contour level, specifying colors.
    map.contourf(x2,y2,daynight,1,colors=['w','0.7'])
    return map


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

# setup Lambert Conformal basemap.
# m = Basemap(projection='cyl', llcrnrlat=-90, urcrnrlat=90,
#             llcrnrlon=-180, urcrnrlon=180, resolution='c')
# m.drawmapboundary(fill_color='white') 
# m.fillcontinents(color='gray',lake_color='white')
fig, ax = plt.subplots()
m = update_map(start,ax)

sublong,sublat,eclipsed = get_sat_position(start)


ax.set_title(f'Time: {start.strftime("%Y-%m-%d %H:%M:%S")}')
sc = m.scatter([sublong], [sublat], latlon=True,cmap='Reds', alpha=0.7, zorder=5)
ax_slider = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor='lightgoldenrodyellow')
sfreq = Slider(ax_slider, 'Time', 0, 300, valinit=0)
# m = Basemap(projection='ortho',lon_0=-105,lat_0=40)
sc.set_offsets(np.c_[[sublong], [sublat]])
if eclipsed:
    sc.set_color('green')
else:
    sc.set_color('blue')


# 定义滑块的更新函数
def update(val):
    time = start + datetime.timedelta(minutes=1) * val
    ax.set_title(f'Time: {time.strftime("%Y-%m-%d %H:%M:%S")}')
    
    # 更新 Basemap 和晨昏线
    update_map(time, ax)
    
    # 更新卫星位置
    sublong, sublat, eclipsed = get_sat_position(time)
    sc.set_offsets(np.c_[[sublong], [sublat]])
    
    if eclipsed:
        sc.set_color('green')
    else:
        sc.set_color('blue')
    fig.canvas.draw_idle()


# 将更新函数与滑块的事件绑定
sfreq.on_changed(update)


# def update(val):
#     d = start + datetime.timedelta(minutes=1)*sfreq.val
#     tle_rec.compute(d)
#     print(float(tle_rec.sublong), float(tle_rec.sublat))
#     sublong = float(tle_rec.sublong)/degree
#     sublat = float(tle_rec.sublat)/degree
#     sc.set_offsets(np.c_[sublong, sublat])
#     plt.canvas.draw_idle()
# sfreq.on_changed(update)


plt.subplots_adjust(left=0.25, bottom=0.25)

plt.show()