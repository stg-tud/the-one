import click
import pandas as pd

import config

from commands import tabular_output_format, help_texts, estimators
from report_models import MessageStatsReportsGroup
from utils import get_output_options, save_tabular


@click.command("diff")
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
    type=click.Path(),
)
def diff(reports_dir, estimator, group, output_dir, output_format, filename_prefix, no_show):
    """Compare two generated simulation report files. If more than two groups are defined, only the first two will be
    considered.
    \f
    :param estimator: name of estimator function to use when comparing groups
    :param filename_prefix: prefix to prepend to output file names
    :param group: list of tuples to split collections of reports into groups
    :param no_show: flag to not show graphs as windows
    :param output_dir: output directory
    :param output_format: output format
    :param reports_dir: report directory
    """

    report_groups = [
        MessageStatsReportsGroup(glob_string, group_name, reports_dir) for (glob_string, group_name) in group
    ]
    stats_df, stats_a, stats_b = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    df_list = [rg.df for rg in report_groups]

    try:
        # get the first two tables of reporting data and join them
        stats_a = df_list[0].agg(estimator)
        stats_b = df_list[1].agg(estimator)
    except IndexError as e:
        click.echo(f"ERROR: You must pass two groups when calling diff. {e}")
        exit(1)

    stats_df = stats_a.to_frame(report_groups[0].name).join(stats_b.to_frame(report_groups[1].name))

    if stats_df.empty:
        click.echo("Warning: Empty result dataframe. No stdout output and nothing saved.")
        return

    stats_df["diff"] = stats_a - stats_b
    stats_df["rel_diff"] = stats_df["diff"] / stats_a

    if not no_show:
        click.echo(stats_df)

    output_dir_path, save_output = get_output_options(output_dir=output_dir, file_format=output_format)
    if save_output:
        save_tabular(
            prefix=filename_prefix,
            filename="diff_output",
            file_format=output_format,
            output_dir=output_dir_path,
            df=stats_df,
        )
