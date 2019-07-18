import logging
import os

import rifle.checker as checker
import rifle.utils as utils
from rifle.errors import ValidationError


def main():
    '''
        Entry point for rifle.
    '''
    # Set up the parser
    parser = utils.crisp_cmdline_args()
    args = parser.parse_args()

    # Set up the logger
    utils.setup_logging(args.verbose)
    logger = logging.getLogger()
    logger.handlers = []
    ch = logging.StreamHandler()
    ch.setFormatter(utils.ColoredFormatter())
    logger.addHandler(ch)
    fh = logging.FileHandler('run.log', 'w')
    logger.addHandler(fh)

    try:
        checker.check_specs(os.path.abspath(args.isa_spec),
                            os.path.abspath(args.platform_spec))
    except ValidationError as msg:
        logger.error(msg)
        return 1


if __name__ == "__main__":
    exit(main())
