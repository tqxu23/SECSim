import ephem
import datetime
from ephem import degree
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider
from map import Map


# https://celestrak.org/NORAD/elements/
class GroundStation:

    # def __init__(self, name = "GS_test", lon = '-111:32.1',lat = '35:05.8',elevation=0):
    #     self.name = name
    #     self.lon = lon
    #     self.lat = lat
    #     self.elevation = elevation
    #     self.observer = ephem.Observer()
    #     self.observer.lon = lon
    #     self.observer.lat = lat
    #     self.observer.elevation = elevation
    #     self.scatter_on_map = None
    
    
    def __init__(self, name = "Boston", observer = ephem.city('Boston')):
            self.observer = observer
            self.name = name
            self.scatter_on_map = None

        
    def get_position(self):
        return self.observer.lon / degree, self.observer.lat / degree

    def update_view(self, map):
        sublong, sublat = self.get_position()
        if self.scatter_on_map==None:
            self.scatter_on_map = map.scatter([sublong], [sublat], latlon=True, alpha=0.7, zorder=5, marker='*',s=100, c='red')
        else:
            self.scatter_on_map.set_offsets(np.c_[[sublong],[sublat]])
        # if eclipsed:
        #     self.scatter_on_map.set_color('blue')
        # else:
        #     self.scatter_on_map.set_color('green')
