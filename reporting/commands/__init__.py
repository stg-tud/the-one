# literals shared in this module
core_commands = ["diff", "graph", "stats"]
graph_types_list = ["delay", "delivery", "stats"]

estimators = ["mean", "median"]

graph_contexts = ["paper", "notebook", "talk", "poster"]
graph_palettes = ["deep", "muted", "bright", "pastel", "dark", "colorblind"]
graph_styles = ["white", "dark", "whitegrid", "darkgrid", "ticks"]

tabular_output_format = {"csv": "csv", "json": "json", "latex": "tex", "pickle": "pkl"}

stat_options = {
    "all": "All stats",
    "sim_time": "Simulation Time",
    "created": "Created Messages",
    "started": "Started Messages",
    "relayed": "Relayed Messages",
    "aborted": "Aborted Messages",
    "dropped": "Dropped Messages",
    "removed": "Removed Messages",
    "delivered": "Delivered Messages",
    "delivery_prob": "Delivery Probability",
    "response_prob": "Response Probability",
    "overhead_ratio": "Overhead Ratio",
    "latency_avg": "Latency (Average)",
    "latency_med": "Latency (Median)",
    "hopcount_avg": "Hopcount (Average)",
    "hopcount_med": "Hopcount (Median)",
    "buffertime_avg": "Buffertime (Average)",
    "buffertime_med": "Buffertime (Median)",
    "rtt_avg": "RTT (Average)",
    "rtt_med": "RTT (Median)",
}
help_texts = {
    "context": "Seaborn context for the generated graphs",
    "describe": "Shows info on how many reports were considered and also the min and max values",
    "estimator": "Estimator to graph when comparing multiple groups",
    "filename_prefix": "Prefix to prepend to all output files",
    "group": "Report groups. Each group is a tuple of a glob pattern and a name for this group of reports. "
    "If more than one group is specified, reports matched by different patterns will be aggregated",
    "no_show": "Do not show output",
    "output_dir": "Output directory",
    "output_format": "Image format for outputs. Output will only be saved if this option is not left empty",
    "palette": "Seaborn color palette for the generated graphs",
    "reports_dir": "Report directory",
    "restore_defaults": "Restores the default values of all config data",
    "stat": "Name of the statistics value that should be parsed from the report files",
    "style": "Seaborn style for the generated graphs",
    "ymin0": "Flag to start the y-axis at 0 no matter what",
}

# imports at the end so we don't run into circular imports
from commands.config_command import config_group  # noqa: E402
from commands.diff_command import diff  # noqa: E402
from commands.graph_command import graph  # noqa: E402
from commands.interactive_command import interactive  # noqa: E402
from commands.stats_command import stats  # noqa: E402
