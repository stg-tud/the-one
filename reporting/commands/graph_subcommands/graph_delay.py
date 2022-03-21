import click
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from pathlib import Path

from commands.graph_subcommands import shared_options
from report_models import MessageDelayReportsGroup
from utils import get_output_options


@click.command("delay")
@shared_options
@click.option(
    "-q",
    "--quant",
    type=click.INT,
    default=360,
    help="Quantisation period in seconds for MessageDelayReports and MessageDeliveryReports",
    show_default=True,
)
def graph_delay(
    reports_dir,
    estimator,
    group,
    output_format,
    filename_prefix,
    output_dir,
    style,
    context,
    palette,
    quant,
    no_show,
):
    """Draw graphs based on MessageDelayReport files.
    \f
    If only one group is passed, each bar represents one simulation. If multiple groups are defined, aggregate results
    are shown.

    :param context: Seaborn context for the generated graphs
    :param estimator: name of estimator function to use when comparing groups
    :param filename_prefix: prefix to prepend to output file names
    :param group: list of tuples to split collections of reports into groups
    :param no_show: flag to not show graphs as windows
    :param output_dir: output directory
    :param output_format: output format
    :param palette: Seaborn palette for the generated graphs
    :param quant: quantisation period in seconds for MessageDelayReports and MessageDeliveryReports
    :param reports_dir: report directory
    :param style: Seaborn style for the generated graphs
    """

    stats_df = pd.DataFrame()
    sns.set_theme(style=style, context=context)

    report_groups = [
        MessageDelayReportsGroup(glob_string, group_name, reports_dir) for (glob_string, group_name) in group
    ]
    for rg in report_groups:
        if not rg.empty:
            stats_df = stats_df.append(rg.df, ignore_index=True)

    if stats_df.empty:
        click.echo("Warning: Empty result dataframe. No stdout output and nothing saved.")
        return

    num_bins = round((stats_df["messageDelay"].max() - stats_df["messageDelay"].min()) / float(quant))
    stats_df["quant"] = pd.cut(x=stats_df["messageDelay"], bins=num_bins, labels=False)
    stats_df["quant_hours"] = stats_df["quant"] * float(quant) / 3600.0

    fig = sns.lineplot(
        data=stats_df,
        x="quant_hours",
        y="cumulativeProbability",
        hue="group",
        ci=None,
        estimator=estimator,
        palette=palette,
    )
    fig.set(xlabel="Delivery Delay [h]", ylabel="Messages")
    fig.legend().set_title(None)  # remove "groups" title from legend to avoid confusion
    fig.set_title("Message Delay")

    output_dir_path, save_output = get_output_options(output_dir=output_dir, file_format=output_format)
    if save_output:
        fp = Path(output_dir_path, f'{filename_prefix or ""}MessageDelayReport.{output_format.lower()}')
        plt.savefig(fp, dpi=300)

    if not no_show:
        plt.show()
