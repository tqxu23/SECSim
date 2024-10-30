import ephem
from datetime import datetime

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

# 示例时间和观察者位置
date_time = datetime(2024, 10, 23, 12, 0, 0)  # 2024年10月23日12:00:00

dec, tau = get_sun_position(date_time)
print(f"Solar Declination (dec): {dec} degrees")
print(f"Hour Angle (tau): {tau} degrees")