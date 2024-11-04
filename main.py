import fire
import utils
import pandas as pd
from pathlib import Path
from optimizers import  perf_opt,carbon_opt,oracle,tech, ff_opt
import sys
#1*24*60
def main(
    region: str="US-CAL",
    start_hour: int=800,
    interval: int= 1*24*60,  
    mem_old: int = 512,
    mem_new: int = 512,
    app_list: list = None,
    server_pair: list = ['i3','m5zn'],
    kat_time:list = [i for i in range(0,31)],
    optimizer: str = 'ecolife',
    STlambda:float = 0.5,
    window_size: int = 20,
    pso_size: int = 15,
    ff_size: int = 15,
    ff_param: dict = {"alpha": 0.2, "beta": 1.0, "gamma": 1.0}
):
    if app_list is None:
        df = pd.read_csv(f"{Path(__file__).parents[0]}/function_mem.csv",header=None)
        app_list = df.iloc[:, 0].tolist()
        #print("App: " + str(app_list))
    # load carbon intensity data
    carbon_intensity, ci_max, ci_min,ci_avg = utils.load_carbon_intensity(region, start_hour, interval)
    #print("Carbon Intesity: " + str(carbon_intensity) + "Max Carbon Intesity: " + str(ci_max) + "Min Carbon Intesity: " + str(ci_min) + "Avg Carbon Intesity: " + str(ci_avg))
    #load trace:
    traces, trace_function_names,_ = utils.read_selected_traces()
    #
    # print("Traces: " + str(trace_function_names))
    for trace in traces:
        #print("Trace: " + str(len(trace)))
        assert len(trace) == len(carbon_intensity)
    function_mem_trace = [utils.read_func_mem_size(trace_function_names[i]) for i in range(len(traces))]
    #print("Function Memory for traces: " + str(function_mem_trace))
    sum=0

    for i in range(len(traces)):
        for j in range(len(traces[0])):
            if int(traces[i][j])!=0:
                sum+=int(traces[i][j])

        """Main optimization function with configuration display."""

    print("\n=== Optimization Configuration ===")
    print(f"Region           : {region}")
    print(f"Start Hour       : {start_hour}")
    print(f"Interval         : {interval} minutes")
    print(f"Memory (Old/New) : {mem_old} MB / {mem_new} MB")
    print(f"Application List : {app_list}")
    print(f"Server Pair      : {server_pair}")
    print(f"KAT Time Range   : {kat_time}")
    print(f"ST Lambda        : {STlambda}")
    print(f"Window Size      : {window_size}")
    
    print("\n=== Selected Optimizer: ", optimizer.upper(), "===")
    
    if optimizer == "ecolife":
        print("Optimizer Type   : Particle Swarm Optimization (PCO)")
        print(f"PSO Population Size : {pso_size}")
    elif optimizer == "firefly":
        print("Optimizer Type   : Firefly Algorithm")
        print(f"Firefly Population Size : {ff_size}")
        print("Firefly Parameters:")
        for param, value in ff_param.items():
            print(f"  - {param.capitalize()} : {value}")
    else:
        print("Optimizer Type   : Eco-life Optimization")

    print("======================================\n")

    if optimizer == "perf_opt":
        optimizer = perf_opt.perf_opt(traces,trace_function_names,server_pair,carbon_intensity,window_size,interval) 
        optimizer.optimize()
    elif optimizer == "carbon_opt":
        optimizer = carbon_opt.carbon_opt(traces,trace_function_names,server_pair,carbon_intensity,window_size,interval) 
        optimizer.optimize()
    elif optimizer == "oracle":
        optimizer = oracle.oracle(traces,trace_function_names,server_pair,carbon_intensity,ci_avg,STlambda, window_size,interval) 
        optimizer.optimize() 
    elif optimizer == "ecolife":
        optimizer = tech.tech(traces,trace_function_names,server_pair,kat_time,STlambda,carbon_intensity,window_size,mem_old,mem_new,ci_max,function_mem_trace,pso_size,region,interval)
        optimizer.optimize()
    elif optimizer == "firefly":
        optimizer = ff_opt.optimizer_FF(traces, trace_function_names, server_pair, kat_time, STlambda, carbon_intensity, window_size, mem_old, mem_new, ci_max, function_mem_trace, ff_size, ff_param, region, interval)
        optimizer.optimize()
    else: 
        sys.exit("input optimizer is not correct!")
   
if __name__ == "__main__":
    fire.Fire(main)
