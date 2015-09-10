"""
### PyLCONF.validator

#### Overview

This module is used by the PyLCONF validation script: `pylconfsd-validate`

```bash
pylconfsd-validate path-to-first.lconfsd path-to-second.lconfsd
```
"""
import argparse
from argparse import RawDescriptionHelpFormatter
from sys import exit as sys_exit

from PyLCONF.lconf_schema import validate_schemas_from_file


def parse_commandline():
    main_parser = argparse.ArgumentParser(
       description='Validate `LCONF Schema files`',
       formatter_class=RawDescriptionHelpFormatter,
       epilog='''EXAMPLES:
    pylconsdf-validate path-to-first.lconf path-to-second.lconf
    '''
    )

    main_parser.add_argument(
       'in_files',
       nargs='*',
       default=[],
       help='List of files to be validates',
    )

    args = main_parser.parse_args()
    if not args.in_files:
        main_parser.print_help()
        sys_exit()

    return args


def main():
    args = parse_commandline()

    for path_to_lconsd_file in args.in_files:
        validate_schemas_from_file(path_to_lconsd_file)


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
if __name__ == '__main__':
    main()
