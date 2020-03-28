import logging
import os
import sys
import shutil
from riscv_config import __version__ as version
import riscv_config.checker as checker
import riscv_config.utils as utils
from riscv_config.errors import ValidationError


def main():
    '''
        Entry point for riscv_config.
    '''
    # Set up the parser
    parser = utils.riscv_config_cmdline_args()
    args = parser.parse_args()
    if len(sys.argv) < 2:
        parser.print_help()
        raise SystemExit
    if (args.version):
        print('RISCV-CONFIG: RISC-V Configuration Validator')
        print('Version: ' + version)
        return 0

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

    try:
        checker.check_specs(os.path.abspath(args.isa_spec),
                            os.path.abspath(args.platform_spec), work_dir, True)
    except ValidationError as msg:
        logger.error(str(msg))
        return 1


if __name__ == "__main__":
    exit(main())
