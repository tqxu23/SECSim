import ephem
import datetime
from ephem import degree
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider

def get_sat_position(time,tle_rec):
    tle_rec.compute(time)
    sublong = float(tle_rec.sublong) / degree
    sublat = float(tle_rec.sublat) / degree
    return sublong, sublat, tle_rec.eclipsed

class Map:

    def __init__(self, ax, cate="cyl"):
        self.terminator_area = None
        self.terminator_line = None
        if cate=='cyl':
            self.basemap = Basemap(projection='cyl', llcrnrlat=-90, urcrnrlat=90,
                    llcrnrlon=-180, urcrnrlon=180, resolution='c',ax=ax)
        elif cate=='mill':
            self.basemap = Basemap(projection='ortho',lon_0=-105,lat_0=40,ax=ax)
        else:
            self.basemap = Basemap(projection='cyl', llcrnrlat=-90, urcrnrlat=90,
                    llcrnrlon=-180, urcrnrlon=180, resolution='c',ax=ax)
        coastlines = self.basemap.drawcoastlines(color='gray')
        paralleles = self.basemap.drawparallels(np.arange(-90, 90, 30), labels=[1, 0, 0, 0])
        meridians = self.basemap.drawmeridians(np.arange(-180, 180, 60), labels=[0, 0, 0, 1])

    @staticmethod
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


    def update_view_daylight(self, date_time):
        if self.terminator_area!=None:
             for collection in self.terminator_area.collections:
                collection.remove()
        if self.terminator_line!=None:
             self.terminator_line[0].remove()

        def terminator(dec, tau, nlons):
                    dg2rad = np.pi / 180.
                    lons = np.linspace(-180, 180, nlons)
                    longitude = lons + tau
                    lats = np.arctan(-np.cos(longitude * dg2rad) / np.tan(dec * dg2rad)) / dg2rad
                    return lons, lats
        map = self.basemap
        dec, tau = Map.get_sun_position(date_time)
        nlons = 1441
        nlats = ((nlons - 1) / 2) + 1
        lons, lats = terminator(dec, tau, nlons)

        x, y = map(lons, lats)

        lons2 = np.linspace(-180, 180, nlons)
        lats2 = np.linspace(-90, 90, int(nlats))
        lons2, lats2 = np.meshgrid(lons2, lats2)
        daynight = np.ones(lons2.shape)
        for nlon in range(nlons):
            daynight[:, nlon] = np.where(lats2[:, nlon] < lats[nlon], 0, daynight[:, nlon])
        x2, y2 = map(lons2, lats2)
        self.terminator_line = map.plot(x, y, 'gray', linewidth=2)
        self.terminator_area = map.contourf(x2, y2, daynight, 1, colors=['w', '0.7'])


    def update_view(self, date_time):
        map = self.basemap
        self.update_view_daylight(date_time)
        return map

