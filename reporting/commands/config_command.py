import click
import config


reset_values = {
    "globals": {"estimator": "median", "output_dir": "./output/", "reports_dir": "../reports/"},
    "graph": {"context": "paper", "palette": "muted", "style": "whitegrid"},
    "graph.delivery": {"quant": "300"},
    "graph.delay": {"quant": "300"},
    "graph.stats": {"stat": "created, started, relayed, aborted, dropped, delivered, delivery_prob"},
    "stats": {"stat": "created, started, relayed, aborted, dropped, delivered, delivery_prob"},
}


@click.group("config")
def config_group():
    """Configuration of defaults"""
    pass


@config_group.command("set")
@click.argument("setting", nargs=1)
@click.argument("value", nargs=1)
def set_settings(setting, value):
    """Change defaults. Use the format full_section_name.key value to identify setting"""

    if "." not in setting:
        _exit_invalid_setting(setting)
    settings_args = setting.split(".")
    if len(settings_args) == 2:
        sect, opt = settings_args
    else:
        sect = ".".join(settings_args[:-1])
        opt = settings_args[-1]

    if sect not in config.get_sections():
        _exit_invalid_setting(setting)

    config.set_value(sect, opt, value)
    click.echo("New default saved to config.ini:")
    click.echo(f"     Section: {sect}, Option: {opt}, Value: {value}")


@config_group.command("list")
def list_settings():
    """List all settable defaults and their current values"""
    settings_dict = config.get_all_items_in_dict()
    for k in settings_dict.keys():
        click.echo(f"Setting: {k}")
        for v in settings_dict[k]:
            click.echo(f"    {k}.{v} = {settings_dict[k][v]}")
        click.echo()


@config_group.command("restore")
def reset_settings():
    """Restore all entries in config.ini to factory settings"""
    click.echo("Are you sure you want to continue? All settings in config.ini will be overwritten [yN] ", nl=False)
    c = click.getchar()
    click.echo()
    if c == "y":
        config.restore_to_default(settings_dict=reset_values)
        click.echo("Settings have been restored to original values")
    else:
        click.echo("Phew! Nothing changed.")


def _exit_invalid_setting(setting):
    click.echo(f"ERROR: '{setting}' is not a valid settings key.")
    click.echo("To see a list of configurable settings:")
    click.echo("  ./toolkit.py config list")
    exit(1)
