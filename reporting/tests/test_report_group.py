import io
from contextlib import redirect_stdout
from unittest import TestCase

import pandas as pd
import pytest
from pytest_mock import MockerFixture

from report_models.reports_group import ReportsGroup


class TestReportsGroup(TestCase):
    glob_string: str
    group_name: str
    reports_dir: str

    def setUp(self):
        super().setUp()
        self.glob_string = "test_globstr"
        self.group_name = "G1"
        self.reports_dir = "."

    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker: MockerFixture):
        self.mocker = mocker

    def test_group_name(self) -> None:
        self.mocker.patch("report_models.reports_group.ReportsGroup.empty", False)
        report_group = ReportsGroup(
            glob_string=self.glob_string, group_name=self.group_name, reports_dir=self.reports_dir
        )
        self.assertEqual(report_group.name, self.group_name)

    def test_set_df(self) -> None:
        expected_df = pd.DataFrame(
            data={"delivered": [100.0, 500.0, 600.0], "delivery_prob": [0.25, 0.3, 0.9]}, index=["S1", "S2", "S3"]
        )
        self.mocker.patch("report_models.reports_group.ReportsGroup.empty", False)
        report_group = ReportsGroup(
            glob_string=self.glob_string, group_name=self.group_name, reports_dir=self.reports_dir
        )
        report_group.df = expected_df
        self.assertTrue(report_group.df.equals(expected_df))

    def test_empty_group(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            report_group = ReportsGroup(
                glob_string=self.glob_string, group_name=self.group_name, reports_dir=self.reports_dir
            )
        self.assertTrue(report_group.empty)
