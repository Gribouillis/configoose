from abc import ABC, abstractmethod
import io
from .util.digattr import dig
from .util.split_preamble import split_preamble


class Error(Exception):
    pass


class AbstractConfigurator(ABC):
    """Provide an interface for client programs that use configoose to configurate themselves

    :param address: the abstract address used to find configuration files
    :type address: str
    """

    def __init__(self, address):
        self._protocols = {}
        self.address = address

    @property
    @abstractmethod
    def database(self):
        """The configoose database used by this configurator"""
        ...

    def add_protocol(self, protopath, *args, **kwargs):
        """Declare a configuration protocol honored by the client program

        :param protopath: full dotted path of a :class:`Protocol` class in Python's module system
        :type protopath: str
        :param args: additional arguments stored in the resulting object
        :param kwargs: additional keyword arguments stored in the resulting object
        :return: an :class:`AddedProtocol` instance that has been registered in this configurator instance
        :rtype: AddedProtocol
        """
        ap = AddedProtocol(args, kwargs)
        self._protocols[protopath] = ap
        return ap

    def run(self, missing_ok=False):
        """Concretely executes the configuration action

        :param missing_ok: indicates that an absence of configuration file must be silently ignored. Defaults to False
        :type missing_ok: bool

        By a lookup in the database, the configurator tries to find a configuration
        file corresponding to
        the address given to the constructor. If this succeeds, it reads the
        preamble of the configuration file to extract the protocol. If this protocol has
        been added to the configurator, it instanciates the protocol class
        and calls the protocol's `run()` method, passing it the :class:`AddedProtocol`
        instance, the preamble and the remaining text of the configuration file.
        """
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
        dig(*preamble["protopath"].split("."))().run(ap, preamble, text, mediator)


class AddedProtocol:
    """Object returned by configurators :func:`add_protocol` and passed to :func:`Protocol.run` methods.

    :param args: additional tuple of arguments
    :param kwargs: additional dict of arguments
    """

    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, func):
        """Use self as a decorator to register a handler function

        :param func: callable
        :type func: Callable
        :return: the function passed as argument unchanged

        The effect of the call is to add a pair `('handler', func)` to the kwarg
        dict stored in the instance. This enables protocols `run()` method to
        call the handler method because this instance is passed to these methods.
        """
        self.kwargs["handler"] = func
        return func
