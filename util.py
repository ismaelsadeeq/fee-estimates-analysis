import matplotlib.pyplot as plt
import json

from datetime import datetime

def read_json_file(file_path):
    """
    Reads estimates data from a JSON file.

    Parameters:
    file_path (str): The path to the JSON file.

    Returns:
    list: A list of dictionaries containing estimates data.
    """
    try:
        with open(file_path, "r") as estimates_data:
            data = json.load(estimates_data)
            new_data = [
                {
                    "timestamp": entry["timestamp"],
                    "block_height": int(float(entry["block_height"])),
                    "forecaster": entry["forecaster"],
                    "low": int(float(entry["low"]) / 1000),
                    "high": int(float(entry["high"]) / 1000),
                    "conservative_fee_rate": int(float(entry["conservative_fee_rate"]) / 1000),
                    "economic_fee_rate": int(float(entry["economic_fee_rate"]) / 1000),
                    "p_5": int(float(entry["p_5"]) / 1000),
                    "p_50": int(float(entry["p_50"]) / 1000)
                }
                for entry in data if 'conservative_fee_rate' in entry and 'p_5' in entry
            ]
            return new_data
    except Exception as e:
        print(f"Failed to load estimates data from {file_path}: {e}")
        return []

def plot_data(forecaster, block_heights, conservative_estimates, economic_estimates, low_percentile, high_percentile, logscale_yaxis):
    """
    Plots estimates data.

    Parameters:
    block_heights (list): List of block heights.
    low_priority_estimates (list): List of low priority estimates.
    high_priority_estimates (list): List of high priority estimates.
    conservative_estimates (list): List of conservative fee estimates.
    economic_estimates (list): List of economic fee estimates.
    low_percentile (list): List of low percentile values.
    high_percentile (list): List of high percentile values.
    logscale_yaxis (bool): Flag to set y-axis to logarithmic scale.
    """
    plt.style.use('ggplot')
    fig, ax = plt.subplots(figsize=(15, 15))

    ax.fill_between(block_heights, low_percentile, high_percentile, alpha=.5, linewidth=0, color='grey', label='5th to 50th percentile target block fee rate')
    ax.plot(block_heights, economic_estimates, linewidth=2, color='green', label='Bitcoind Economic')
    ax.plot(block_heights, conservative_estimates, linewidth=2, color='red', label='Bitcoind Conservative')

    plt.title("Bitcoind conservative v economic estimate", loc="left", fontsize=12, fontstyle='italic')
    plt.suptitle("With confirmation target (1, 2)", y=0.92, fontsize=10, fontweight='bold')

    plt.xlabel("Block Height", fontsize=10, fontweight='bold')
    plt.ylabel("Fee Estimates", fontsize=10, fontweight='bold')
    plt.legend(loc='lower right', bbox_to_anchor=(1, 1))
    if logscale_yaxis:
        ax.set_yscale('log')
    plt.show()

def plot_estimates(start, end, data, forecaster, logscale_yaxis=False):
    """
    Plots fee estimates.

    Parameters:
    start (int): Starting block.
    end (int): Ending block.
    data (list): List of dictionaries containing estimates data.
    forecaster (str): The name of the forecaster.
    logscale_yaxis (bool): Flag to set y-axis to logarithmic scale.
    """
    if not data:
        print("Fee estimates data not provided")
        return

    MAX_THRESHOLD = 200
    if (end - start) > MAX_THRESHOLD:
        print(f"Blocks exceeded maximum threshold of {MAX_THRESHOLD} Blocks")
        return

    if start < 0 or end >= data[-1]["block_height"]:
        print("Invalid range")
        return

    filtered_data = [
        entry for entry in data
        if start <= entry["block_height"] <= end and entry["forecaster"] == forecaster
    ]
    block_heights = [entry["block_height"] for entry in filtered_data]
    conservative_estimates = [entry["conservative_fee_rate"] for entry in filtered_data]
    economic_estimates = [entry["economic_fee_rate"] for entry in filtered_data]
    low_percentile = [entry["p_5"] for entry in filtered_data]
    high_percentile = [entry["p_50"] for entry in filtered_data]

    plot_data(forecaster, block_heights, conservative_estimates, economic_estimates, low_percentile, high_percentile, logscale_yaxis)


def calculate_percentages(data, key):
    total = len(data)
    if total == 0:
        return [(0, 0), (0, 0), (0, 0)]
    underpaid = sum(1 for row in data if row[key] < row["p_5"])
    overpaid = sum(1 for row in data if row[key] > row["p_50"])
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

def get_summary(data, forecaster):
    total = len(data)
    if total == 0:
        return

    filtered_data = [
        entry for entry in data
        if entry["forecaster"] == forecaster
    ]
    start_time = datetime.fromisoformat(filtered_data[0]['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
    end_time = datetime.fromisoformat(filtered_data[-1]['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
    start_block = int(filtered_data[0]['block_height']) - 1
    end_block = int(filtered_data[-1]['block_height']) - 1

    print(f"Total of {total} estimates were made from {start_time} to {end_time} from Block {start_block} to Block {end_block}")
    print("---------------------------------------------------------")
    print("Bitcoind conservative estimate")
    print_summary(filtered_data, "conservative_fee_rate")

    print("---------------------------------------------------------")
    print("Bitcoind economic estimate")
    print_summary(filtered_data, "economic_fee_rate")

    
        
