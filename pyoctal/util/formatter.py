import logging
import argparse
import sys

class Colours:
    cyan = "\x1b[34m"
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    orange = "\x1b[38;5;214m"
    red = "\x1b[38;5;202m"
    reset = "\x1b[0m"
    end = '\033[0m'
    italic = '\033[3m'
    bold = '\033[1m'
    underline = '\033[4m'

class CustomLogFileFormatter(logging.Formatter):
    """ Format the logging output to the log file to display extra information. """

    fmat = "%(asctime)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: Colours.cyan + fmat + Colours.reset,
        logging.INFO: Colours.grey + fmat + Colours.reset,
        logging.WARNING: Colours.yellow + fmat + Colours.reset,
        logging.ERROR: Colours.orange + fmat + Colours.reset,
        logging.CRITICAL: Colours.red + fmat + Colours.reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%d-%m-%Y %H:%M:%S')
        return formatter.format(record)

class CustomLogConsoleFormatter(logging.Formatter):
    """ Get a colourful terminal output for different logging level. """

    fmat = "%(message)s"
 
    FORMATS = {
        logging.DEBUG: Colours.cyan + fmat + Colours.reset,
        logging.INFO: Colours.grey + fmat + Colours.reset,
        logging.WARNING: Colours.yellow + fmat + Colours.reset,
        logging.ERROR: Colours.orange + fmat + Colours.reset,
        logging.CRITICAL: Colours.red + fmat + Colours.reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class CustomArgparseFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    """ Display default values in the helper message. """

    def _get_help_string(self, action):
        help_msg = action.help
        if '%(default)' not in action.help:
            if action.default is not argparse.SUPPRESS:
                defaulting_nargs = [argparse.OPTIONAL, argparse.ZERO_OR_MORE]
                if action.option_strings or action.nargs in defaulting_nargs:
                    if isinstance(action.default, type(sys.stdin)):
                        help_msg += ' [default: ' + str(action.default.name) + ']'
                    elif isinstance(action.default, bool):
                        help_msg += ' [default: ' + str(action.default) + ']'
                    elif isinstance(action.default, str):
                        help_msg += ' [default: ' + str(action.default) + ']'
                    elif action.default is not None:
                        help_msg += f' [default: {", ".join(map(str, action.default))}]'
        return help_msg
