# ECOLIFE: Carbon-Aware Serverless Function Scheduling for Sustainable Computing 

## Table of Contents
- [About the Project](#about-the-project)
- [Setup](#setup)
- [Project Structure](#project-structure)
- [How to run](#how_to_run)
- [Tasks](#tasks)


## About the Project
EcoLife is an innovative scheduling framework that co-optimizes **carbon footprint** and **service time** in a serverless environment. This project leverages **multi-generation hardware** to make dynamic keep-alive and execution decisions using **Dynamic Particle Swarm Optimization (DPSO)** and **Firefly Algorithm (FA)**. Experimental results show that EcoLife effectively reduces carbon emissions while maintaining high execution performance.

## Setup
- **Language**: Python3.10
- **Hardware**: This repo is mainly simulation, you don't need any hardware to reproduce the results.
- **Libs**: Ensure that all the libs are installed.

## Project Structure:
```
Ecolife
│   .gitignore
│   exe_decide.py
│   firefly.py
│   main.py
│   plot.py
│   pso.py
│   README.md
│   requirements.txt
│   utils.py
│
├───carbon_intensity
│       US-CAL-CISO_2023_hourly.csv
│       ...
│
├───data
│   └───avg_data
│           bfs-1000k_c5.metal.json
│           ...
│
├───motivations
│       motiv1.pdf
│       ...
│
├───node
│   └───control_node
│           control.py
│
├───optimizers
│       carbon_opt.py
│       ff_opt.py
│       oracle.py
│       perf_opt.py
│       tech.py
│
├───results
│   ├───eco_life
│   │       carbon.json
│   │       st.json
│   └───firefly
│           carbon.json
│           st.json
│
└───selected_trace
        bfs-1000k_115.txt
        ...

```
### Key Files:

1. `main.py`: The main entry point for running the EcoLife simulation. It initializes parameters and executes the chosen optimizer (`PSO` or `Firefly`) based on user configuration.
2. `exe_decide.py`: The Execution Placement Decision Maker, responsible for deciding which server to execute functions on, balancing carbon emissions and service time.
3. `firefly.py`: Implements the Firefly Optimization algorithm. This algorithm adapts the standard Firefly Algorithm to optimize scheduling by balancing service time and carbon footprint in a serverless environment. Each firefly represents a scheduling configuration, and the algorithm adjusts positions based on brightness (fitness), where fitness measures carbon and service efficiency. 
4. `pso.py`: Contains the Dynamic Particle Swarm Optimization (DPSO) algorithm, used in the original EcoLife project for scheduling optimizations.
5. `utils.py`: Utility functions for data handling, reading configuration files, and computing necessary metrics.
6. `plot.py`: Generates visualizations comparing different optimization approaches based on the carbon and service time metrics.
7. `plot_ff_pso.py`: Dedicated plotting script to visualize the results of `PSO` and `Firefly` optimizers.

### Data Folders:

1. `carbon_intensity/`: Contains carbon intensity data for different regions, used to simulate environmental conditions affecting server emissions.
2. `data/avg_data/`: Profiled data for various functions, including energy and carbon costs associated with different serverless operations.
3. `selected_trace/`: Trace files representing invocation patterns for various functions, used to simulate realistic function execution patterns in serverless environments.

### Optimizers Folder

`optimizers/`: Contains optimizer-specific implementations, such as `ff_opt.py` for the Firefly algorithm and `tech.py` for DPSO. This folder also includes `carbon_opt.py` and `perf_opt.p`y for different optimization goals.

### Results Folder:

`results/`: Stores output from optimizations, with subfolders for each type (e.g., `ecolife`, `firefly`). Each folder contains JSON files with results data on carbon and service times for later analysis.


## How to Run:
1. **Extract Trace Files:** Begin by unzipping the `selected_trace.zip` file, which contains traces for simulation.
```bash
unzip selected_trace.zip
```
2. **Install Required Packages:** Make sure all necessary packages are installed by using `pip` with the provided `requirements.txt` file:

```bash
pip install -r requirements.txt
```
3. **Configuration Options:** Customize the simulation using the following configuration parameters:

- `region`: The region to use for carbon intensity data. Default is `"US-CAL"`.
- `start_hour`: Start hour for the simulation. Default is `800`.
- `interval`: Length of time (in minutes) for each simulation run. Default is `1*24*60` (one day).
- `mem_old`: Memory allocation for the older generation server. Default is `512` MB.
- `mem_new`: Memory allocation for the newer generation server. Default is `512` MB.
- `app_list`: List of applications to simulate. Default is None (all applications).
- `server_pair`: List defining the pair of server types used in the simulation. Default is `['i3', 'm5zn']`.
- `kat_time`: List defining keep-alive times in minutes. Default is `[i for i in range(0, 31)]`, representing times from 0 to 30 minutes.
- `optimizer`: The optimizer to use. Options include `"ecolife"` or `"firefly"`. Default is `'ecolife'`.
- `STlambda`: Lambda value to control the balance between service time and carbon footprint. Default is `0.5`.
- `window_size`: Size of the time window (in minutes) used for the sliding window approach. Default is `20`.
- `pso_size`: Population size for PSO. Default is `15`.
- `ff_size`: Population size for Firefly algorithm. Default is `15`.
- `ff_param`: Dictionary of parameters for Firefly algorithm, with "alpha", "beta", and "gamma" values. Default is `{"alpha": 0.2, "beta": 1.0, "gamma": 1.0}`.

4. Run the Main Script: Use the `main.py` script to initiate the simulation with desired configurations. You can specify settings like region, optimizer type, and interval duration, among others. Here’s an example of how to execute the code with custom configurations:
```bash
python3 main.py --region "US-CAL" --start_hour 800 --interval 1440 --mem_old 512 --mem_new 512 --server_pair '["i3","m5zn"]' --kat_time "[i for i in range(0,31)]" --optimizer "firefly" --STlambda 0.5 --window_size 20 --pso_size 15 --ff_size 15 --ff_param '{"alpha": 0.2, "beta": 1.0, "gamma": 1.0}'
```
Alternatively, you can modify the configuration options directly in `main.py` to suit your preferences.


## Tasks

This project involved substantial enhancements, specifically integrating the Firefly Algorithm (FA) into EcoLife for optimized serverless scheduling. Key contributions are as follows:
- **Firefly Algorithm Integration:** Developed and implemented the Firefly Algorithm as an alternative to Dynamic Particle Swarm Optimization (DPSO). This algorithm provides a novel approach to scheduling by co-optimizing service time and carbon footprint.
- **Dedicated Firefly Documentation:** Added a folder named firefly_document containing detailed documentation of the Firefly Algorithm's integration. This includes descriptions of the Firefly Algorithm, function explanations, optimization logic, and configuration instructions for users interested in utilizing or extending FA within EcoLife.
- **Comparison with DPSO:** Conducted a comprehensive comparison between the Firefly Algorithm and DPSO. This analysis includes metrics on carbon footprint and service time, illustrating the relative strengths and differences of each optimizer.
- **Enhanced Visualization:** Modified the plotting scripts (plot_ff_pso.py) to display the performance results of both DPSO and Firefly algorithms side-by-side, allowing for clear comparisons of average carbon footprint and service time.
- **Detailed Execution and Results Summary:** Enhanced the output of the main simulation to include an execution summary, providing detailed insights on overall performance, algorithm efficiency, and execution time.



