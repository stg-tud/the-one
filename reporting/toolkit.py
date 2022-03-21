#!/usr/bin/env python

import os
from pathlib import Path
import re

import click

from commands import config_group, diff, graph, interactive, stats


def print_version(ctx, _, value):
    if not value or ctx.resilient_parsing:
        return

    click.echo(f"Version {_get_version()}")
    ctx.exit()


def _get_version():
    # it is astonishingly hard to pry the version number out of pyproject.toml
    version = "[unidentified -- either pyproject.toml is missing or configured incorrectly]"
    compiled_version_regex = re.compile(r"\s*version\s*=\s*[\"']\s*([-.\w]{3,})\s*[\"']\s*")
    pyproject = Path(os.path.dirname(os.path.abspath(__file__))) / "pyproject.toml"
    if pyproject.is_file():
        with pyproject.open(mode="r") as fh:
            for line in fh:
                ver = compiled_version_regex.search(line)
                if ver is not None:
                    version = ver.group(1).strip()
                    break
    return version


@click.group()
@click.option(
    "-v",
    "--version",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
    help="Show version and exit.",
)
def toolkit():
    """The OneTwo Reporting Toolkit"""
    pass


# noinspection PyTypeChecker
toolkit.add_command(config_group, name="config")
# noinspection PyTypeChecker
toolkit.add_command(diff, name="diff")
# noinspection PyTypeChecker
toolkit.add_command(graph, name="graph")
# noinspection PyTypeChecker
toolkit.add_command(stats, name="stats")
# noinspection PyTypeChecker
toolkit.add_command(interactive, name="i")

if __name__ == "__main__":
    toolkit()
