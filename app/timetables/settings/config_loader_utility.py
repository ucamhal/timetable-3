"""
This module contains code used in the project's settings files.
"""
import ConfigParser


# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.
from django.core.exceptions import ImproperlyConfigured


def load_external_config(config_path):
    """
    Load an .ini file at config_path.

    Returns:
        A ConfigParser like object (actually a ExternalConfigWrapper).
    Raises:
        ImproperlyConfigured: On any error, including methods called on
            returned object.
    """
    config = ConfigParser.RawConfigParser()

    # Read the config file
    try:
        with open(config_path) as config_file:
            try:
                config.readfp(config_file)
            except ConfigParser.Error as err:
                msg = "Error parsing external config file '%s'.\n %s" % (
                    config_path, err.message)
                raise ImproperlyConfigured(msg)
    except IOError as err:
        msg = "Unable to open external config file: '%s'.\n %s" % (
            config_path, err.message)
        raise ImproperlyConfigured(msg)

    return ExternalConfigWrapper(config, config_path)


class ExternalConfigWrapper(object):
    """
    A wrapper for RawConfigParser which catches any errors it raises and
    instead raises ImproperlyConfigured.
    """

    def __init__(self, config, filename):
        assert isinstance(config, ConfigParser.RawConfigParser)
        self.config_path = filename
        self.config = config

    def trap_config_error(self, func):
        try:
            return func()
        except ConfigParser.Error as err:
            msg = "Error reading value from config file: '%s'.\n %s" % (
                self.config_path, err.message)
            raise ImproperlyConfigured(msg)

    def get(self, section, option):
        return self.trap_config_error(
            lambda: self.config.get(section, option)
        )

    def getint(self, section, option):
        return self.trap_config_error(
            lambda: self.config.getint(section, option)
        )

    def getfloat(self, section, option):
        return self.trap_config_error(
            lambda: self.config.getfloat(section, option)
        )

    def getboolean(self, section, option):
        return self.trap_config_error(
            lambda: self.config.getboolean(section, option)
        )

    def items(self, section):
        return self.trap_config_error(
            lambda: self.config.items(section)
        )

    def sections(self, section):
        return self.trap_config_error(
            lambda: self.config.sections(section)
        )
