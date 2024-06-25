from . import abc
from configparser import ConfigParser


class Protocol(abc.Protocol):
    def run(self, ap, preamble, text):
        parser = ConfigParser()
        parser.read_string(text)
        if handler := ap.kwargs.get("handler", None):
            handler(ap, preamble, parser)

    @classmethod
    def template_text(cls):
        return "[section]\n"
