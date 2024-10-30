import pybamm
import matplotlib.pyplot as plt
import os

model = pybamm.lithium_ion.SPM({"SEI": "ec reaction limited"})
parameter_values = pybamm.ParameterValues("Chen2020")
parameter_values.update({"SEI kinetic rate constant [m.s-1]": 1e-14})
N = 1
sat0 = ['Rest for 60.0 seconds']*60
cccv_experiment = pybamm.Experiment(
    [tuple(sat0)]
)
# cccv_experiment = pybamm.Experiment(
#     [
#         (
#             "Discharge at 1C for 5 minute",
#             "Hold at 4.2V for 1 hour",
#             "Charge at 1C for 5 minute",
#             # "Rest for 1 hour",
#         )
#     ]
#     * N
# )
# charge_experiment = pybamm.Experiment(
#     [
#         (
#             "Charge at 1C until 4.2V",
#             "Hold at 4.2V until C/50",
#         )
#     ]
# )
# rpt_experiment = pybamm.Experiment([("Discharge at C/3 until 3V",)])
sim = pybamm.Simulation(
    model, experiment=cccv_experiment, parameter_values=parameter_values
)
cccv_sol = sim.solve()
# sim = pybamm.Simulation(
#     model, experiment=charge_experiment, parameter_values=parameter_values
# )
# charge_sol = sim.solve(starting_solution=cccv_sol)
# sim = pybamm.Simulation(
#     model, experiment=rpt_experiment, parameter_values=parameter_values
# )
rpt_sol = sim.solve(starting_solution=cccv_sol)
t = rpt_sol["Total lithium capacity [A.h]"].entries
time = rpt_sol['Time [s]'].entries
print(t)
print(time)
# pybamm.plot_summary_variables(rpt_sol)


sat1 = ['Discharge at 8.00W for 60.0 seconds', 'Discharge at 21.00W for 60.0 seconds', 'Discharge at 21.00W for 60.0 seconds', 'Discharge at 21.00W for 60.0 seconds', 'Discharge at 21.00W for 60.0 seconds', 'Discharge at 11.00W for 60.0 seconds', 'Discharge at 21.00W for 60.0 seconds', 'Discharge at 21.00W for 60.0 seconds', 'Discharge at 21.00W for 60.0 seconds', 'Discharge at 21.00W for 60.0 seconds', 'Discharge at 21.00W for 60.0 seconds', 'Discharge at 21.00W for 60.0 seconds', 'Discharge at 21.00W for 60.0 seconds', 'Discharge at 21.00W for 60.0 seconds', 'Discharge at 11.00W for 60.0 seconds', 'Discharge at 11.00W for 60.0 seconds', 'Discharge at 21.00W for 60.0 seconds', 'Discharge at 11.00W for 60.0 seconds', 'Discharge at 21.00W for 60.0 seconds', 'Discharge at 21.00W for 60.0 seconds', 'Discharge at 11.00W for 60.0 seconds', 'Discharge at 21.00W for 60.0 seconds', 'Discharge at 11.00W for 60.0 seconds', 'Discharge at 11.00W for 60.0 seconds', 'Discharge at 11.00W for 60.0 seconds', 'Discharge at 11.00W for 60.0 seconds', 'Discharge at 11.00W for 60.0 seconds', 'Discharge at 11.00W for 60.0 seconds', 'Discharge at 0.27W for 60.0 seconds', 'Rest for 60.0 seconds', 'Rest for 60.0 seconds', 'Rest for 60.0 seconds', 'Rest for 60.0 seconds', 'Rest for 60.0 seconds', 'Charge at 2.00W for 60.0 seconds', 'Charge at 2.00W for 60.0 seconds', 'Charge at 2.00W for 60.0 seconds', 'Charge at 2.00W for 60.0 seconds', 'Charge at 2.00W for 60.0 seconds', 'Charge at 2.00W for 60.0 seconds', 'Charge at 2.00W for 60.0 seconds', 'Charge at 2.00W for 60.0 seconds', 'Charge at 2.00W for 60.0 seconds', 'Charge at 2.00W for 60.0 seconds', 'Charge at 2.00W for 60.0 seconds', 'Charge at 2.00W for 60.0 seconds', 'Charge at 2.00W for 60.0 seconds', 'Charge at 2.00W for 60.0 seconds', 'Charge at 2.00W for 60.0 seconds', 'Charge at 2.00W for 60.0 seconds', 'Charge at 2.00W for 60.0 seconds', 'Charge at 2.00W for 60.0 seconds', 'Charge at 2.00W for 60.0 seconds', 'Charge at 2.00W for 60.0 seconds', 'Charge at 2.00W for 60.0 seconds', 'Charge at 2.00W for 60.0 seconds', 'Charge at 2.00W for 60.0 seconds', 'Charge at 2.00W for 60.0 seconds', 'Charge at 2.00W for 60.0 seconds', 'Charge at 2.00W for 60.0 seconds', 'Charge at 2.00W for 60.0 seconds', "Charge at 1C until 4.2V" ]

model = pybamm.lithium_ion.SPM({"SEI": "ec reaction limited"})
parameter_values = pybamm.ParameterValues("Chen2020")
parameter_values.update({"SEI kinetic rate constant [m.s-1]": 1e-14})
cccv_experiment = pybamm.Experiment(
    [tuple(sat1)]
)
# cccv_experiment = pybamm.Experiment(
#     [
#         (
#             "Rest for 5 minute",
#             "Rest for 1 hour",
#             "Rest for 5 minute",
#             # "Rest for 1 hour",
#         )
#     ]
#     * N
# )
# charge_experiment = pybamm.Experiment(
#     [
#         (
#             "Charge at 1C until 4.2V",
#             "Hold at 4.2V until C/50",
#         )
#     ]
# )
# rpt_experiment = pybamm.Experiment([("Discharge at C/3 until 3V",)])
sim = pybamm.Simulation(
    model, experiment=cccv_experiment, parameter_values=parameter_values
)
cccv_sol = sim.solve()
# sim = pybamm.Simulation(
#     model, experiment=charge_experiment, parameter_values=parameter_values
# )
# charge_sol = sim.solve(starting_solution=cccv_sol)
# sim = pybamm.Simulation(
#     model, experiment=rpt_experiment, parameter_values=parameter_values
# )
rpt_sol = sim.solve(starting_solution=cccv_sol)
t = rpt_sol["Voltage [V]"].entries
time = rpt_sol['Time [s]'].entries
print(t)
# print(time)
# pybamm.plot_summary_variables(rpt_sol)