from abc import abstractmethod, ABC
from collections import deque
from collections.abc import Mapping, MutableMapping
from importlib import import_module
import marshmallow as ms
import os
from pathlib import Path
from reprlib import recursive_repr as _recursive_repr


class Db(Mapping):
    """Groups multiple marinas to create a single view.

    Conceptually similar to a collections.ChainMap, but
    uses Marina instances intead of dicts.

    The underlying marinas are stored in a list. That list
    is public and can be accessed or updated using the
    *path* attribute. There is no other state.

    Lookups search the underlying marinas successively
    until a key is found.
    """

    # Implementation largely inspired from ChainMap.
    def __init__(self, *marinas):
        self.path = list(marinas)

    def __missing__(self, key):
        raise KeyError(key)

    def __getitem__(self, key):
        for marina in self.path:
            try:
                s = marina[key]  # can't use 'key in mapping' with defaultdict
            except KeyError:
                pass
            else:
                return mediator_loads(s)
        return self.__missing__(key)  # support subclasses that define __missing__

    def get(self, key, default=None):
        return self[key] if key in self else default

    def __len__(self):
        return len(set().union(*self.path))

    def __iter__(self):
        d = {}
        for marina in reversed(self.path):
            d.update(dict.fromkeys(marina))
        return iter(d)

    def __contains__(self, key):
        return any(key in m for m in self.path)

    def __bool__(self):
        return any(self.path)

    @_recursive_repr()
    def __repr__(self):
        return f'{self.__class__.__name__}({", ".join(map(repr, self.path))})'

    def __delitem__(self, key):
        """Deletion (missing is OK)"""
        for marina in self.path:
            try:
                del marina[key]
            except KeyError:
                pass

    # updates and deletions currently left unimplemented
    __setitem__ = None
    popitem = None
    pop = None
    clear = None
    __ior__ = None
    __or__ = None
    __ror__ = None


class Marina(MutableMapping):
    """Base class for marinas"""

    __eq__ = object.__eq__
    __ne__ = object.__ne__
    __hash__ = object.__hash__

    def __init__(self, tags=()):
        self.tags = set(tags)

    def __repr__(self):
        return f"<{type(self).__name__}(tags={self.tags!r})>"

    def is_valid_key(self, key, keyerror=False):
        return True


class MarinaDict(dict, Marina):
    """Marina built on a dict instance"""

    def __init__(self, tags=()):
        Marina.__init__(self, tags=tags)

    __eq__ = object.__eq__
    __ne__ = object.__ne__
    __hash__ = object.__hash__
    __init__ = Marina.__init__
    __repr__ = Marina.__repr__


class MarinaDirInOs(Marina):
    def __init__(self, path, tags=()):
        if not isinstance(path, Path):
            raise TypeError("Expected pathlib.Path instance, got", repr(path))
        super().__init__(tags=tags)
        self.path = path

    def __repr__(self):
        return f"{type(self).__name__}({self.path!r}, tags={self.tags!r})"

    def __iter__(self):
        return iter(next(os.walk(self.path))[2])

    def keys(self):
        return next(os.walk(self.path))[2]

    def __len__(self):
        return ilen(iter(self))

    def __getitem__(self, key):
        self.is_valid_key(key, keyerror=True)
        p = self.path / key
        if p.is_file():
            return p.read_text()
        else:
            raise KeyError(key)

    def __setitem__(self, key, text):
        del self[key]  # does not raise KeyError if missing key
        p = self.path / key
        p.write_text(text)

    def __delitem__(self, key):
        self.is_valid_key(key, keyerror=True)
        p = self.path / key
        p.unlink(missing_ok=True)

    def is_valid_key(self, key, keyerror=False):
        if key == Path(key).name:
            return True
        elif keyerror:
            raise KeyError(key)
        else:
            return False


# mediators are serializable with MediatorSchema
# keep the Mediator interface minimal.
# Concrete subclasses define access to concrete storage
# support.
class Mediator(ABC):
    @abstractmethod
    def read_bytes(self):
        raise NotImplementedError

    def read_text(self, encoding="utf8"):
        return self.read_bytes().decode(encoding)

    @classmethod
    @abstractmethod
    def schema_type(cls):
        ...

    def system_path(self):
        """Return a system path of self if available, else None"""


def mediator_dumps(med):
    return MediatorSchema().dumps(med)


def mediator_loads(s):
    return MediatorSchema().loads(s)


class MediatorSchema(ms.Schema):
    module = ms.fields.Str()
    qualname = ms.fields.Str()
    instance = ms.fields.Dict()

    @ms.pre_dump
    def predump(self, obj, **kwargs):
        tp = type(obj)
        st = tp.schema_type()
        res = {
            "module": tp.__module__,
            "qualname": tp.__qualname__,
            "instance": st().dump(obj),
        }
        return res

    @ms.post_load
    def postload(self, obj, **kwargs):
        tp = import_module(obj["module"])
        for name in obj["qualname"].split("."):
            tp = getattr(tp, name)
        st = tp.schema_type()
        res = st().load(obj["instance"])
        return res


class FileInOsMediator(Mediator):
    def __init__(self, path):
        self.path = Path(path)

    def __repr__(self):
        return f"{type(self).__name__}({self.path!r})"

    def read_bytes(self):
        return self.path.read_bytes()

    def read_text(self):
        return self.path.read_text()

    @classmethod
    def schema_type(cls):
        return FileInOsSchema

    def system_path(self):
        return self.path


class FileInOsSchema(ms.Schema):
    path = ms.fields.Str()

    @ms.post_load
    def postload(self, obj, **kwargs):
        return FileInOsMediator(obj["path"])


def ilen(iterable):
    # taken from more_itertools (MIT)
    counter = count()
    deque(zip(iterable, counter), maxlen=0)
    return next(counter)
