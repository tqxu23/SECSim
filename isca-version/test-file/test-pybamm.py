import pybamm
import matplotlib.pyplot as plt
import os

model = pybamm.lithium_ion.SPM({"SEI": "ec reaction limited"})
parameter_values = pybamm.ParameterValues("Chen2020")
parameter_values.update({"SEI kinetic rate constant [m.s-1]": 1e-14})
N = 100
cccv_experiment = pybamm.Experiment(
    [
        (
            "Charge at 1C until 4.2V",
            "Hold at 4.2V until C/50",
            "Discharge at 1C until 3V",
            "Rest for 1 hour",
        )
    ]
    * N
)
charge_experiment = pybamm.Experiment(
    [
        (
            "Charge at 1C until 4.2V",
            "Hold at 4.2V until C/50",
        )
    ]
)
rpt_experiment = pybamm.Experiment([("Discharge at C/3 until 3V",)])
sim = pybamm.Simulation(
    model, experiment=cccv_experiment, parameter_values=parameter_values
)
cccv_sol = sim.solve()
sim = pybamm.Simulation(
    model, experiment=charge_experiment, parameter_values=parameter_values
)
charge_sol = sim.solve(starting_solution=cccv_sol)
sim = pybamm.Simulation(
    model, experiment=rpt_experiment, parameter_values=parameter_values
)
rpt_sol = sim.solve(starting_solution=charge_sol)
pybamm.dynamic_plot(rpt_sol.cycles[-1], ["Current [A]", "Voltage [V]"])
pybamm.plot_summary_variables(rpt_sol)