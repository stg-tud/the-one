import configparser
import os
from pathlib import Path
from typing import List, Dict

# config.py must be kept in the same directory as config.ini or this setting must get changed:
ini_dir = Path(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = ini_dir / "config.ini"


def _instantiate():
    """
    Prepares every step (initialize and read) to use ConfigParser Class.
    """
    if not CONFIG_PATH.is_file():
        raise FileNotFoundError(f"config.ini not found in {ini_dir}")

    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config


def set_value(section, key, value):
    """
    Changes the value of an entry in config.ini file.

    :param section: string of the section name
    :param key: string of the key that holds the value
    :param value: string of the value that should be inserted
    """
    config = _instantiate()
    config.set(section, key, value)

    # save to file
    with open(CONFIG_PATH, "w") as configfile:
        config.write(configfile)


def get_all_items_in_dict() -> Dict:
    """
    Returns a dict of the complete config.ini contents which can also be fed back into the
    ConfigParser to create a new ini file.
    :returns: dictionary of all sections and items in config.ini
    """
    config = _instantiate()
    return {n: s for n, s in zip(dict(config).keys(), map(dict, dict(config).values()))}


def get_string(section, key):
    """
    Returns the string value of an entry in config.ini file.
    :param section: string of the section name
    :param key: string of the key that holds the value that should be returned
    :returns: string value of the specified entry
    """
    config = _instantiate()
    return config.get(section, key)


def get_int(section, key):
    """
    Returns the integer value of an entry in config.ini file.
    :param section: string of the section name
    :param key: string of the key that holds the value that should be returned
    :returns: integer value of the specified entry
    """
    config = _instantiate()
    return config.getint(section, key)


def get_list(section, key):
    """
    Returns the value of a list-entry in config.ini file.

    :param section: string of the section name
    :param key: string of the key that holds the value that should be returned
    :returns: list[str] of values of the specified entry
    """
    config = _instantiate()
    return list(map(lambda x: x.strip(), config.get(section, key).split(",")))


def get_sections() -> List[str]:
    """
    Returns all sections in config.ini except DEFAULT
    :returns: list[str] of sections in config.ini
    """
    return _instantiate().sections()


def get_section_keys(section):
    """
    Returns the value of all keys of a section in config.ini.
    :param section: string of the section name that has the values that should be returned.
    """
    config = _instantiate()
    for sec in config.sections():
        if sec == section:
            keys = []
            for (key, val) in config.items(sec):
                keys.append(key)
            return sorted(keys)


def restore_to_default(settings_dict):
    """
    Restores all the data in config.ini to the default given values (resets the whole file).
    """
    c = configparser.ConfigParser()
    c.read_dict(settings_dict)
    # save to file
    with open(CONFIG_PATH, "w") as configfile:
        c.write(configfile)


if __name__ == "__main__":
    print("This is a module used internally. If you want to configure the toolkit, please use the command")
    print("    $ python toolkit.py config --help")
    print("for more information")
