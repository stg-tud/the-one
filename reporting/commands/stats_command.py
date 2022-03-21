import click
import config
import pandas as pd

from report_models import MessageStatsReportsGroup
from commands import estimators, tabular_output_format, stat_options, help_texts
from utils import get_output_options, save_tabular, show_describe_df


@click.command("stats")
@click.option("-c", "--describe", help=help_texts["describe"], is_flag=True, type=click.BOOL)
@click.option(
    "-e",
    "--estimator",
    default=config.get_string("globals", "estimator"),
    help=help_texts["estimator"],
    show_default=True,
    type=click.Choice(estimators, case_sensitive=False),
)
@click.option("-p", "--filename-prefix", help=help_texts["filename_prefix"], type=click.STRING)
@click.option(
    "-g",
    "--group",
    help=help_texts["group"],
    nargs=2,
    type=click.Tuple([str, str]),
    multiple=True,
    show_default=True,
)
@click.option("-n", "--no-show", default=False, help=help_texts["no_show"], is_flag=True, type=click.BOOL)
@click.option(
    "-o",
    "--output-dir",
    default=config.get_string("globals", "output_dir"),
    help=help_texts["output_dir"],
    show_default=True,
    type=click.Path(),
)
@click.option(
    "-f",
    "--output-format",
    help=help_texts["output_format"],
    type=click.Choice(tabular_output_format, case_sensitive=False),
)
@click.option(
    "-d",
    "--reports-dir",
    default=config.get_string("globals", "reports_dir"),
    help=help_texts["reports_dir"],
    show_default=True,
    type=click.Path(exists=True),
)
@click.option(
    "-s",
    "--stat",
    default=config.get_list("graph.stats", "stat"),
    help=help_texts["stat"],
    multiple=True,
    show_default=True,
    type=click.Choice(stat_options.keys(), case_sensitive=False),
)
def stats(describe, reports_dir, estimator, group, output_dir, stat, output_format, filename_prefix, no_show):
    """Get stats from the generated report files.
    \f
    :param describe: shows info on how many reports were considered and also the min and max values
    :param filename_prefix: prefix to prepend to output file names
    :param estimator: name of estimator function to use when comparing groups
    :param group: list of tuples to split collections of reports into groups
    :param no_show: flag to not show graphs as windows
    :param output_dir: output directory
    :param output_format: output format
    :param reports_dir: report directory
    :param stat: name of the statistics value that should be parsed from the report files
    """

    report_groups = [
        MessageStatsReportsGroup(glob_string, group_name, reports_dir) for (glob_string, group_name) in group
    ]
    cols = list(report_groups[0].df.columns) if "all" in stat else list(stat)
    stats_df = pd.DataFrame()

    if len(report_groups) == 1:
        # only one group: list all the found scenarios with their individual stats
        rg = report_groups[0]
        if not rg.empty:
            stats_df = rg.df[cols]
    else:
        # more groups: aggregate with estimator and list all stats for each group
        for rg in report_groups:
            if not rg.empty:
                stats_df = stats_df.append(rg.df[cols].agg(estimator).to_frame(rg.name).T)

    if stats_df.empty:
        click.echo("Warning: Empty result dataframe. No stdout output and nothing saved.")
        return

    if not no_show:
        click.echo(stats_df)

    if describe:
        click.echo()
        show_describe_df(report_groups, cols, estimator)

    output_dir_path, save_output = get_output_options(output_dir=output_dir, file_format=output_format)
    if save_output:
        save_tabular(
            prefix=filename_prefix,
            filename="stats_output",
            file_format=output_format,
            output_dir=output_dir_path,
            df=stats_df,
        )
