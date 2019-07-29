import logging
import os
import shutil

import rifle.checker as checker
import rifle.utils as utils
from rifle.errors import ValidationError


def main():
    '''
        Entry point for rifle.
    '''
    # Set up the parser
    parser = utils.rifle_cmdline_args()
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

    work_dir = os.path.join(os.getcwd(), args.work_dir)
    if not os.path.exists(work_dir):
        logger.debug('Creating new work directory: ' + work_dir)
        os.mkdir(work_dir)
    else:
        logger.debug('Removing old work directory: ' + work_dir)
        shutil.rmtree(work_dir)
        logger.debug('Creating new work directory: ' + work_dir)
        os.mkdir(work_dir)

    try:
        checker.check_specs(os.path.abspath(args.isa_spec),
                            os.path.abspath(args.platform_spec), work_dir)
    except ValidationError as msg:
        logger.error(msg)
        return 1


if __name__ == "__main__":
    exit(main())
