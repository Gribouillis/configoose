from . import abc
import sys


class Error(Exception):
    pass


class Protocol(abc.Protocol):
    """The :emphasis:`methodic` protocol, a type of Python configuration

    The methodic protocol expects a Python configuration file containing
    a `configure()` function with a simple `handler` argument. A handler
    instance is created by calling the handler function (or class)
    registered by the configurator, with arguments

    * The :class:`AddedProtocol` instance given by the configurator
    * The :class:`Preamble` extracted from the configuration file

    The configuration text is executed by Python and the `configure()`
    function is called. It is the responsibility of the configuration file
    to call methods of the handler object in its `configure()` function.

    The configoose module itself is configured with the methodic protocol,
    thus the contents of the `configooseconf` module is an example of
    how to configure a file with this protocol.
    """

    def run(self, ap, preamble, text):
        from types import ModuleType

        mod = ModuleType(f"{__name__}.mooring.{preamble['address']}")
        sys.modules[mod.__name__] = mod
        try:
            exec(text, vars(mod))
            if handler := ap.kwargs.get("handler", None):
                h = handler(ap, preamble)
                try:
                    mod.configure(h)
                except Exception as exc:
                    raise Error(text) from exc
        finally:
            # Forget configuration module
            del sys.modules[mod.__name__]

    @classmethod
    def template_text(cls):
        return """
def configure(handler):
    pass
"""
