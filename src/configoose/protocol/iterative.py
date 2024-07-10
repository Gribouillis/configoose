from . import abc
import sys


class Protocol(abc.Protocol):
    """The :emphasis:`iterative` protocol is an experimental configuration protocol

    Like the methodic protocol, it is based on configuration files containing Python code.
    These configuration files must define a generator function named iconfigure()
    which generates a sequence of :emphasis:`configuration items`, such as small dictionaries
    for exemple. For each item, the protocol calls the handler function provided by
    client code with three arguments

    * The :class:`AddedProtocol` instance given by the configurator.
    * The :class:`Preamble` extracted from the configuration file
    * The generated configuration item.
    """

    def run(self, ap, preamble, text, med):
        from types import ModuleType

        mod = ModuleType(f"{__name__}.mooring.{preamble['address']}")
        sys.modules[mod.__name__] = mod
        try:
            exec(text, vars(mod))
            if handler := ap.kwargs.get("handler", None):
                for item in mod.iconfigure():
                    handler(ap, preamble, item)
        finally:
            # Forget configuration module
            del sys.modules[mod.__name__]

    @classmethod
    def template_text(cls):
        return """
def iconfigure():
    if False:
        yield {}
"""
