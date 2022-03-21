import click

from commands.graph_subcommands.graph_delay import graph_delay
from commands.graph_subcommands.graph_delivery import graph_delivery

from commands.graph_subcommands.graph_stats import graph_stats


@click.group("graph")
def graph():
    """Draw graphs based on the generated report files."""
    pass


# noinspection PyTypeChecker
graph.add_command(graph_delay, name="delay")
# noinspection PyTypeChecker
graph.add_command(graph_delivery, name="delivery")
# noinspection PyTypeChecker
graph.add_command(graph_stats, name="stats")
