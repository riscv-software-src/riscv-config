import logging
import argparse
import operator

import ruamel
from ruamel.yaml import YAML

yaml = YAML(typ="rt")
yaml.default_flow_style = False
yaml.allow_unicode = True


def load_yaml(foo):
    try:
        with open(foo, "r") as file:
            return yaml.load(file)
    except ruamel.yaml.constructor.DuplicateKeyError as msg:
        logger = logging.getLogger(__name__)
        error = "\n".join(str(msg).split("\n")[2:-7])
        logger.error(error)
        raise SystemExit


class ColoredFormatter(logging.Formatter):
    """                                                                         
        Class to create a log output which is colored based on level.           
    """

    def __init__(self, *args, **kwargs):
        super(ColoredFormatter, self).__init__(*args, **kwargs)
        self.colors = {
            'DEBUG': '\033[94m',
            'INFO': '\033[92m',
            'WARNING': '\033[93m',
            'ERROR': '\033[91m',
        }

        self.reset = '\033[0m'

    def format(self, record):
        msg = str(record.msg)
        level_name = str(record.levelname)
        name = str(record.name)
        color_prefix = self.colors[level_name]
        return '{0}{1:<9s} : {2}{3}'.format(color_prefix,
                                            '[' + level_name + ']', msg,
                                            self.reset)


def setup_logging(log_level):
    """Setup logging                                                            
                                                                                
        Verbosity decided on user input                                         
                                                                                                                                                   
        :param log_level: User defined log level                             
                                                                                
        :type log_level: str                                                               
    """
    numeric_level = getattr(logging, log_level.upper(), None)

    if not isinstance(numeric_level, int):
        print(
            "\033[91mInvalid log level passed. Please select from debug | info | warning | error\033[0m"
        )
        raise ValueError("{}-Invalid log level.".format(log_level))

    logging.basicConfig(level=numeric_level)


class SortingHelpFormatter(argparse.HelpFormatter):

    def add_arguments(self, actions):
        actions = sorted(actions, key=operator.attrgetter('option_strings'))
        super(SortingHelpFormatter, self).add_arguments(actions)


def rifle_cmdline_args():
    parser = argparse.ArgumentParser(formatter_class=SortingHelpFormatter,
                                     prog="rifle",
                                     description="RISC-V Feature Legalizer")
    parser.add_argument('--isa_spec',
                        '-ispec',
                        type=str,
                        metavar='YAML',
                        help='The YAML which contains the ISA specs.',
                        required=True)
    parser.add_argument('--platform_spec',
                        '-pspec',
                        type=str,
                        metavar='YAML',
                        help='The YAML which contains the Platfrorm specs.',
                        required=True),
    parser.add_argument(
        '--work_dir',
        type=str,
        default="rifle_work",
        metavar='DIR',
        help='The name of the work dir to dump the output files to.'),
    parser.add_argument('--verbose',
                        action='store',
                        default='info',
                        help='debug | info | warning | error',
                        metavar="")
    return parser
