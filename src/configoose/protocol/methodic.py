from . import abc
import sys


class Error(Exception):
    pass


class Protocol(abc.Protocol):
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
