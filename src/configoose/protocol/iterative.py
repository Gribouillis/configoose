from . import abc
import sys


class Protocol(abc.Protocol):
    def run(self, ap, preamble, text):
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
