from .cli.util import format_desc, random_address, top_package
from .util.algorithm import algorithm
from .util.digattr import dig
from .util.dispatcher import PolymorphicDispatcher
import argparse
from functools import wraps
from importlib import import_module
import sys


def post_process(*ifunc):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            x = func(*args, **kwargs)
            for f in ifunc:
                x = f(x)
            return x

        return wrapper

    return decorator


class main(algorithm):
    # dispatcher to add subcommands.
    # Add subcommand with: main.subcommand[name] = callable
    # callable signature is Callable(command: str, args: List[str]) -> Any
    subcommand = PolymorphicDispatcher()

    def run(self, args):
        parser = self.parser = argparse.ArgumentParser(
            prog=f"python -m {__package__}",
            description=format_desc(
                f"""\
            >Run various commands relative to {__package__}.

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
                mod = import_module(f"{__package__}.cli.subcommand.{name}")
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

    @post_process("\n    ".join)
    def subcommand_summary(self):
        # XXX This is broken because commands in main/subcommands are
        # never reached.
        for command, callback in sorted(self.subcommand.items()):
            line = (callback.__doc__ or "").split("\n", 1)[0]
            yield f"{command}: {line}"


def gather_command():
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
    from .cli import subcommand

    # Gather commands defined as main() function in a submodule of
    # f'{__package__}.cli.subcommand'. Submodules without a .main
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
def _(command, args):
    """Display a list of known marinas"""
    parser = argparse.ArgumentParser(
        prog=f"python -m {__package__} {command}",
        description=format_desc(
            """\
        >Display a list of known marinas"""
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.parse_args(args)
    from . import root_db

    for marina in root_db.path:
        print(marina)


@main.subcommand("random-address")
def _(command, args):
    """Generate a random address"""
    parser = argparse.ArgumentParser(
        prog=f"python -m {__package__} {command}",
        description=format_desc(
            """\
        >Generate a random address"""
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.parse_args(args)
    print(repr(random_address()))


@main.subcommand("template")
def _(command, args):
    """Print a template configuration for a protocol"""
    parser = argparse.ArgumentParser(
        prog=f"python -m {__package__} {command}",
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
    print(preamble + protoclass.template_text(), end="")


@main.subcommand("version")
def _(command, args):
    """Print program's version"""
    print(top_package.__version__)


if __name__ == "__main__":
    main(sys.argv[1:])
