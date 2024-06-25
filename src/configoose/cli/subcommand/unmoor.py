from ..util import format_desc, top_package
from ...util.split_preamble import split_preamble
import argparse
from pathlib import Path


def main(command, args):
    """Unmoor a configuration file"""
    parser = argparse.ArgumentParser(
        prog=f"python -m {top_package.__name__} {command}",
        description=format_desc(
            """\
            >Unmoor a configuration in a marina."""
        ),
    )
    parser.add_argument(
        "config",
        help=("system path of configuration file to unmoor"),
        nargs="?",
        metavar="CONFIGFILE",
    )
    parser.add_argument(
        "-a",
        "--address",
        action="store",
        dest="address",
        required=False,
        help="mooring address if needed",
    )
    args = parser.parse_args(args)

    # if no address given, extract address from config file
    if not args.address:
        with open(args.config) as ifh:
            args.address = split_preamble(ifh)["address"]

    # remove address from root_db if it exists
    del top_package.root_db[args.address]
