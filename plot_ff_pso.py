import json
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import fire
import utils

# Configuration for consistent plotting
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
plt.rcParams["font.family"] = "Times New Roman"  # Set to "Gill Sans" for consistency

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        return data

def verify(
    window_size: int = 20,
    interval: int = 24 * 60,
):
    traces, trace_function_names, original_names = utils.read_selected_traces()
    
    # Calculate the total number of invocations in the interval
    sum_invoke = sum(
        int(traces[i][j]) != 0
        for j in range(window_size, window_size + interval)
        for i in range(len(traces))
    )

    # Read and calculate metrics for Eco-Life
    eco_carbon = read_json_file("./results/eco_life/carbon.json")
    eco_st = read_json_file("./results/eco_life/st.json")

    sum_carbon_eco, sum_st_eco = 0, 0
    for i in range(len(traces)):
        for _, value in eco_carbon[i].items():  # Assumes JSON data as list of dicts
            sum_carbon_eco += value["carbon"]
        for _, value in eco_st[i].items():
            sum_st_eco += value["st"]

    avg_carbon_eco = sum_carbon_eco / sum_invoke
    avg_st_eco = sum_st_eco / sum_invoke
    print(f"Eco-Life AVG Carbon: {avg_carbon_eco}, AVG Service Time: {avg_st_eco}")

    # Read and calculate metrics for Firefly
    firefly_carbon = read_json_file("./results/firefly/carbon.json")
    firefly_st = read_json_file("./results/firefly/st.json")

    sum_carbon_firefly, sum_st_firefly = 0, 0
    for i in range(len(traces)):
        for _, value in firefly_carbon[i].items():
            sum_carbon_firefly += value["carbon"]
        for _, value in firefly_st[i].items():
            sum_st_firefly += value["st"]

    avg_carbon_firefly = sum_carbon_firefly / sum_invoke
    avg_st_firefly = sum_st_firefly / sum_invoke
    print(f"Firefly AVG Carbon: {avg_carbon_firefly}, AVG Service Time: {avg_st_firefly}")

    # Set up the plot with actual values
    fig, ax = plt.subplots(figsize=(6.5, 3))
    FONTSIZE = 13
    XLABEL = "CO$_2$ Footprint (Average)"
    YLABEL = "Service Time (Average)"

    # Use actual average values for x and y coordinates
    x = [avg_carbon_eco, avg_carbon_firefly]
    y = [avg_st_eco, avg_st_firefly]
    LABELS = ['Eco-Life', 'Firefly']
    colors = ['#17becf', '#ff7f0e']  # Custom colors for Eco-Life and Firefly
    markers = ['o', 'X']

    # Plot settings
    ax.set_xlabel(XLABEL, fontsize=FONTSIZE)
    ax.set_ylabel(YLABEL, fontsize=FONTSIZE)
    ax.tick_params(axis='both', labelsize=FONTSIZE)
    ax.grid(which='both', color='lightgrey', ls='dashed', zorder=0)
    
    # Scatter plot and annotation for each algorithm
    for i in range(len(x)):
        ax.scatter(x=x[i], y=y[i], color=colors[i], label=LABELS[i], s=200, zorder=3, alpha=1, edgecolors="black", marker=markers[i])
        # Annotate with exact values beside each point
        ax.text(x[i] + 0.001, y[i] + 1, f"({x[i]:.4f}, {y[i]:.2f})", fontsize=FONTSIZE, verticalalignment='bottom')

    # Legend and formatting
    ax.legend(loc="upper left", frameon=False, fontsize=13)
    ax.set_ylim(0, max(y) + 10)  # Add padding to y-axis
    ax.set_xlim(0, max(x) + 0.01)  # Add padding to x-axis
    plt.tight_layout()
    plt.savefig("firefly_vs_eco_life_avg_comparison.pdf", bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    fire.Fire(verify)
