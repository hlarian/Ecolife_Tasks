import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import fire
import utils

# Configuration for consistent plotting
plt.rcParams["font.family"] = "Time"
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        return data
    
def verify(
    window_size: int=20,
    interval: int=24*60,
):
    traces, trace_function_names, original_names = utils.read_selected_traces()
    sum_invoke = sum(
        int(traces[i][j]) != 0
        for j in range(window_size, window_size + interval)
        for i in range(len(traces))
    )

    # Read EcoLife results
    eco_carbon = read_json_file("./results/eco_life/carbon.json")
    eco_st = read_json_file("./results/eco_life/st.json")

    sum_carbon_eco, sum_st_eco = 0, 0
    for i in range(len(traces)):
        for _, value in eco_carbon[str(i)].items():
            sum_carbon_eco += value["carbon"]
        for _, value in eco_st[str(i)].items():
            sum_st_eco += value["st"]

    print(f"Eco-Life AVG Carbon: {sum_carbon_eco / sum_invoke}, AVG Service Time: {sum_st_eco / sum_invoke}")

    # Read Firefly results
    firefly_carbon = read_json_file("./results/firefly/carbon.json")
    firefly_st = read_json_file("./results/firefly/st.json")

    sum_carbon_firefly, sum_st_firefly = 0, 0
    for i in range(len(traces)):
        for _, value in firefly_carbon[str(i)].items():
            sum_carbon_firefly += value["carbon"]
        for _, value in firefly_st[str(i)].items():
            sum_st_firefly += value["st"]

    print(f"Firefly AVG Carbon: {sum_carbon_firefly / sum_invoke}, AVG Service Time: {sum_st_firefly / sum_invoke}")

    # Plotting setup
    fig, ax = plt.subplots(figsize=(6.5, 3))
    FONTSIZE = 13
    XLABEL = "CO$_2$ Footprint \n(% increase w.r.t. EcoLife)"
    YLABEL = "Service Time (% increase w.r.t. EcoLife)"

    # Calculating relative performance metrics
    min_st = min(sum_st_eco / sum_invoke, sum_st_firefly / sum_invoke)
    min_carbon = min(sum_carbon_eco / sum_invoke, sum_carbon_firefly / sum_invoke)

    eco_percent = [100 * ((sum_st_eco / sum_invoke) - min_st) / min_st, 100 * ((sum_carbon_eco / sum_invoke) - min_carbon) / min_carbon]
    firefly_percent = [100 * ((sum_st_firefly / sum_invoke) - min_st) / min_st, 100 * ((sum_carbon_firefly / sum_invoke) - min_carbon) / min_carbon]

    x = [eco_percent[1], firefly_percent[1]]
    y = [eco_percent[0], firefly_percent[0]]

    ax.set_xlabel(XLABEL, fontsize=FONTSIZE)
    ax.set_ylabel(YLABEL, fontsize=FONTSIZE)
    ax.tick_params(axis='both', labelsize=FONTSIZE)
    ax.grid(which='both', color='lightgrey', ls='dashed', zorder=0)
    colors = ['#17becf', '#ff7f0e']  # Custom colors for EcoLife and Firefly

    markers = ['o', 'X']
    LABELS = ['Eco-Life', 'Firefly']
    
    for i in range(len(x)):
        ax.scatter(x=x[i], y=y[i], color=colors[i], label=LABELS[i], s=200, zorder=3, alpha=1, edgecolors="black", marker=markers[i])

    ax.legend(loc="upper left", frameon=False, ncol=1, labels=LABELS, fontsize=13)
    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%i'))
    ax.set_ylim(0, max(y) + 10)
    ax.set_xlim(0, max(x) + 10)
    plt.savefig("firefly_vs_eco_life_result.pdf", bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    fire.Fire(verify)
