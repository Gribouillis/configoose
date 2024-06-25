import string
import sys

from .. import __name__ as _top_name

top_package = sys.modules[_top_name]


def random_address() -> str:
    """Generate a random address"""
    import random
    import string

    alpha = string.digits + string.ascii_lowercase
    n = random.randrange(2**126, 2**128)
    n, r = divmod(n, 26)
    res = alpha[10 + r]
    while n:
        n, r = divmod(n, 36)
        res += alpha[r]
    return res


def format_desc(s, width=70):
    """Function to format description in argparse arguments

    Usage:
        arparse.ArgumentParser(
            ...
            description = format_desc(...),
            formatter_class=argparse.RawTextHelpFormatter,
            ...
        )"""
    import io
    from textwrap import dedent, fill

    file = io.StringIO(dedent(s))
    output = io.StringIO()
    paragraph = []

    def output_paragraph():
        output.write(fill("".join(paragraph), width=width))
        output.write("\n")
        paragraph[:] = ""

    for line in file:
        if not line.strip():
            if paragraph:
                output_paragraph()
            output.write(line)
        elif paragraph:
            paragraph.append(line)
        elif line.startswith(">"):
            paragraph.append(line[1:])
        else:
            output.write(line)
    if paragraph:
        output_paragraph()
    return output.getvalue()


def edit_file(filename):  # pragma: no cover
    import os
    import shutil
    import subprocess as sp

    filename = str(filename)
    if hasattr(os, "startfile"):
        os.startfile(filename)
    elif shutil.which("xdg-open"):
        sp.Popen(["xdg-open", filename], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    elif sys.platform() == "darwin":
        sp.Popen(["open", filename], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    else:
        pass
