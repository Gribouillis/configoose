from importlib import import_module
from inspect import ismodule

_raise_error = object()
_sentinel = object()


def digattr(obj, *iattr, default=_raise_error):
    head = obj
    for attr in iattr:
        v = _digattr(head, attr)
        if v is _raise_error:
            if default is _raise_error:
                raise AttributeError(head, "has no attribute", attr)
            else:
                return default
        else:
            head = v
    return head


def _digattr(obj, attr):
    v = getattr(obj, attr, _raise_error)
    if v is _raise_error and ismodule(obj) and hasattr(obj, "__path__"):
        try:
            v = import_module(f"{obj.__name__}.{attr}")
        except ImportError:
            pass
    return v


def dig(name, *iattr, default=_raise_error):
    obj = getattr(__builtins__, name, _sentinel)
    if obj is _sentinel:
        try:
            obj = import_module(name)
        except ImportError:
            if default is _raise_error:
                raise
            return default
    return digattr(obj, *iattr, default=default)
