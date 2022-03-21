import pandas as pd
from pandas import DataFrame

from report_models.reports_group import ReportsGroup


class MessageStatsReportsGroup(ReportsGroup):
    """
    A reports-group contains a certain collection of reports that can be either intrinsically compared or used for
    comparisons with other ReportSeries objects.

    :param glob_string: glob pattern to look for
    :param reports_dir: directory of the files

    """

    def __init__(self, glob_string: str, group_name: str, reports_dir: str):
        super().__init__(glob_string, group_name, reports_dir)

    def _load_data(self) -> None:
        """ " Utility method to assist in loading all data from a collection of filepaths"""

        file_handles = self._get_file_handles()

        if len(file_handles) > 0:
            msg_stats = []
            for fh in file_handles:
                scenario = {"scenario": fh.readline().split(" ")[-1].strip()}
                for line in fh.readlines():
                    elems = line.split(":")
                    if len(elems) > 1:
                        scenario[elems[0].strip()] = elems[1].strip()
                msg_stats.append(scenario)
                fh.close()

            self._df = DataFrame(msg_stats).set_index("scenario").sort_index()
            for col in self._df.columns:
                if col != "scenario":
                    self._df[col] = pd.to_numeric(self._df[col], errors="coerce")
