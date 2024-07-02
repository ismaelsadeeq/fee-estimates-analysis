from util import get_summary, plot_mempool_estimates, plot_forecaster_estimates, read_json_file

file_dir = "forcast_output.json"
data = read_json_file(file_dir, BitcoindThreshold=False, mode="conservative_fee_rate")

# Compare two estimates estimates
plot_mempool_estimates(848920, 849120, data, logscale_yaxis=True)

# Plot forecaster estimates
plot_forecaster_estimates(848920, 849120, data, forecaster="Block Forecast", logscale_yaxis=True)

# Get summary
get_summary(data, forecaster="Block Forecast")
