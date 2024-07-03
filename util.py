import matplotlib.pyplot as plt
import json
from datetime import datetime

MempoolLast10Min = "Mempool Last 10 min Forecast"
Mempool = "Mempool Forecast"
LastBlock = "Last Block Forecast"
Last6Blocks = "Block Forecast"
Conservative = "conservative_fee_rate"
Economic = "economic_fee_rate"

def sats_per_kb_to_sats_per_byte(sats_per_kb):
    """
    Converts satoshis per kilobyte to satoshis per byte.

    Parameters:
    sats_per_kb (float): Fee rate in satoshis per kilobyte.

    Returns:
    int: Fee rate in satoshis per byte.
    """
    return int(float(sats_per_kb) / 1000)


def read_json_file(file_path, BitcoindThreshold=False, mode=Conservative):
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
                    "low": sats_per_kb_to_sats_per_byte(entry["low"]),
                    "high": sats_per_kb_to_sats_per_byte(entry["high"]),
                    "conservative_fee_rate": sats_per_kb_to_sats_per_byte(entry["conservative_fee_rate"]),
                    "economic_fee_rate": sats_per_kb_to_sats_per_byte(entry["economic_fee_rate"]),
                    "p_5": sats_per_kb_to_sats_per_byte(entry["p_5"]),
                    "p_50": sats_per_kb_to_sats_per_byte(entry["p_50"])
                }
                for entry in data if 'conservative_fee_rate' in entry and 'p_5' in entry
            ]
            if BitcoindThreshold:
                for d in new_data:
                    for key in ["high", "low"]:
                        if d[key] > d[mode]:
                            d[key] = d[mode]
            return new_data
    except Exception as e:
        print(f"Failed to load estimates data from {file_path}: {e}")
        return []

def plot_data(block_heights, estimates_dict, low_percentile, high_percentile, logscale_yaxis, labels, colors):
    """
    Plots estimates data.

    Parameters:
    block_heights (list): List of block heights.
    estimates_dict (dict): Dictionary containing lists of different estimates.
    low_percentile (list): List of low percentile values.
    high_percentile (list): List of high percentile values.
    logscale_yaxis (bool): Flag to set y-axis to logarithmic scale.
    labels (dict): Dictionary containing labels for the plot.
    """
    plt.style.use('ggplot')
    fig, ax = plt.subplots(figsize=(15, 15))
    
    for key, values in estimates_dict.items():
        ax.plot(block_heights, values, linewidth=2, alpha=0.6, color=colors[key], label=labels[key])

    ax.fill_between(block_heights, low_percentile, high_percentile, alpha=1, linewidth=0, color='grey', label='5th to 50th percentile')

    plt.title("Estimators against the block 5th percentile to 50th percentile fee rate", loc="left", fontsize=12, fontstyle='italic')
    plt.suptitle("With confirmation target 1", y=0.92, fontsize=10, fontweight='bold')

    plt.xlabel("Block Height", fontsize=10, fontweight='bold')
    plt.ylabel("Fee Estimates", fontsize=10, fontweight='bold')
    plt.legend(loc='lower right', bbox_to_anchor=(1, 1))
    if logscale_yaxis:
        ax.set_yscale('log')
    plt.show()

def validate_data_range(start, end, data):
    """
    Validates the data range for plotting.

    Parameters:
    start (int): Starting block.
    end (int): Ending block.
    data (list): List of dictionaries containing estimates data.

    Returns:
    bool: True if the range is valid, False otherwise.
    """
    if not data:
        print("Fee estimates data not provided")
        return False

    MAX_THRESHOLD = 200
    if (end - start) > MAX_THRESHOLD:
        print(f"Blocks exceeded maximum threshold of {MAX_THRESHOLD} Blocks")
        return False

    if start < 0 or end >= data[-1]["block_height"]:
        print("Invalid range")
        return False

    return True

def plot_mempool_estimates(start, end, data, logscale_yaxis=False):
    """
    Plots mempool fee estimates.

    Parameters:
    start (int): Starting block.
    end (int): Ending block.
    data (list): List of dictionaries containing estimates data.
    logscale_yaxis (bool): Flag to set y-axis to logarithmic scale.
    """
    if not validate_data_range(start, end, data):
        return

    filtered_data = [entry for entry in data if start <= entry["block_height"] <= end and entry["forecaster"] in {Mempool, MempoolLast10Min}]
    
    if not filtered_data:
        print("No data found for the given range and forecaster criteria")
        return

    block_heights = [entry["block_height"] for entry in filtered_data if entry["forecaster"] == MempoolLast10Min]
    mempool_high_estimates = [entry["high"] for entry in filtered_data if entry["forecaster"] == Mempool]
    mempool_last_10_low_estimates = [entry["low"] for entry in filtered_data if entry["forecaster"] == MempoolLast10Min]
    low_percentile = [entry["p_5"] for entry in filtered_data if entry["forecaster"] == MempoolLast10Min]
    high_percentile = [entry["p_50"] for entry in filtered_data if entry["forecaster"] == MempoolLast10Min]

    if len(mempool_high_estimates) != len(mempool_last_10_low_estimates):
        print("Mismatch in the lengths of mempool high and last 10 min low estimates")
        return

    estimates_dict = {
        "mempool_high": mempool_high_estimates,
        "mempool_last_10_low": mempool_last_10_low_estimates
    }
    labels = {
        "mempool_high": "Mempool High priority",
        "mempool_last_10_low": "Mempool Last 10 Min Low priority"
    }

    colors = {
        "mempool_high": "yellow",
        "mempool_last_10_low": "blue"
    }
    plot_data(block_heights, estimates_dict, low_percentile, high_percentile, logscale_yaxis, labels, colors)

def plot_forecaster_estimates(start, end, data, forecaster, logscale_yaxis=False):
    """
    Plots forecaster fee estimates.

    Parameters:
    start (int): Starting block.
    end (int): Ending block.
    data (list): List of dictionaries containing estimates data.
    forecaster (str): The name of the forecaster.
    logscale_yaxis (bool): Flag to set y-axis to logarithmic scale.
    """
    if not validate_data_range(start, end, data):
        return

    filtered_data = [entry for entry in data if start <= entry["block_height"] <= end and entry["forecaster"] == forecaster]
    
    if not filtered_data:
        print(f"No data found for forecaster {forecaster}")
        return

    block_heights = [entry["block_height"] for entry in filtered_data]
    low_priority_estimates = [entry["low"] for entry in filtered_data]
    high_priority_estimates = [entry["high"] for entry in filtered_data]
    conservative_estimates = [entry["conservative_fee_rate"] for entry in filtered_data]
    economic_estimates = [entry["economic_fee_rate"] for entry in filtered_data]
    low_percentile = [entry["p_5"] for entry in filtered_data]
    high_percentile = [entry["p_50"] for entry in filtered_data]

    estimates_dict = {
        "high_priority": high_priority_estimates,
        "low_priority": low_priority_estimates,
        "conservative": conservative_estimates,
        "economic": economic_estimates
    }

    labels = {
        "high_priority": f"{forecaster} High Priority",
        "low_priority": f"{forecaster} Low Priority",
        "conservative": "Bitcoind Conservative",
        "economic": "Bitcoind Economic"
    }

    colors = {
        "high_priority": "yellow",
        "low_priority": "blue",
        "conservative": "green",
        "economic": "red"
    }    

    plot_data(block_heights, estimates_dict, low_percentile, high_percentile, logscale_yaxis, labels, colors)

def calculate_percentages(data, key):
    total = len(data)
    if total == 0:
        return [(0, 0), (0, 0), (0, 0)]
    underpaid = sum(1 for row in data if row[key] < row["p_5"])
    overpaid = sum(1 for row in data if row[key] > row["p_50"])
    within_range = total - underpaid - overpaid
    return [
        (overpaid, (overpaid / total * 100)),
        (underpaid, (underpaid / total * 100)),
        (within_range, (within_range / total * 100))
    ]

def print_summary(data, key):
    arr = calculate_percentages(data, key)
    for category, (count, percentage) in zip(["overpaid", "underpaid", "are within the range"], arr):
        print(f"{count} estimates {category} {percentage:.2f}% of the total estimates ")

def get_summary(data, forecaster):
    filtered_data = [entry for entry in data if entry["forecaster"] == forecaster]
    
    if not filtered_data:
        print(f"No data found for forecaster {forecaster}")
        return

    total = len(filtered_data)
    start_time = datetime.fromisoformat(filtered_data[0]['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
    end_time = datetime.fromisoformat(filtered_data[-1]['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
    start_block = filtered_data[0]['block_height'] - 1
    end_block = filtered_data[-1]['block_height'] - 1

    print(f"Total of {total} estimates were made from {start_time} to {end_time} from Block {start_block} to Block {end_block}")
    print("---------------------------------------------------------")
    print("Low priority estimates")
    print_summary(filtered_data, "low")

    print("---------------------------------------------------------")
    print("High priority estimates")
    print_summary(filtered_data, "high")

    print("---------------------------------------------------------")
    print("Bitcoind conservative estimates")
    print_summary(filtered_data, "conservative_fee_rate")

    print("---------------------------------------------------------")
    print("Bitcoind economic estimates")
    print_summary(filtered_data, "economic_fee_rate")
