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
    fig, ax = plt.subplots(figsize=(15, 15))

    ax.fill_between(block_heights, low_percentile, high_percentile, alpha=.5, linewidth=0, color='grey')
    ax.plot(block_heights, blockpolicy_estimates, linewidth=2, color='yellow', label='Block Policy Estimates')
    ax.plot(block_heights, mempool_estimates, linewidth=2, color='blue', label='Mempool Estimates')

    plt.title("Mempool fee estimate vs estimatesmartfee against the block 5th percentile to 75th percentile fee rate", loc="left", fontsize=12, fontstyle='italic')
    plt.suptitle("With confirmation target 1", y=0.92, fontsize=10, fontweight='bold')

    plt.xlabel("Block Height", fontsize=10, fontweight='bold')
    plt.ylabel("Fee Estimates", fontsize=10, fontweight='bold')
    plt.legend()
    plt.show()

def plot_estimates(start, end, data):
    """
    Plots fee estimates.

    Parameters:
    start (int): Starting block.
    end (int): Ending block.
    data (list): List of dictionaries containing mempool data.
    """
    MAX_THRESHOLD = 200
    if (end - start) > MAX_THRESHOLD:
        print(f"Blocks exceeded maximum threshold of {MAX_THRESHOLD} Blocks")
        return
    
    if start < 0 or end >= int(float(data[len(data) -1]["block_height"])):
        print("Invalid range")
        return

    block_heights = []
    mempool_estimates = [] 
    blockpolicy_estimates = []
    low_percentile = [] 
    high_percentile = []

    i = 0
    while(i < len(data) and end >= int(float(data[i]["block_height"]))):
        blk_height = int(float(data[i]["block_height"]))
        if start >= blk_height:
            block_heights.append(int(float(data[i]["block_height"])))
            mempool_estimates.append(int(float(data[i]["mempool_fee_rate_estimate"]) / 1000))
            blockpolicy_estimates.append(int(float(data[i]["block_fee_rate_estimate"]) / 1000))
            low_percentile.append(int(float(data[i][".05"])))
            high_percentile.append(int(float(data[i][".75"])))
            start+=1
        i+=1

    plot_data(block_heights, mempool_estimates, blockpolicy_estimates, low_percentile, high_percentile)

