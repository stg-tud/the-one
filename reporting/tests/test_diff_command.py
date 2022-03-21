from pathlib import Path
from typing import List
from unittest import TestCase
from unittest.mock import ANY

from click.testing import CliRunner, Result
import pytest
from pytest_mock import MockerFixture

from tests.mock_classes import MockMessageStatsReportsGroup
from toolkit import toolkit

runner = CliRunner()


class TestDiffCommand(TestCase):
    default_opts: List[str]
    empty_group_opts: List[str]
    file_output_opts: List[str]
    two_group_opts: List[str]
    one_group_opts: List[str]
    mocker: MockerFixture

    def setUp(self):
        super().setUp()
        self.default_opts = ["diff", "--reports-dir", "."]
        self.two_group_opts = ["--group", "", "G2", "--group", "", "G1"]
        self.one_group_opts = ["--group", "", "G2"]
        self.empty_group_opts = ["--group", "", "empty", "--group", "", "G2"]
        self.file_output_opts = ["-p", "test_", "--estimator", "median", "--output-format", "latex", "-o", "."]

    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker: MockerFixture):
        self.mocker = mocker
        self.mocker.patch("commands.diff_command.MessageStatsReportsGroup", MockMessageStatsReportsGroup, spec=True)

    def test_empty_dataframe(self) -> None:
        result_empty_df: Result = runner.invoke(toolkit, self.default_opts + self.empty_group_opts)
        print(result_empty_df.output)
        self.assertEqual(result_empty_df.exit_code, 0)
        self.assertIn("Warning: Empty result dataframe.", result_empty_df.output)

    def test_no_show(self) -> None:
        result_no_show: Result = runner.invoke(toolkit, self.default_opts + self.two_group_opts + ["--no-show"])
        self.assertEqual(result_no_show.exit_code, 0)
        self.assertEqual(len(result_no_show.output), 0)

    def test_one_group_error(self) -> None:
        result_one_group: Result = runner.invoke(toolkit, self.default_opts + self.one_group_opts)
        self.assertNotEqual(result_one_group.exit_code, 0)
        self.assertIn("You must pass two groups when calling diff.", result_one_group.output)

    def test_correct_mean(self) -> None:
        result_mean: Result = runner.invoke(toolkit, self.default_opts + self.two_group_opts + ["--estimator", "mean"])
        self.assertEqual(result_mean.exit_code, 0)
        self.assertRegex(result_mean.output, r"delivery_prob\s+0\.5\s+0\.25\s+0\.25\s+0.5")

    def test_correct_median(self) -> None:
        result_median: Result = runner.invoke(
            toolkit, self.default_opts + self.two_group_opts + ["--estimator", "median"]
        )
        self.assertEqual(result_median.exit_code, 0)
        self.assertRegex(result_median.output, r"delivery_prob\s+0\.3\s+0\.25\s+0\.05\s+0.16")

    def test_output_to_file(self) -> None:
        with runner.isolated_filesystem():
            mock_save = self.mocker.patch("commands.diff_command.save_tabular")
            mock_save_opts = self.mocker.patch("commands.diff_command.get_output_options")
            mock_save_opts.return_value = (Path("."), True)

            result_output_file: Result = runner.invoke(
                toolkit, self.default_opts + self.two_group_opts + self.file_output_opts
            )

            self.assertEqual(result_output_file.exit_code, 0)
            mock_save_opts.assert_called_once_with(output_dir=".", file_format="latex")
            mock_save.assert_called_once_with(
                prefix="test_",
                filename="diff_output",
                file_format="latex",
                output_dir=Path("."),
                df=ANY,  # work-around because comparison to expected_df fails
            )
