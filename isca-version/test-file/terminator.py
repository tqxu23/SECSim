import numpy as np
from mpl_toolkits.basemap import Basemap, _geoslib
import matplotlib.pyplot as plt

def terminator(dec,tau,nlons):
    # tau is "hour angle"
    # dec is "declination"
    dg2rad = np.pi/180.
    lons = np.linspace(-180,180,nlons)
    longitude = lons + tau
    lats = np.arctan(-np.cos(longitude*dg2rad)/np.tan(dec*dg2rad))/dg2rad
    return lons, lats

# these can be computed from Julian Day.
dec = 19.73
tau = 25.89

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
plt.title('Day/Night Terminator: Declination %4.2f, Hour Angle %4.2f' %
        (dec,tau))
plt.show()
