from ...database import FileInOsMediator, mediator_dumps
from ..util import format_desc, top_package
from ...util.split_preamble import split_preamble
import argparse
from pathlib import Path


class TagNotFoundError(Exception):
    pass


def main(command, args):
    """Moor a configuration file in a marina

    Implementation of the :code:`moor` subcommand which usage string is

    .. code-block:: text

        usage: python -m configoose moor [-h] [-a ADDRESS] MARINA CONFIGFILE

        Moor a configuration file in a marina.

        positional arguments:
        MARINA                tag of target marina
        CONFIGFILE            system path of configuration file to moor

        options:
        -h, --help            show this help message and exit
        -a ADDRESS, --address ADDRESS
                                abstract address if needed. If not given, the address is extracted
                                from the configuration file

    """
    parser = argparse.ArgumentParser(
        prog=f"python -m {top_package.__name__} {command}",
        description=format_desc(
            """\
            >Moor a configuration file in a marina."""
        ),
    )
    parser.add_argument(
        "tag",
        help="tag of target marina",
        metavar="MARINA",
    )
    parser.add_argument(
        "config",
        help=("system path of configuration file to moor"),
        metavar="CONFIGFILE",
    )
    parser.add_argument(
        "-a",
        "--address",
        action="store",
        dest="address",
        required=False,
        help="abstract address if needed. If not given, the address is extracted from the configuration file",
    )
    args = parser.parse_args(args)
    # find first marina with the given tag, err if no marina.
    for marina in top_package.root_db.path:
        if args.tag in marina.tags:
            break
    else:
        raise TagNotFoundError("No marina with tag", args.tag)

    # if no address given, extract address from config file
    if not args.address:
        with open(args.config) as ifh:
            args.address = split_preamble(ifh)["address"]

    # create mediator for given file or extract it from db
    if args.config:
        mediator = FileInOsMediator(Path(args.config).resolve())
    else:
        mediator = top_package.root_db[args.address]

    # remove address from root_db if it exists
    del top_package.root_db[args.address]

    # store mediator in marina
    marina[args.address] = mediator_dumps(mediator)
