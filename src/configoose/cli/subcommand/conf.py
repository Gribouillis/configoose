from ..util import format_desc, top_package
import argparse
from pathlib import Path
import site

top_name = top_package.__name__


def main(command, args):
    f"""Create file {top_name}conf.py or user{top_name}conf.py"""
    parser = argparse.ArgumentParser(
        prog=f"python -m {top_name} {command}",
        description=format_desc(
            f"""\
            >Create file {top_name}conf.py or user{top_name}conf.py"""
        ),
    )
    parser.add_argument(
        "-u",
        "--user",
        help="create user configuration file",
        action="store_true",
        dest="user",
    )
    parser.add_argument(
        "-m",
        "--marina",
        metavar="MARINADIR",
        dest="marina",
        help="directory to use as initial marina",
        required=True,
    )
    parser.add_argument(
        "-d",
        "--dest",
        metavar="DESTDIR",
        dest="destdir",
        help=(
            "directory on the python path to write the python module,"
            " if value is - the module is written to stdout."
            " If omitted, module is written to site-packages directory,"
            " user or global depending on the --global option."
        ),
        nargs="?",
    )

    args = parser.parse_args(args)
    args.user = "user" if args.user else ""
    marina = Path(args.marina).resolve()
    rootname = f"{args.user}{top_name}conf"
    address = f"{rootname}-address"
    code = template.format(
        tag={"initial", "user"} if args.user else {"initial"},
        top_name=top_name,
        marina=str(marina),
        address=address,
        rootname=rootname,
    )

    if args.destdir == "-":
        print(code)
    else:
        if not args.destdir:
            args.destdir = (
                site.getusersitepackages() if args.user else site.getsitepackages()[0]
            )
        dest = Path(args.destdir) / f"{rootname}.py"
        if dest.exists():
            raise RuntimeError(f"Cannot create {dest}: file exists")
        else:
            dest.write_text(code)


template = '''\
{{
    "address": "{address}",
    'protopath': "{top_name}.protocol.methodic.Protocol",
}}
__doc__ = """{rootname}.py

This is {top_name}'s root database configuration module.
The basic configuration is to add marinas, usually OS directories,
where configuration mediators can be stored.
"""

def configure(handler):
    handler.add_marina(
        path={marina!r},
        style="os-directory",
        tags={tag!r},
    )
'''
