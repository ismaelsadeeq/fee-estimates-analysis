from util import get_summary, plot_estimates, read_json_file

file_dir = "forecast_output.json"
data = read_json_file(file_dir)

plot_estimates(845518, 845687, data, logscale_yaxis=True)
