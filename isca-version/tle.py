from satellite import Satellite
from satellite_communication import CommunicationSystem
from satellite_energy import EnergySystem
from satellite_sensor import SensorSystem
from satellite_inference import InferenceSystem

def get_sat_from_tle(time, file_name):
    satellites = []
    with open(file_name, 'r') as file:
        lines = file.readlines()
        i = 0
        for line in lines:
            if i%3==0:
                name = line.replace("\n","")
            elif i%3==1:
                assert line.startswith("1"), f"line{i} not start with \'1\'"
                line1 = line
            else:
                assert line.startswith("2"), f"line{i} not start with \'2\'"
                line2 = line
                energy = EnergySystem(start_time=time, solar_size= 0.03, bat_num= 3)
                comm = CommunicationSystem(start_time=time,power_cost= 10)
                infer = InferenceSystem(start_time=time,power_cost= 10)
                sensor = SensorSystem(start_time=time,power_cost= 10)
                sat = Satellite(name=name,start_time=time,line1=line1,line2=line2,energy_system=energy,communication_system=comm,inference_system=infer, sensor_system=sensor)
                satellites.append(sat)
            i = i + 1
    return satellites
