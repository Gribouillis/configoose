from abc import ABC, abstractmethod
import io
from .util.digattr import dig
from .util.split_preamble import split_preamble


class Error(Exception):
    pass


class AbstractConfigurator(ABC):
    def __init__(self, address):
        self._protocols = {}
        self.address = address

    @property
    @abstractmethod
    def database(self):
        ...

    def add_protocol(self, protopath, *args, **kwargs):
        ap = AddedProtocol(args, kwargs)
        self._protocols[protopath] = ap
        return ap

    def run(self, missing_ok=False):
        try:
            mediator = self.database[self.address]
        except KeyError:
            if missing_ok:
                return
            else:
                raise Error("Missing configuration for address", self.address)
        f = io.StringIO(mediator.read_text())
        preamble = split_preamble(f)
        text = f.read()
        try:
            ap = self._protocols[preamble["protopath"]]
        except KeyError:
            if missing_ok:
                return
            else:
                raise
        dig(*preamble["protopath"].split("."))().run(ap, preamble, text)


class AddedProtocol:
    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, func):
        """Use self as a decorator"""
        self.kwargs["handler"] = func
        return func
