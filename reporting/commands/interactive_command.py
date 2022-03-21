import click
import config
import questionary
from matplotlib import pyplot as plt

from commands import (
    core_commands,
    graph_contexts,
    graph_styles,
    graph_palettes,
    graph_types_list,
    estimators,
    stat_options,
    tabular_output_format,
)
from commands.diff_command import diff
from commands.stats_command import stats
from commands.graph_subcommands.graph_delay import graph_delay
from commands.graph_subcommands.graph_delivery import graph_delivery
from commands.graph_subcommands.graph_stats import graph_stats


@click.command()
def interactive():
    """Interactive way to use the reporting tool. Takes settings from user-prompts."""
    # Result argument list
    command_opts = []
    # command_str = ["./toolkit.py"]

    # Command
    command = questionary.select("Choose command", choices=core_commands).ask()
    # command_str.append(command)

    graph_type = None
    if command == "graph":
        graph_type = questionary.select("Choose which type of graph", choices=graph_types_list).ask()
        # command_str.append(graph_type)

    reports_path = questionary.path(
        "Path of reports directory:", default=config.get_string("globals", "reports_dir")
    ).ask()
    command_opts.append(f'--reports-dir "{reports_path}"')

    # Save settings
    save_results = questionary.confirm("Save results?").ask()
    if save_results:
        output_path = questionary.path(
            "Directory path for output files:", default=config.get_string("globals", "output_dir")
        ).ask()
        filename_prefix = questionary.text("Filename prefix (leave empty for none):").ask()
        if len(filename_prefix) > 0:
            command_opts.append(f"--filename-prefix {filename_prefix}")
        if command == "graph":
            format_choices = sorted(plt.gcf().canvas.get_supported_filetypes().keys())
        else:
            format_choices = tabular_output_format.keys()
        output_format = questionary.select("Choose Output Format", choices=format_choices).ask()
        command_opts.append(f'--output-dir "{output_path}" --output-format "{output_format}"')
        show_result = questionary.confirm("Show result in terminal/windows?").ask()
        if not show_result:
            command_opts.append("--no-show")

    # Graph specific options
    if command == "graph":

        # Quantization interval if we're creating a delay or delivery graph
        if graph_type == "delay" or graph_type == "delivery":
            quant_default = (
                config.get_string("graph.delay", "quant")
                if graph_type == "delay"
                else config.get_string("graph.delivery", "quant")
            )
            quant = questionary.text("Quantization interval:", default=quant_default).ask()
            command_opts.append(f"--quant {quant}")

        # Graph theme settings
        context = questionary.select(
            "Choose Context", choices=graph_contexts, default=config.get_string("graph", "context")
        ).ask()
        palette = questionary.select(
            "Choose Palette", choices=graph_palettes, default=config.get_string("graph", "palette")
        ).ask()
        style = questionary.select(
            "Choose Style", choices=graph_styles, default=config.get_string("graph", "style")
        ).ask()
        command_opts.append(f'--context "{context}" --palette "{palette}" --style "{style}"')

        # yMin0
        if graph_type == "stats":
            ymin0 = questionary.confirm("Start the y-axis at zero?").ask()
            if ymin0:
                command_opts.append("--ymin0")

    # Groups
    if command == "diff":
        group_count = 2
    else:
        group_count = questionary.text("How many report groups?").ask()
    for group_nr in range(1, int(group_count) + 1):
        glob_default = ""
        if command == "stat" or command == "diff":
            glob_default = "*MessageStats*"
        elif graph_type == "delay":
            glob_default = "*MessageDelay*"
        elif graph_type == "delivery":
            glob_default = "*MessageDelivery*"
        group_name = questionary.text(f"Enter a name for report group #{group_nr}:").ask()
        group_pattern = questionary.text(
            f"Enter a glob pattern for report group '{group_name}':", default=glob_default
        ).ask()
        command_opts.append(f'--group "{group_pattern}" "{group_name}"')

    # Stats
    if command == "stats" or graph_type == "stats":
        checked_stats = questionary.checkbox("Select stats", choices=stat_options.keys()).ask()
        for stat in checked_stats:
            command_opts.append(f'--stat "{stat}"')

    if command == "stats":
        # Print Description
        description = questionary.confirm("Also include descriptive statistics?").ask()
        if description:
            command_opts.append("--describe")

    # Estimator
    estimator = questionary.select(
        "Choose estimator", choices=estimators, default=config.get_string("globals", "estimator")
    ).ask()
    command_opts.append(f'--estimator "{estimator}"')

    # Print arguments in a format that can be re-used
    graph_type_str = f" {graph_type}" if graph_type is not None else ""
    command_str = f"./toolkit.py {command}{graph_type_str} " + " ".join(command_opts)
    click.echo("Generated command:")
    click.echo(command_str)

    if questionary.confirm("Run this command now?", default=False).ask():
        opts = [a.strip('"') for a in " ".join(command_opts).split()]
        if command == "stats":
            stats(opts)
        elif command == "diff":
            diff(opts)
        elif graph_type == "stats":
            graph_stats(opts)
        elif graph_type == "delay":
            graph_delay(opts)
        elif graph_type == "delivery":
            graph_delivery(opts)
