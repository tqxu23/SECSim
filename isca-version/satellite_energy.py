import time
import pybamm
import numpy as np
class EnergySystem:
  
    def __init__(self, start_time, solar_size = 1, bat_num = 10):

        # solar size 单位为平方米
        # energy storage 单位为Wh
        # step size 单位为s

        self.vol_per_bat = 5*0.8
        self.solar_size = solar_size
        self.bat_num = bat_num
        self.storage = bat_num*self.vol_per_bat
        self.energy = self.storage
        self.cur_time = start_time


        # 电池仿真部分

        self.model = pybamm.lithium_ion.SPM({"SEI": "ec reaction limited"})
        # Parameters for an LG M50 cell, from the paper Chen et al.[9] and references therein.
        self.parameter_values = pybamm.ParameterValues("Chen2020")
        # self.parameter_values.update({"SEI kinetic rate constant [m.s-1]": 1e-14})
        # print(self.parameter_values)
        # print(self.model.variable_names())
        # assert False
        # self.parameter_values.update({"SEI kinetic rate constant [m.s-1]": 1e-14})
        # add anode potential as a variable
        # we use the potential at the separator interface since that is the minimum potential
        # during charging (plating is most likely to occur first at the separator interface)
        # self.model.variables["Anode potential [V]"] = self.model.variables[
        #     "Negative electrode surface potential difference at separator interface [V]"
        # ]
        # self.parameter_values = pybamm.ParameterValues("Chen2020")
        self.solver = pybamm.CasadiSolver(mode="fast")
        self.exp_expr:list[str] = []
        self.sim = None

        # trace
        self.date_trace : list[float] = []
        self.eclipse_trace : list[float] = []
        self.energy_trace : list[float] = []
    
    def trace(self,date, eclipsed, energy):
        self.date_trace.append(date)
        self.eclipse_trace.append(eclipsed)
        self.energy_trace.append(energy)

    def step(self, eclipesd, power_cost, cur_time):
        assert self.cur_time < cur_time, "Current time back in Energy System!"
        step_size = (cur_time - self.cur_time).total_seconds()
        self.cur_time = cur_time        
        cur_power = 0
        if not eclipesd:
            cur_power += self.solar_size * 100
            self.energy += 100 * self.solar_size * step_size / 60 / 60
        cur_power -= power_cost
        self.energy -= power_cost * step_size / 60 / 60
        if self.energy < 0:
            cur_power = cur_power - self.energy / step_size * 60 * 60
            self.energy = 0
        if self.energy > self.storage:
            cur_power = cur_power - self.energy / step_size * 60 * 60 + self.storage / step_size * 60 * 60
            self.energy = self.storage
        self.energy = self.energy
        self.battery_step(cur_power, step_size)

        self.trace(date=cur_time, eclipsed= eclipesd, energy= self.energy)
    
    def battery_step(self, cur_power,step_size):
        cur_power = cur_power / self.bat_num
        direction = "Charge"
        target_power = cur_power
        if cur_power<0:
            direction = "Discharge"
            target_power = -cur_power
        if cur_power<0.01 and cur_power> -0.01:
            self.exp_expr.append(f"Rest for {step_size} seconds")
        else:
            self.exp_expr.append(f"{direction} at {target_power:.2f}W for {step_size} seconds")

    def battery_exp(self):
        print(self.exp_expr)
        step = pybamm.Experiment([tuple(self.exp_expr)])
        self.sim = pybamm.Simulation(
            self.model, experiment=step, parameter_values=self.parameter_values
        ).solve(solver=self.solver)
        # pybamm.plot_summary_variables(self.sim)

        # t = self.sim["Discharge capacity [A.h]"].entries
        # t = self.sim["Power [W]"].entries
        # https://docs.pybamm.org/en/v23.5_a/source/examples/notebooks/getting_started/tutorial-3-basic-plotting.html
        t = self.sim["Total lithium capacity [A.h]"].entries
        time = self.sim['Time [s]'].entries
        return t,time
        # self.sim.plot()



        # C_volume = 1.5
        # direction = "Charge"
        # target_power = cur_power
        # if cur_power<0:
        #     direction = "Discharge"
        #     target_power = -cur_power
        # def custom_step_power(variables):
        #     # target_power = 4
        #     voltage = variables["Voltage [V]"]
        #     return target_power / voltage
        # step = pybamm.Experiment([
        #     (
        #         f"{direction} at {target_power}W for {step_size} seconds"
        #     )
        # ])
        # if self.sim==None:
        #     self.sim = pybamm.Simulation(
        #         self.model, experiment=step, parameter_values=self.parameter_values
        #     ).solve(solver=self.solver)
        # else:
        #     self.sim = pybamm.Simulation(
        #         self.model, experiment=step, parameter_values=self.parameter_values
        #     ).solve(solver=self.solver,starting_solution=self.sim)


        # direction = "Charge"
        # target_power = cur_power
        # if cur_power<0:
        #     direction = "Discharge"
        #     target_power = -cur_power
        # def custom_step_power(variables):
        #     # target_power = 4
        #     voltage = variables["Voltage [V]"]
        #     return target_power / voltage
        # step = pybamm.step.CustomStepExplicit(
        #     custom_step_power, direction=direction, duration=step_size
        # )
        # if self.sim==None:
        #     self.sim = pybamm.Simulation(
        #         self.model, experiment=step, parameter_values=self.parameter_values
        #     ).solve(solver=self.solver)
        # else:
        #     self.sim = pybamm.Simulation(
        #         self.model, experiment=step, parameter_values=self.parameter_values
        #     ).solve(solver=self.solver,starting_solution=self.sim)