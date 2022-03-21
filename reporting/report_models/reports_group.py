from abc import abstractmethod
from glob import glob
from pathlib import PurePath

import click
import pandas as pd


class ReportsGroup:
    """
    A reports-group contains a certain collection of reports that can be either intrinsically compared or used for
    comparisons with other ReportsGroup objects. This is the parent class that can be inherited from for different
    report types.

    It mainly provides methods for associating report-group names and related The OneTwo report data as well as a few
    hand getter and setter methods.

    :param glob_string: glob pattern to select report data files
    :param group_name: name for report group that is used to compare data in tables and graphs
    :param reports_dir: directory of the report data files
    """

    def __init__(self, glob_string: str, group_name: str, reports_dir: str):
        self._glob_string = glob_string
        self._group_name = group_name
        self._reports_dir = reports_dir
        self._file_list = []
        self._df = pd.DataFrame()
        self._file_list = glob(PurePath(self._reports_dir, self._glob_string).as_posix())

        self._load_data()

        if self.empty:
            click.echo(
                f"Warning: {self._group_name} dataframe is empty. No report files match glob '{self._glob_string}'"
            )

    @property
    def df(self) -> pd.DataFrame:
        return self._df

    @df.setter
    def df(self, df: pd.DataFrame) -> None:
        self._df = df

    @property
    def name(self) -> str:
        return self._group_name

    @property
    def empty(self) -> bool:
        return self._df.empty

    @abstractmethod
    def _load_data(self) -> None:
        """
        To implement in child classes. Will handle in the reading in of report data files depending on report class
        """
        pass

    def _get_file_handles(self):
        try:
            file_handles = [open(fp, "r") for fp in self._file_list]
        except (OSError, FileNotFoundError) as e:
            print(
                f"ERROR: Something went terribly wrong opening a file. Please check your glob pattern or file list and "
                f"try again. OS Error: {e}"
            )
            file_handles = []
        return file_handles

    def _load_times_series_data(self, cols: list, file_handles: list, omit_header: bool = True):
        """
        Utility function to handle reading in time-series style data in which one line in a file represents a
        time-related data sample

        :param cols: list of column names
        :param file_handles: list of opened file handles that provide the data files to read in data from
        :param omit_header: set to true if file contains a header that is not part of the contained data readings

        """
        if len(file_handles) == 0:
            click.echo("ERROR: No files matching your glob patterns found.")
            exit(1)

        for fh in file_handles:
            raw_data = fh.readlines()[1:] if omit_header else fh.readlines()
            data_untyped = [[d.strip() for d in meas.split()] for meas in raw_data]

            _exit_on_valid_col_num(filename=fh.name, cols=cols, data=data_untyped)

            new_df = pd.DataFrame(data_untyped, columns=cols)
            for col in new_df.columns:
                new_df[col] = pd.to_numeric(new_df[col], errors="coerce")
            new_df["scenario"] = PurePath(fh.name).stem
            new_df["group"] = self._group_name
            self._df = self._df.append(new_df, ignore_index=True)

            fh.close()

        # some very basic cleaning, this might have to be expanded depending on data quality
        # of different simulation setups
        self._df = self._df.dropna(axis=1, how="all").dropna(axis=0, how="any")

    def __repr__(self):
        return f"{self.__class__.__name__}({self._glob_string}, {self._group_name}, {self._reports_dir})"


def _exit_on_valid_col_num(filename: str, cols: list, data: list):
    # check if we're ingesting valid data: if the number of passed columns doesn't equal
    # the number of read-in columns, something is fishy:
    found_lengths = [len(d) for d in data]
    max_col = max(found_lengths)
    min_col = min(found_lengths)
    if all([len(cols) == length for length in found_lengths]):
        return
    else:
        click.echo("ERROR: Report data shape not suitable for further processing.")
        if max_col == min_col:
            click.echo(f"Data was supposed to have {len(cols)} columns, but it actually had {max_col} columns.")
        else:
            click.echo(
                f"Data was supposed to have {len(cols)} columns, but it actually had between {min_col} to "
                f"{max_col} columns."
            )
        click.echo(f"Encountered in {filename}")
        click.echo("This might be caused by glob patterns that include wrong report files")
        click.echo("or incomplete report files due to aborted simulations.")
        exit(1)
