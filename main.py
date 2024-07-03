from util import get_summary, plot_mempool_estimates, plot_forecaster_estimates, read_json_file

file_dir = "forcast_output.json"
data = read_json_file(file_dir, BitcoindThreshold=False, mode="economic_fee_rate")

# Plot forecaster estimates
# plot_forecaster_estimates(848920, 849120, data, forecaster="Block Forecast", logscale_yaxis=False)

plot_mempool_estimates(848920, 849120, data, logscale_yaxis=True)

# Get summary
get_summary(data, forecaster="Block Forecast")
