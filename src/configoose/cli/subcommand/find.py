from ..util import edit_file, top_package
import argparse
from pathlib import Path
import sys


def main(command, args):
    """Find configuration file"""

    parser = argparse.ArgumentParser(
        prog=f"python -m {top_package.__name__} {command}",
        description=("Find a configuration from an address"),
    )

    parser.add_argument(
        "address", help="Abstract address of configuration", metavar="ADDRESS"
    )

    parser.add_argument(
        "-e",
        "--edit",
        help="Launch editor if file found",
        dest="edit",
        action="store_true",
    )

    args = parser.parse_args(args)

    mediator = top_package.root_db[args.address]
    print(mediator)

    if args.edit and (p := mediator.system_path()):
        edit_file(p)
