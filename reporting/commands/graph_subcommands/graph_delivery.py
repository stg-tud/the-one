import click
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from report_models import MessageDeliveryReportsGroup
from commands.graph_subcommands import shared_options
from utils import save_graph_output


@click.command("delivery")
@shared_options
@click.option(
    "-q",
    "--quant",
    type=click.INT,
    default=360,
    help="Quantisation period in seconds for MessageDelayReports and MessageDeliveryReports",
    show_default=True,
)
def graph_delivery(
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
    """Draw graphs based on MessageDeliveryReport files.
     \f
    If only one group is passed, each bar represents one simulation. If multiple groups are defined, aggregate results
    are shown.
    :param quant: quantisation period in seconds for MessageDelayReports and MessageDeliveryReports
    :param filename_prefix: prefix to prepend to output file names
    :param no_show: flag to not show graphs as windows
    :param estimator: name of estimator function to use when comparing groups
    :param palette: Seaborn palette for the generated graphs
    :param context: Seaborn context for the generated graphs
    :param style: Seaborn style for the generated graphs
    :param output_dir: output directory
    :param output_format: output format
    :param group: list of tuples to split collections of reports into groups
    :param reports_dir: report directory
    """

    stats_df = pd.DataFrame()
    sns.set_theme(style=style, context=context)

    report_groups = [
        MessageDeliveryReportsGroup(glob_string, group_name, reports_dir) for (glob_string, group_name) in group
    ]
    for rg in report_groups:
        if not rg.empty:
            stats_df = stats_df.append(rg.df, ignore_index=True)

    if stats_df.empty:
        click.echo("Warning: Empty result dataframe. No stdout output and nothing saved.")
        return

    stats_df["percent"] = stats_df["delivered/created"] * 100.0

    # if absolute created messages are ever needed, we can melt the original df and let seaborn do the
    # heavy lifting for us:
    # m_df = stats_df.melt(
    #     id_vars=["group", "quant_hours"],
    #     value_vars=["created", "delivered"],
    #     var_name="status",
    #     value_name="count")
    # sns.lineplot(data=m_df, x="quant_hours", y="count", hue="group", style="status")

    num_bins = round((stats_df["time"].max() - stats_df["time"].min()) / float(quant))
    stats_df["quant"] = pd.cut(x=stats_df["time"], bins=num_bins, labels=False)
    stats_df["quant_hours"] = stats_df["quant"] * float(quant) / 3600.0

    fig = sns.lineplot(
        data=stats_df, x="quant_hours", y="delivered", hue="group", ci=None, estimator=estimator, palette=palette
    )
    fig.set(xlabel="Time [h]", ylabel="Messages Delivered")
    fig.legend().set_title(None)  # remove "groups" title from legend to avoid confusion
    fig.set_title("Message Delivery")

    save_graph_output(
        filename_prefix=filename_prefix,
        output_dir=output_dir,
        output_format=output_format,
        graph_name="MessageDeliveryReport-Abs",
    )

    plt.figure()

    fig = sns.lineplot(data=stats_df, x="quant_hours", y="percent", hue="group", ci=None)
    fig.set(xlabel="Time [h]", ylabel="Messages Delivered [%]")
    fig.legend().set_title(None)  # remove "groups" title from legend to avoid confusion

    save_graph_output(
        filename_prefix=filename_prefix,
        output_dir=output_dir,
        output_format=output_format,
        graph_name="MessageDeliveryReport-Rel",
    )

    if not no_show:
        plt.show()
