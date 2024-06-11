from util import get_summary, plot_estimates, read_json_file

file_dir = "forcast_output.json"
MempoolLast10Min = "Mempool Last 10 min Forecast"
Mempool = "Mempool Forecast"
LastBlock = "Last Block Forecast"
Last6Blocks = "Block Forecast"

data = read_json_file(file_dir, BitcoindThreshold=False)

plot_estimates(846887, 847087, data, forecaster=Mempool, logscale_yaxis=True)

get_summary(data, forecaster=Mempool)
