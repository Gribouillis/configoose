from . import abc
from configparser import ConfigParser


class Protocol(abc.Protocol):
    """Protocol to handle configurations in Python's configparser format

    Running this protocol creates a ConfigParser instance that parses
    the configuration text, then it calls a handler method if the client
    code has registered one. It passes three arguments to the handler method:

    * the :class:`AddedProtocol` instance that was registered by the configurator
    * the :class:`Preamble` extracted from the configuration file
    * the :class:`ConfigParser` instance used to parse the configuration.
    """

    def run(self, ap, preamble, text, med):
        parser = ConfigParser()
        parser.read_string(text)
        if handler := ap.kwargs.get("handler", None):
            handler(ap, preamble, parser)

    @classmethod
    def template_text(cls):
        return "[section]\n"
