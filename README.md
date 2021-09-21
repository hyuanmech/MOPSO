# MOPSO
A parallelized Multi-Objective Particle Swarm Optimization (MOPSO) framework for the design optimization of magnetic couplers used in EV wireless charging systems. The MOPSO algorithm is based on [Coello et al., IEEE TEVC, 2004].

This parallelized framework uses the multiprocessing package from the Python standard library to achieve parallel computation. Details of the multiprocessing package are available at https://docs.python.org/3/library/multiprocessing.html.

The framework is currently integrated with electromagnetic simulations for magnetic couplers using ANSYS Maxwell. The operations in ANSYS Maxwell are recorded by a Visual Basic script which is used as a text user interface (TUI) between the framework and ANSYS Maxwell. The geometric parameters are udpated during the optimization via the function 'vbs_cmd_output' in 'geo_parameters_update.py'.

The framework can be integrated with other CAE simulations, as long as a TUI is provided. The user will need to specify design parameters and objective functions in the provided functions. Note that the parallel computation in the framework might be limited by the license if the CAE simualtions are performed in commerical models.
