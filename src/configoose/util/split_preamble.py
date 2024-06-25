from .digattr import dig
from ast import literal_eval
import itertools as itt
from token import OP, NL, NEWLINE, COMMENT
from tokenize import generate_tokens


class InvalidPreamble(Exception):
    pass


class Preamble(dict):
    pass


def split_preamble(infile, eval=True):
    readline = infile.readline
    buffer = []

    def rdline():
        if s := readline():
            buffer.append(s)
        return s

    itoken = generate_tokens(rdline)
    diclevel = 0
    for t in itoken:
        if t.type in (COMMENT, NL, NEWLINE):
            continue
        elif t.type == OP and t.string == "{":
            diclevel = 1
            break
        else:
            raise InvalidPreamble("Expected literal dictionary")
    for t in itoken:
        if t.type == OP:
            if t.string == "{":
                diclevel += 1
            elif t.string == "}":
                diclevel -= 1
                if diclevel == 0:
                    break
    else:
        raise InvalidPreamble("Unterminated literal dictionary")
    source_code = "".join(buffer)
    if eval:
        D = literal_eval(source_code)
        return Preamble(
            address=D["address"],
            protopath=D["protopath"],
        )
    else:
        return source_code


if __name__ == "__main__":
    import io

    s = """
    # spam spam spam
    {
        'protopath': 'eggs.spam.ham',
        # some stuff
        'ham': 134,
    }
    patatit patata patato, machin, chose. chouette!
    """

    infile = io.StringIO(s)
    preamble = split_preamble(infile)
    print(infile.read())
    print("-" * 20)
    print(preamble)
