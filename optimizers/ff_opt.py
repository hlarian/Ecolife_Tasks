from pathlib import Path
import sys
sys.path.append("..")
import utils
import exe_decide
import firefly  # Import the Firefly algorithm
import json
import time
from tqdm import tqdm

class optimizer_FF:
    def __init__(self,
                 traces: list,
                 trace_function_names: list,
                 server_pair: list,
                 kat_time: list,
                 st_lambda: float,
                 carbon_intensity: list,
                 window_size: int,
                 mem_old_limit: int,
                 mem_new_limit: int,
                 ci_avg: float,
                 function_mem_trace: list,
                 ff_size: int,
                 ff_param: dict,
                 region: str,
                 interval: int) -> None:
        self.traces = traces
        self.trace_function_names = trace_function_names
        self.server_pair = server_pair
        self.kat_time = [int(x) for x in kat_time]
        self.st_lambda = st_lambda
        self.carbon_lambda = 1 - self.st_lambda
        self.carbon_intensity = carbon_intensity
        self.window_size = window_size
        self.mem_old_limit = mem_old_limit
        self.mem_new_limit = mem_new_limit
        self.ci_avg = ci_avg
        self.function_mem_trace = function_mem_trace
        self.ff_size = ff_size
        self.ff_param = ff_param
        self.region = region
        self.interval = interval

    def optimize(self):
        # Start timing the entire optimization process
        total_start_time = time.time()

        time_length = len(self.traces[0])
        function_num = len(self.traces)
        invoke_interval = [[] for _ in range(function_num)]
        old_warm_pool = {}
        new_warm_pool = {}

        new_function = {}
        sum_st = 0
        sum_carbon = 0
        discard_list = []
        result_st = [{} for _ in range(function_num)]
        result_carbon = [{} for _ in range(function_num)]
        sum1 = 0
        for j in range(self.window_size, self.window_size + self.interval):
            print(f"Begin time: {j}")
            old_decision = {}
            new_decision = {}
            start = time.time()
            sum_discard = 0
            sum_per_function = 0
            with tqdm(total=function_num, desc="Algorithm Progress", bar_format="{l_bar}{bar} [Elapsed: {elapsed} | Remaining: {remaining}]") as pbar:
                for i in range(function_num):
                    window_invoc = self.traces[i][j - self.window_size:j]
                    invoc_index = [k for k, num in enumerate(window_invoc) if int(num) != 0]
                    interval = [invoc_index[k + 1] - invoc_index[k] for k in range(len(invoc_index) - 1)]
                    invoke_interval[i].append(interval)

                    function_name = self.trace_function_names[i]
                    old_cold_st, old_warm_st = utils.get_st(function_name, self.server_pair[0])
                    new_cold_st, new_warm_st = utils.get_st(function_name, self.server_pair[1])
                    cold_carbon, warm_carbon = utils.compute_exe(function_name, self.server_pair, self.carbon_intensity[j])
                    old_cold_carbon = cold_carbon[0]
                    new_cold_carbon = cold_carbon[1]
                    old_warm_carbon = warm_carbon[0]
                    new_warm_carbon = warm_carbon[1]

                    concurrent_function = int(self.traces[i][j])

                    if concurrent_function == 0:
                        # Check expiration of functions in warm pool
                        self.check_warm_pool_expiry(i, old_warm_pool, new_warm_pool, result_carbon, function_name, j)
                    else:
                        sum_per_function += concurrent_function
                        sum1 += concurrent_function

                        # Execute function
                        st_per_func, carbon_per_func, result_st[i], result_carbon[i] = exe_decide.exe_loc_decision(
                            old_warm_pool,
                            new_warm_pool,
                            i,
                            concurrent_function,
                            old_cold_st,
                            new_cold_st,
                            old_cold_carbon,
                            new_cold_carbon,
                            old_warm_st,
                            new_warm_st,
                            old_warm_carbon,
                            new_warm_carbon,
                            self.st_lambda,
                            function_name,
                            self.server_pair,
                            self.carbon_intensity,
                            j,
                            result_st[i],
                            result_carbon[i]
                        )
                        assert st_per_func > 0
                        assert carbon_per_func > 0
                        sum_st += st_per_func
                        sum_carbon += carbon_per_func

                        # Initialize Firefly optimizer
                        if i not in new_function:
                            parameters = {
                            'population_size': self.ff_size,
                            'kat_times': self.kat_time,
                            'lambda': self.st_lambda,
                            'alpha': self.ff_param['alpha'],
                            'beta': self.ff_param['beta'],
                            'gamma': self.ff_param['gamma']
                            }
                            new_function[i] = firefly.Firefly(parameters, self.server_pair, function_name, self.ci_avg)
                            best_solution = new_function[i].main(self.carbon_intensity[j], invoke_interval[i][j - self.window_size])
                            decision = best_solution
                        else:
                            best_solution = new_function[i].main(self.carbon_intensity[j], invoke_interval[i][j - self.window_size])
                            decision = best_solution

                        # Apply decision
                        self.apply_decision(decision, i, j, old_decision, new_decision)
                        
                    # Update the progress bar
                    pbar.update(1)

            # Check memory and adjust pools
            sum_discard, sum_carbon = self.check_memory_and_adjust(sum_discard, old_decision, new_decision, result_carbon, sum_carbon, invoke_interval, j, new_warm_pool, old_warm_pool)

            print(f"Finish time: {j}")
            discard_list.append(sum_discard)
            print(f"Current service time is: {sum_st / sum1}, carbon is: {sum_carbon / sum1}")
            

        # Calculate the total execution time
        total_execution_time = time.time() - total_start_time

        self.save_results(result_carbon, result_st)

        # Final summary of results
        avg_service_time = sum_st / sum1 if sum1 > 0 else 0
        avg_carbon_footprint = sum_carbon / sum1 if sum1 > 0 else 0
        print("\n=== Final Optimization Results ===")
        print(f"Total Functions Invoked: {sum1}")
        print(f"Average Service Time per Function: {avg_service_time}")
        print(f"Average Carbon Footprint per Function: {avg_carbon_footprint}")
        #print(f"Total Discarded Functions: {total_discarded}")
        #print(f"Memory Adjustments: {len(discard_list)}")
        print(f"Total Execution Time: {total_execution_time:.2f} seconds")    
        print(f"\n=== Firefly Optimization Completed Successfully ===")

    def check_warm_pool_expiry(self, i, old_warm_pool, new_warm_pool, result_carbon, function_name, j):
        if i in old_warm_pool and int(old_warm_pool[i]["end_time"]) <= j:
            last = int(old_warm_pool[i]["end_time"]) - int(old_warm_pool[i]["start_time"])
            kat_carbon = int(old_warm_pool[i]['num']) * utils.compute_kat(function_name, self.server_pair[0], last, self.carbon_intensity[int(old_warm_pool[i]["start_time"])])
            result_carbon[i][int(old_warm_pool[i]["invoke_time"])]["carbon"] += kat_carbon
            del old_warm_pool[i]
        if i in new_warm_pool and new_warm_pool[i]["end_time"] <= j:
            last = int(new_warm_pool[i]["end_time"] - new_warm_pool[i]["start_time"])
            kat_carbon = int(new_warm_pool[i]['num']) * utils.compute_kat(function_name, self.server_pair[1], last, self.carbon_intensity[new_warm_pool[i]["start_time"]])
            result_carbon[i][int(new_warm_pool[i]["invoke_time"])]["carbon"] += kat_carbon
            del new_warm_pool[i]

    def apply_decision(self, decision, i, j, old_decision, new_decision):
        ka_loc, ka_last = int(decision[0]), int(decision[1])
        if ka_loc == 0 and ka_last != 0:
            going_ka = {"num": int(self.traces[i][j]), "start_time": j, "end_time": int(j + ka_last), "invoke_time": int(j)}
            old_decision[i] = going_ka
        elif ka_loc == 1 and ka_last != 0:
            going_ka = {"num": int(self.traces[i][j]), "start_time": j, "end_time": int(j + ka_last), "invoke_time": int(j)}
            new_decision[i] = going_ka

    def check_memory_and_adjust(self, sum_discard, old_decision, new_decision, result_carbon, sum_carbon, invoke_interval, j, new_warm_pool, old_warm_pool):
        mem_checker = utils.mem_check(self.mem_new_limit, self.mem_old_limit, old_decision, new_decision, self.function_mem_trace, new_warm_pool, old_warm_pool)
        return sum_discard, sum_carbon

    def save_results(self, result_carbon, result_st):
        with open(f"{Path(__file__).parents[1]}/results/firefly/carbon.json", "w") as file:
            json.dump(result_carbon, file, indent=4)
        with open(f"{Path(__file__).parents[1]}/results/firefly/st.json", "w") as file:
            json.dump(result_st, file, indent=4)
