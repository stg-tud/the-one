import click
from matplotlib import pyplot as plt
import pandas as pd
from pathlib import Path
from typing import Tuple

from commands import tabular_output_format


def get_output_options(file_format: str, output_dir: str = "") -> Tuple[Path, bool]:
    """
    Utility function to return a tuple containing information about if and where
    output files are to be saved.

    :param output_dir: string description of the output directory
    :param file_format: identifier for output format
    """
    # check if we have a valid path before doing anything else
    save_output = False
    output_path = Path(output_dir or "")
    if file_format:
        try:
            # create directory if it doesn't exist
            output_path.mkdir(parents=True, exist_ok=True)
            save_output = True
        except FileExistsError as e:
            click.echo(f"The path to your --output-dir points to an existing file. Output will not be saved. {e}")
    return output_path, save_output


def save_tabular(
    file_format: str, output_dir: Path, df: pd.DataFrame, prefix: str = "", filename: str = "output"
) -> None:
    """
    Utility function to save tabular data located in a Pandas dataframe

    :param filename: filename for the output file
    :param file_format: identifier for output format
    :param output_dir: string description of the output directory
    :param df: Pandas dataframe to be saved to output file
    :param prefix: filename prefix for the saved file
    """
    fmt = file_format.lower()
    ext = tabular_output_format[fmt]
    fp = Path(output_dir, f'{prefix or ""}{filename}.{ext}')
    if fmt == "csv":
        df.to_csv(fp)
    elif fmt == "json":
        df.to_json(fp)
    elif fmt == "pickle":
        df.to_pickle(str(fp))
    elif fmt == "latex":
        df.to_latex(fp)


def show_describe_df(report_groups, cols, estimator):
    """quick and dirty descriptive statistics (N, min, max) of report groups"""
    desc_df = pd.DataFrame()
    for rg in report_groups:
        if not rg.empty:
            desc_df = desc_df.append(rg.df.assign(report_group=rg.name))
    if not desc_df.empty:
        click.echo(
            desc_df.groupby("report_group", sort=False).agg({c: ["count", "min", estimator, "max"] for c in cols})
        )


def save_graph_output(filename_prefix, graph_name, output_dir, output_format):
    output_dir_path, save_output = get_output_options(output_dir=output_dir, file_format=output_format)
    if save_output:
        fp = Path(output_dir_path, f'{filename_prefix or ""}{graph_name}.{output_format.lower()}')
        plt.savefig(fp, dpi=300)
