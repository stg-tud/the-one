import click
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from commands import stat_options, help_texts
import config
from report_models import MessageStatsReportsGroup
from commands.graph_subcommands import shared_options
from utils import show_describe_df, save_graph_output


@click.command("stats")
@shared_options
@click.option("-c", "--describe", help=help_texts["describe"], is_flag=True, type=click.BOOL)
@click.option(
    "-s",
    "--stat",
    default=config.get_list("graph.stats", "stat"),
    help=help_texts["stat"],
    type=click.Choice(stat_options.keys(), case_sensitive=False),
    multiple=True,
    show_default=True,
)
@click.option("-0", "--ymin0", default=False, help=help_texts["ymin0"], is_flag=True, type=click.BOOL)
def graph_stats(
    describe,
    reports_dir,
    estimator,
    group,
    output_format,
    filename_prefix,
    output_dir,
    stat,
    style,
    context,
    palette,
    ymin0,
    no_show,
):
    """Draw graphs based on MessageStatsReport files.
     \f
    If only one group is passed, each bar represents one simulation. If multiple groups are defined, aggregate results
    are shown.
    :param describe: shows info on how many reports were considered and also the min and max values
    :param filename_prefix: prefix to prepend to output file names
    :param no_show: flag to not show graphs as windows
    :param estimator: name of estimator function to use when comparing groups
    :param ymin0: Start the y-axis at 0 no matter what
    :param palette: Seaborn palette for the generated graphs
    :param context: Seaborn context for the generated graphs
    :param style: Seaborn style for the generated graphs
    :param stat: name of the statistics value that should be parsed from the report files
    :param output_dir: output directory
    :param output_format: output format
    :param group: list of tuples to split collections of reports into groups
    :param reports_dir: report directory
    """

    stats_df = pd.DataFrame()
    sns.set_theme(style=style, context=context)
    plt.rcParams["errorbar.capsize"] = 10

    report_groups = [
        MessageStatsReportsGroup(glob_string, group_name, reports_dir) for (glob_string, group_name) in group
    ]
    cols = list(report_groups[0].df.columns) if "all" in stat else list(stat)

    one_group = len(report_groups) == 1
    if one_group:
        # only one group: just show graph of generated stats
        rg = report_groups[0]
        if not rg.empty:
            stats_df = rg.df
    else:
        # more groups: aggregate with estimator and list all stats for each group
        # this could also be cleverly rewritten as two reduce calls, but we're opting for readability here:
        stats_df = pd.DataFrame()
        for rg in report_groups:
            if not rg.empty:
                df = rg.df.loc[:, cols]
                df["group"] = rg.name
                stats_df = stats_df.append(other=df)

    if stats_df.empty:
        click.echo("Warning: Empty result dataframe. No graphs to output and nothing saved.")
        return

    # current stat index to control the plt.figure() call in the loop
    i = 0
    # cycle through all selected stats columns and output a graph for each
    for st in cols:
        if one_group:
            fig = sns.barplot(x=stats_df.index, y=stats_df[st], palette=palette)
            xlabel = "Scenario"
        else:
            data = stats_df.groupby(["group"]).agg([min, max, estimator])[st]
            # requirement: show min/max values on each bar as error
            yerr = data[["min", "max"]].sub(data[estimator], axis=0).abs().T.to_numpy()
            # requirement: use statistics.median instead of the default mean here:
            fig = sns.barplot(data=data, y=estimator, x=data.index, palette=palette, yerr=yerr)
            xlabel = "Group"

        fig.set_title(stat_options[st])
        fig.set_ylabel(stat_options[st])
        fig.set_xlabel(xlabel)

        if ymin0:
            fig.set_ylim(bottom=0)
        else:
            fig.set_ylim((stats_df[st].min() * 0.98, stats_df[st].max() * 1.005))

        save_graph_output(
            filename_prefix=filename_prefix,
            output_dir=output_dir,
            output_format=output_format,
            graph_name=f"MessageStatsReport-{st}",
        )

        # call this only between to plots, never at the end
        if i < len(cols) - 1:
            plt.figure()
        i += 1

    if describe:
        show_describe_df(report_groups, cols, estimator)

    if not no_show:
        plt.show()
