import click
import config as conf
import matplotlib.pyplot as plt

from commands import estimators, graph_contexts, graph_palettes, graph_styles, help_texts

# shared options for all graph sub-commands
# these are defined here so they can be passed first after the sub-command instead of directly after graph
# more details see here: https://github.com/pallets/click/issues/108
_shared_options = [
    click.option(
        "-c",
        "--context",
        default=conf.get_string("graph", "context"),
        help=help_texts["context"],
        show_default=True,
        type=click.Choice(graph_contexts),
    ),
    click.option(
        "-e",
        "--estimator",
        default=conf.get_string("globals", "estimator"),
        help=help_texts["estimator"],
        show_default=True,
        type=click.Choice(estimators, case_sensitive=False),
    ),
    click.option("--filename-prefix", help=help_texts["filename_prefix"], type=click.STRING),
    click.option(
        "-g",
        "--group",
        help=help_texts["group"],
        nargs=2,
        type=click.Tuple([str, str]),
        multiple=True,
        show_default=True,
    ),
    click.option("-n", "--no-show", default=False, help=help_texts["no_show"], is_flag=True, type=click.BOOL),
    click.option(
        "-o",
        "--output-dir",
        default=conf.get_string("globals", "output_dir"),
        help=help_texts["output_dir"],
        show_default=True,
        type=click.Path(),
    ),
    click.option(
        "-f",
        "--output-format",
        help=help_texts["output_format"],
        type=click.Choice(sorted(plt.gcf().canvas.get_supported_filetypes().keys()), case_sensitive=False),
    ),
    click.option(
        "-p",
        "--palette",
        default=conf.get_string("graph", "palette"),
        help=help_texts["palette"],
        type=click.Choice(graph_palettes),
        show_default=True,
    ),
    click.option(
        "-d",
        "--reports-dir",
        default=conf.get_string("globals", "reports_dir"),
        help=help_texts["reports_dir"],
        type=click.Path(exists=True),
        show_default=True,
    ),
    click.option(
        "-y",
        "--style",
        default=conf.get_string("graph", "style"),
        help=help_texts["style"],
        type=click.Choice(graph_styles),
        show_default=True,
    ),
]


def shared_options(func):
    for option in reversed(_shared_options):
        func = option(func)
    return func
