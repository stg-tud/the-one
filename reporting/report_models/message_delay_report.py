from report_models.reports_group import ReportsGroup


class MessageDelayReportsGroup(ReportsGroup):
    """
    Class to manage MessageDelayReports

    :param glob_string: glob pattern to select report data files
    :param group_name: name for report group that is used to compare data in tables and graphs
    :param reports_dir: directory of the report data files
    """

    def __init__(self, glob_string: str, group_name: str, reports_dir: str):
        super().__init__(glob_string, group_name, reports_dir)

    def _load_data(self) -> None:
        cols = ["messageDelay", "cumulativeProbability"]
        self._load_times_series_data(cols=cols, file_handles=self._get_file_handles())
        if "messageDelay" not in self._df.keys():
            print('ERROR: Report data missing "messageDelay" column.')
            print("This might be caused by glob patterns that include wrong report files.")
            exit(1)
        self._df["hours"] = self._df["messageDelay"] / 3600
