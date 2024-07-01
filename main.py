from util import get_summary, plot_estimates, read_json_file

file_dir = "forcast_output.json"
MempoolLast10Min = "Mempool Last 10 min Forecast"
Mempool = "Mempool Forecast"
LastBlock = "Last Block Forecast"
Last6Blocks = "Block Forecast"
Conservative = "conservative_fee_rate"
Economic = "economic_fee_rate"

data = read_json_file(file_dir, BitcoindThreshold=False, mode=Conservative)

plot_estimates(848920, 849120, data, forecaster=Last6Blocks, logscale_yaxis=True)

get_summary(data, forecaster=Last6Blocks)
