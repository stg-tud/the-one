from io import StringIO
from unittest import TestCase
from unittest.mock import MagicMock, mock_open, Mock

import pandas as pd
import pytest
from pytest_mock import MockerFixture

from report_models.message_stats_report import MessageStatsReportsGroup

report_text1 = """Message stats for scenario test_scenario1
sim_time: 12345.0000
created: 98
started: 65
relayed: 32
aborted: 12
dropped: 45"""
report_text2 = """Message stats for scenario test_scenario2
sim_time: 12345.0000
created: 97
started: 64
relayed: 31
aborted: 13
dropped: 46"""
report_text3 = """Message stats for scenario test_scenario3
sim_time: 12345.0000
created: 87
started: 54
relayed: 21
aborted: 23
dropped: 56"""

report_contents = {
    "msg_stats_report_1.txt": report_text1,
    "msg_stats_report_2.txt": report_text2,
    "msg_stats_report_3.txt": report_text3,
}

expected_df = pd.DataFrame(
    data={
        "sim_time": [12345.0, 12345.0, 12345.0],
        "created": [98, 97, 87],
        "started": [65, 64, 54],
        "relayed": [32, 31, 21],
        "aborted": [12, 13, 23],
        "dropped": [45, 46, 56],
    },
    index=["test_scenario1", "test_scenario2", "test_scenario3"],
)


def open_side_effect(name: str, _) -> Mock:
    if name not in report_contents.keys():
        raise FileNotFoundError("Entry not found in report_contents dict")
    return mock_open(read_data=report_contents.get(name))()


class TestMessageStatsReportsGroup(TestCase):
    glob_string: str
    group_name: str
    reports_dir: str

    def setUp(self) -> None:
        super().setUp()
        self.glob_string = "test_globstr"
        self.group_name = "G1"
        self.reports_dir = "."

    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker: MockerFixture) -> None:
        self.mocker = mocker

    def test_load_data(self) -> None:
        # this is going to take a lot of mocking:
        mock_glob: MagicMock = self.mocker.patch("report_models.reports_group.glob")
        mock_glob.return_value = ["msg_stats_report_1.txt", "msg_stats_report_2.txt", "msg_stats_report_3.txt"]
        mock_file: MagicMock = self.mocker.patch("builtins.open", side_effect=open_side_effect)

        reports_group = MessageStatsReportsGroup(
            glob_string=self.glob_string, group_name=self.group_name, reports_dir=self.reports_dir
        )
        self.assertTrue(not reports_group.empty)
        self.assertTrue(expected_df.equals(reports_group.df))
        self.assertEqual(mock_file.call_count, 3)

    def test_open_error(self) -> None:
        mock_glob: MagicMock = self.mocker.patch("report_models.reports_group.glob")
        mock_glob.return_value = ["non_existent_file.txt"]
        mock_fail_open: MagicMock = self.mocker.patch("builtins.open")
        mock_fail_open.side_effect = OSError("Don't worry, we're only mocking!")
        mock_stdout = self.mocker.patch("sys.stdout", new=StringIO())
        MessageStatsReportsGroup(glob_string=self.glob_string, group_name=self.group_name, reports_dir=self.reports_dir)
        self.assertIn("ERROR", mock_stdout.getvalue())
