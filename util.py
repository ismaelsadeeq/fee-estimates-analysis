import matplotlib.pyplot as plt
import numpy as np
import json
import sys

def read_json_file(file_path):
    """
    Reads mempool data from a JSON file.

    Parameters:
    file_path (str): The path to the JSON file.

    Returns:
    list: A list of dictionaries containing mempool data.
    """
    try:
        with open(file_path, "r") as mempool_data:
            return json.load(mempool_data)
    except Exception as e:
        print(f"Failed to load mempool txs from {file_path}: {e}")
        return []

def plot_data(block_heights, mempool_estimates, blockpolicy_estimates, low_percentile, high_percentile):
    """
    Plots mempool data.

    Parameters:
    block_heights (list): List of block heights.
    mempool_estimates (list): List of mempool fee rate estimates.
    blockpolicy_estimates (list): List of estimatesmartfee fee rate estimates.
    low_percentile (list): List of low percentile values.
    high_percentile (list): List of high percentile values.
    """
    plt.style.use('ggplot')
    fig, ax = plt.subplots()

    ax.fill_between(block_heights, low_percentile, high_percentile, alpha=.5, linewidth=0, color='grey')
    ax.plot(block_heights, blockpolicy_estimates, linewidth=2, color='yellow', label='Block Policy Estimates')
    ax.plot(block_heights, mempool_estimates, linewidth=2, color='blue', label='Mempool Estimates')

    plt.title("Mempool fee estimate vs estimatesmartfee vs Actual block median fee", loc="left", fontsize=12, fontstyle='italic')
    plt.suptitle("All with confirmation target 1", y=0.92, fontsize=10, fontweight='bold')

    plt.xlabel("Block Height", fontsize=10, fontweight='bold')
    plt.ylabel("Fee Estimates", fontsize=10, fontweight='bold')
    plt.legend()
    plt.show()

def plot_estimates(start=0, end=1500, data=None):
    """
    Plots fee estimates.

    Parameters:
    start (int): Starting index.
    end (int): Ending index.
    data (list): List of dictionaries containing mempool data.
    """
    MAX_THRESHOLD = 2000
    if (end - start) > MAX_THRESHOLD:
        print(f"Data point exceeded maximum threshold of {MAX_THRESHOLD}")
        return
    
    if start < 0 or end >= len(data):
        print("Invalid range")
        return

    block_heights = []
    mempool_estimates = [] 
    blockpolicy_estimates = []
    low_percentile = [] 
    high_percentile = []

    while(start < end):
        block_heights.append(int(float(data[start]["block_height"])))
        mempool_estimates.append(int(float(data[start]["mempool_fee_rate_estimate"]) / 1000))
        blockpolicy_estimates.append(int(float(data[start]["block_fee_rate_estimate"]) / 1000))
        low_percentile.append(int(float(data[start][".05"])))
        high_percentile.append(int(float(data[start][".75"])))
        start +=1

    plot_data(block_heights, mempool_estimates, blockpolicy_estimates, low_percentile, high_percentile)

