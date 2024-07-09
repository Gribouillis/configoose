from abc import abstractmethod, ABC
from collections import deque
from collections.abc import Mapping, MutableMapping
from importlib import import_module
import marshmallow as ms
import os
from pathlib import Path
from reprlib import recursive_repr as _recursive_repr


# mediators are serializable with MediatorSchema
# keep the Mediator interface minimal.
# Concrete subclasses define access to concrete storage
# support.
class Mediator(ABC):
    """This is the base class of mediator objects which
    can be seen as smart pointers giving access to
    configuration content. Mediators have two main features:

    * They give access to configuration content through their
      :func:`read_text` or :func:`read_bytes` methods.
    * They can be serialized to strings that are stored
      as values in :class:`Marina` mappings.

    Subclasses of :class:`Mediator` implement concrete
    access to configuration content in specific storage.
    """

    @abstractmethod
    def read_bytes(self) -> bytes:
        """Read configuration content as bytes"""
        ...

    def read_text(self, encoding: str = "utf8") -> str:
        """Read configuration content as a unicode string.
        The default implementation uses :func:`read_bytes`

        :param encoding: unicode encoding, defaults to utf8
        :type encoding: str
        """
        return self.read_bytes().decode(encoding)

    @classmethod
    @abstractmethod
    def schema_type(cls):
        """This required classmethod returns a subclass of :class:`marshmallow.Schema`
        which is used to serialize instances of this class.

        Instances of :class:`Mediator` are serialized to be stored as values
        in :class:`Marina` objects and deserialized during lookups in
        :class:`Db` objects.
        """
        ...

    def system_path(self):
        """Return a system path of this mediator if available, else None"""


class Db(Mapping[str, Mediator]):
    """The :class:`Db` class is the type of :mod:`configoose`'s
    main database. It maps abstract configuration addresses (strings)
    to mediators giving access to configuration content.

    It is built upon a sequence of marinas, creating a
    single view of this sequence.

    The underlying marinas are stored in a list. That list
    is public and can be accessed or updated using the
    *path* attribute. There is no other state.

    Lookups search the underlying marinas successively
    until a key is found. This is conceptually similar
    to a collections.ChainMap except that the values
    found are deserialized before return: lookups return
    Mediator instances instead of serialized mediators
    which are stored into marinas.
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


class Marina(MutableMapping[str, str]):
    """This is the base class of marina objects. They
    are mutable mappings that map strings to strings.
    They are used to associate abstract configuration
    addresses to serialized :class:`Mediator` instances.

    :param tags: A set of strings used to identify marinas
    """

    __eq__ = object.__eq__
    __ne__ = object.__ne__
    __hash__ = object.__hash__

    def __init__(self, tags=()):
        self.tags = set(tags)

    def __repr__(self):
        return f"<{type(self).__name__}(tags={self.tags!r})>"

    def is_valid_key(self, key: str, keyerror: bool = False) -> bool:
        """Indicates whether a given key is valid for this marina type.

        :param key: a configuration address
        :type key: str
        :param keyerror: if set, the function raises `KeyError`
          for invalid keys instead of returning `False`. Defaults
          to `False` (don't raise `KeyError`)
        :type keyerror: bool
        :return: a boolean indicating if the key is valid
        :rtype: bool

        In the base class :class:`Marina`, this function always returns `True`
        but concrete subclasses may whish to exclude some keys.
        """
        return True


class MarinaDict(dict, Marina):
    """Subclass of :class:`Marina` built on a dict instance. As these marinas
    are not persistent, they can only be used temporarily
    in a single process.

    :param tags: A set of strings used to identify marinas
    """

    def __init__(self, tags=()):
        Marina.__init__(self, tags=tags)

    __eq__ = object.__eq__
    __ne__ = object.__ne__
    __hash__ = object.__hash__
    __init__ = Marina.__init__
    __repr__ = Marina.__repr__


class MarinaDirInOs(Marina):
    """Subclass of :class:`Marina` built on a file system directory.
    Pairs `(key, value)` are stored in the directory as a
    file name and a file content.

    As a consequence, not every key is allowed in such a marina,
    for example `spam/ham` is not a valid filename in a directory
    in Linux, but `spam-ham` is.

    :param path: The path to the underlying directory
    :type path: `pathlib.Path`
    :param tags: A set of strings used to identify marinas
    """

    def __init__(self, path: Path, tags=()):
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


def mediator_dumps(med: Mediator) -> str:
    """Serialize a mediator as a string"""
    return MediatorSchema().dumps(med)


def mediator_loads(s: str) -> Mediator:
    """Deserialize a string as a mediator"""
    return MediatorSchema().loads(s)


class MediatorSchema(ms.Schema):
    """A subclass of `marshmallow.Schema` used internally
    to serialize all instances of :class:`Mediator`.

    Don't use this class directly. Use instead the functions
    :func:`mediator_dumps` and :func:`mediator_loads`
    """

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
    """A class of mediators pointing to configuration files
    stored as regular files in the file system.

    :param path: the path to the underlying file
    """

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
        """Return the path to the underlying file of this mediator"""
        return self.path


class FileInOsSchema(ms.Schema):
    """A subclass of `marshmallow.Schema` used to
    serialized instances of :class:`FileInOsMediator`
    """

    path = ms.fields.Str()

    @ms.post_load
    def postload(self, obj, **kwargs):
        return FileInOsMediator(obj["path"])


def ilen(iterable):
    """Utility function returning the length of an iterable"""
    # taken from more_itertools (MIT)
    counter = count()
    deque(zip(iterable, counter), maxlen=0)
    return next(counter)
