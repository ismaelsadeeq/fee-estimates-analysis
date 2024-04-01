import matplotlib.pyplot as plt
import json

from datetime import datetime

def read_json_file(file_path):
    """
    Reads mempool data from a JSON file.

    Parameters:
    file_path (str): The path to the JSON file.

    Returns:
    list: A list of dictionaries containing mempool data.
    """
    try:
        with open(file_path, "r") as estimates_data:
            data = json.load(estimates_data)
            # Convert relevant values to integers
            for entry in data:
                entry["block_height"] = int(float(entry["block_height"]))
                entry["mempool_fee_rate_estimate"] = int(float(entry["mempool_fee_rate_estimate"]) / 1000) # Convert from sat/kvB to sat/vB
                entry["block_fee_rate_estimate"] = int(float(entry["block_fee_rate_estimate"]) / 1000) # Convert from sat/kvB to sat/vB
                entry[".05"] = int(float(entry[".05"]))
                entry[".75"] = int(float(entry[".75"]))
            return data
    except Exception as e:
        print(f"Failed to load estimates data from {file_path}: {e}")
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
    
    if start < 0 or end >= data[-1]["block_height"]:
        print("Invalid range")
        return

    block_heights = []
    mempool_estimates = [] 
    blockpolicy_estimates = []
    low_percentile = [] 
    high_percentile = []

    for entry in data:
        blk_height = entry["block_height"]
        if start <= blk_height <= end:
            block_heights.append(blk_height)
            mempool_estimates.append(entry["mempool_fee_rate_estimate"])
            blockpolicy_estimates.append(entry["block_fee_rate_estimate"])
            low_percentile.append(entry[".05"])
            high_percentile.append(entry[".75"])

    plot_data(block_heights, mempool_estimates, blockpolicy_estimates, low_percentile, high_percentile)

def calculate_percentages(data, key):
    total = len(data)
    if total == 0:
        return [(0, 0), (0, 0), (0, 0)]
    underpaid = sum(1 for row in data if row[key] < row[".05"])
    overpaid = sum(1 for row in data if row[key] > row[".75"])
    within_range = total - underpaid - overpaid
    arr = []
    arr.append((overpaid, (overpaid / total * 100)))
    arr.append((underpaid, (underpaid / total * 100)))
    arr.append((within_range, (within_range / total * 100)))
    return arr

def print_summary(data, key):
    arr = calculate_percentages(data, key)
    for category, (count, percentage) in zip(["overpaid", "underpaid", "are within the range"], arr):
        print(f"{count} estimates {category} {percentage:.2f}% of the total estimates ")

def get_summary(data):
    total = len(data)
    if total == 0:
        return
    
    start_time = datetime.fromisoformat(data[0]['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
    end_time = datetime.fromisoformat(data[-1]['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
    start_block = data[0]['prev_block_height']
    end_block = data[-1]['prev_block_height']

    print(f"Total of {total} estimates were made from {start_time} to {end_time} from Block {start_block} to Block {end_block}")
    print("---------------------------------------------------------")
    print("CBlockPolicyEstimator estimatesmartfee economic mode with confirmation target 1")
    print_summary(data, "block_fee_rate_estimate")
    print("---------------------------------------------------------")
    print("Mempool estimate for next block")
    print_summary(data, "mempool_fee_rate_estimate")

    
        
