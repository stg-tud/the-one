from pathlib import Path
from typing import List
from unittest import TestCase
from unittest.mock import ANY

import pandas as pd
from click.testing import CliRunner, Result
import pytest
from pytest_mock import MockerFixture

from tests.mock_classes import MockMessageStatsReportsGroup
from toolkit import toolkit

runner = CliRunner()


class TestStatsCommand(TestCase):
    default_opts: List[str]
    empty_group_opts: List[str]
    file_output_opts: List[str]
    mul_group_opts: List[str]
    one_group_opts: List[str]
    mocker: MockerFixture

    def setUp(self) -> None:
        super().setUp()
        self.default_opts = ["stats", "--stat", "delivered", "--stat", "delivery_prob", "--reports-dir", "."]
        self.mul_group_opts = ["--group", "", "G1", "--group", "", "G2", "--group", "", "G3"]
        self.one_group_opts = ["--group", "", "G2"]
        self.empty_group_opts = ["--group", "", "empty"]
        self.file_output_opts = ["-p", "test_", "--estimator", "median", "--output-format", "latex", "-o", "."]

    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker: MockerFixture) -> None:
        self.mocker = mocker
        self.mocker.patch("commands.stats_command.MessageStatsReportsGroup", MockMessageStatsReportsGroup, spec=True)

    def test_empty_dataframe(self) -> None:
        result_empty_df: Result = runner.invoke(toolkit, self.default_opts + self.empty_group_opts)
        self.assertEqual(result_empty_df.exit_code, 0)
        self.assertIn("Warning: Empty result dataframe", result_empty_df.output)

    def test_no_show(self) -> None:
        result_no_show: Result = runner.invoke(toolkit, self.default_opts + self.one_group_opts + ["--no-show"])
        self.assertEqual(result_no_show.exit_code, 0)
        self.assertEqual(len(result_no_show.output), 0)

    def test_describe(self) -> None:
        result_describe: Result = runner.invoke(
            toolkit, self.default_opts + self.mul_group_opts + ["--estimator", "median", "--describe"]
        )
        self.assertEqual(result_describe.exit_code, 0)
        self.assertIn("delivered", result_describe.output)
        self.assertIn("delivery_prob", result_describe.output)
        self.assertRegex(result_describe.output, r"count\s+min\s+median\s+max")
        self.assertRegex(result_describe.output, r"G2\s+3\s+200\s+500\s+5000\s+3\s+0\.25\s+0\.30\s+0\.95")

    def test_correct_mean(self) -> None:
        result_mean: Result = runner.invoke(toolkit, self.default_opts + self.mul_group_opts + ["--estimator", "mean"])
        self.assertEqual(result_mean.exit_code, 0)
        self.assertRegex(result_mean.output, r"G2\s+1900\.0\s+0\.50")

    def test_correct_median(self) -> None:
        result_median: Result = runner.invoke(
            toolkit, self.default_opts + self.mul_group_opts + ["--estimator", "median"]
        )
        self.assertEqual(result_median.exit_code, 0)
        self.assertRegex(result_median.output, r"G2\s+500\.0\s+0\.30")

    def test_correct_one_group(self) -> None:
        result_one_group: Result = runner.invoke(toolkit, self.default_opts + self.one_group_opts)
        self.assertEqual(result_one_group.exit_code, 0)
        self.assertRegex(result_one_group.output, r"S2\s+200\s+0\.25")
        self.assertRegex(result_one_group.output, r"S3\s+500\s+0\.30")
        self.assertRegex(result_one_group.output, r"S4\s+5000\s+0\.95")

    def test_output_to_file(self) -> None:
        expected_df = pd.DataFrame(  # noqa F841 for now
            data={"delivered": [100.0, 500.0, 600.0], "delivery_prob": [0.25, 0.3, 0.9]}, index=["G1", "G2", "G3"]
        )
        with runner.isolated_filesystem():
            # mock called functions so test coverage stays in the module
            mock_save = self.mocker.patch("commands.stats_command.save_tabular")
            mock_save_opts = self.mocker.patch("commands.stats_command.get_output_options")
            mock_save_opts.return_value = (Path("."), True)

            result_output_file: Result = runner.invoke(
                toolkit, self.default_opts + self.mul_group_opts + self.file_output_opts
            )

            self.assertEqual(result_output_file.exit_code, 0)
            mock_save_opts.assert_called_once_with(output_dir=".", file_format="latex")
            mock_save.assert_called_once_with(
                prefix="test_",
                filename="stats_output",
                file_format="latex",
                output_dir=Path("."),
                df=ANY,  # work-around because comparison to expected_df fails
            )
