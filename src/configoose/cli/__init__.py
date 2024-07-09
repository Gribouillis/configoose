from .util import format_desc, random_address, top_package
from ..util.algorithm import algorithm
from ..util.digattr import dig
from ..util.dispatcher import PolymorphicDispatcher
import argparse
from functools import wraps
from importlib import import_module
from pathlib import Path


class main(algorithm):
    # dispatcher to add subcommands.
    # Add subcommand with: main.subcommand[name] = callable
    # callable signature is Callable(command: str, args: List[str]) -> Any
    """Implementation of configoose's command line interface. Here is its main
    usage string

    .. code-block:: text

        usage: python -m configoose [-h] [COMMAND]

        Run various commands relative to configoose.

        positional arguments:
        COMMAND     Subcommand to run. Use COMMAND -h for details

        options:
        -h, --help  Print this help to standard output and exit

        Available commands:

        conf                 Create file `configooseconf.py` or `userconfigooseconf.py`
        find                 Find configuration file
        marina-list          Display a list of known marinas
        moor                 Moor a configuration file in a marina
        random-address       Generate a random address
        template             Create a template configuration file for a given protocol
        unmoor               Unmoor a configuration file
        version              Print program's version

    """
    subcommand = PolymorphicDispatcher()

    def run(self, args):
        parser = self.parser = argparse.ArgumentParser(
            prog=f"python -m {top_package.__name__}",
            description=format_desc(
                f"""\
            >Run various commands relative to {top_package.__name__}.

            """
            ),
            formatter_class=argparse.RawTextHelpFormatter,
            add_help=False,
        )
        parser.add_argument(
            "-h",
            "--help",
            action="store_true",
            help="Print this help to standard output and exit",
            dest="help",
        )
        parser.add_argument(
            "command",
            help="Subcommand to run. Use COMMAND -h for details",
            metavar="COMMAND",
            default="",
            nargs="?",
        )
        # parse_args defaults to argv[1:] for args, but we need to
        # exclude the rest of the args too, or validation will fail
        ns = parser.parse_args(args[0:1])
        if ns.help or not ns.command:
            self.print_help(parser)
            return
        command = ns.command

        try:
            # see if the command is registered in the dispatcher
            callback = self.subcommand[command]
        except KeyError:
            try:
                # try to import callback from package main.subcommand
                name = command.replace("-", "_")
                mod = import_module(f"{top_package.__name__}.cli.subcommand.{name}")
                callback = mod.main
            except Exception:
                print(f"Unrecognized command {command!r}", end="\n\n")
                self.print_help(parser)
                return

        callback(command, args[1:])

    def print_help(self, parser):
        L = [parser.format_help()]
        L.append("\nAvailable commands:\n\n")
        L.extend(gather_command())
        print("".join(L))


def gather_command():
    """Function used internally to gather implemented subcommands"""
    # list to gather pairs (command_name: str, short_description: str)
    gathering = []

    def get_short_desc(callback):
        # for each command, its short description is the first
        # line of its callback's docstring if available.
        return (callback.__doc__ or "").split("\n", 1)[0]

    # Gather commands defined with the @main.subcommand(command) decorator
    for name, callback in main.subcommand.items():
        gathering.append((name, get_short_desc(callback)))
    from pkgutil import iter_modules
    from . import subcommand

    # Gather commands defined as main() function in a submodule of
    # f'{top_package.__name__}.cli.subcommand'. Submodules without a .main
    # attribute are not listed. The command's name is the submodule's
    # name where underscores '_' are replaced by dash '-'.
    for mod_info in iter_modules(subcommand.__path__):
        mod = import_module(f".{mod_info.name}", subcommand.__name__)
        name = mod_info.name.replace("_", "-")
        if callback := getattr(mod, "main", None):
            gathering.append((name, get_short_desc(callback)))
    gathering.sort()
    for name, short_desc in gathering:
        yield (f"   {name:<21}{short_desc}\n")


"""
# Exemple pour implémenter une sous commande

@main.subcommand('spam')
def run(command, args):
    "does nothing useful"
    print(f'{command.capitalize()}! {args!r}')

# autre solution: créer cli/subcommand/spam.py
# et mettre une fonction main(command, args) dedans.
"""


@main.subcommand("marina-list")
def marina_list_(command, args):
    """Display a list of known marinas

    Implementation of the `marina-list` subcommand.
    Its usage string is

    .. code-block:: text

        usage: python -m configoose marina-list [-h]

        Display a list of known marinas

        options:
        -h, --help  show this help message and exit

    """
    parser = argparse.ArgumentParser(
        prog=f"python -m {top_package.__name__} {command}",
        description=format_desc(
            """\
        >Display a list of known marinas"""
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.parse_args(args)

    for marina in top_package.root_db.path:
        print(marina)


@main.subcommand("random-address")
def random_address_(command, args):
    """Generate a random address

    Implementation of the `random-address` subcommand which usage
    string is

    .. code-block:: text

        usage: python -m configoose random-address [-h]

        Generate a random address

        options:
        -h, --help  show this help message and exit

    """
    parser = argparse.ArgumentParser(
        prog=f"python -m {top_package.__name__} {command}",
        description=format_desc(
            """\
        >Generate a random address"""
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.parse_args(args)
    print(repr(random_address()))


@main.subcommand("template")
def template_(command, args):
    """Print a template configuration for a protocol

    Implementation of the `template` subcommand
    which usage string is

    .. code-block:: text

        usage: python -m configoose template [-h] [-a ADDRESS] [-o [OUTFILE]] PROTOCOL

        Print a template configuration for a protocol

        positional arguments:
        PROTOCOL

        options:
        -h, --help            show this help message and exit
        -a ADDRESS, --address ADDRESS
                                configuration address, defaults to random
        -o [OUTFILE], --output [OUTFILE]
                                destination file. If not given or equal to '-', print to stdout

    """
    parser = argparse.ArgumentParser(
        prog=f"python -m {top_package.__name__} {command}",
        description=format_desc(
            """\
        >Print a template configuration for a protocol"""
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-a",
        "--address",
        dest="address",
        default="",
        metavar="ADDRESS",
        help="configuration address, defaults to random",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        metavar="OUTFILE",
        help="destination file. If not given or equal to '-', print to stdout",
        nargs="?",
        default="",
    )
    parser.add_argument("protocol", metavar="PROTOCOL")
    ns = parser.parse_args(args)
    if not ns.address:
        ns.address = random_address()
    preamble = f"""{{
    "address" : "{ns.address}",
    "protopath" : "{ns.protocol}",
}}
"""
    protoclass = dig(*ns.protocol.split("."))
    text = preamble + protoclass.template_text()
    if ns.output and ns.output != "-":
        Path(ns.output).write_text(text)
    else:
        print(text, end="")


@main.subcommand("version")
def version_(command, args):
    """Print the package version

    Implementation of the `version` subcommand which usage string is

    .. code-block:: text

        usage: python -m configoose version [-h]

        Print the package version

        options:
        -h, --help  show this help message and exit

    """
    parser = argparse.ArgumentParser(
        prog=f"python -m {top_package.__name__} {command}",
        description=format_desc(
            """\
        >Print the package version"""
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.parse_args(args)
    print(top_package.__version__)
