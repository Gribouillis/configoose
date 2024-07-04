from abc import ABC, abstractmethod


class Protocol(ABC):
    """Abstract base class for protocol classes

    Informally speaking, a protocol is a manner of handling a certain type of
    configuration data, for example configuration in json or toml or ini or
    a python file etc. Client code chooses the protocol that it wants to handle
    its configuration data.

    A protocol class is essentially defined by its `run()` method which takes
    the text of the configuration as argument.

    New protocols can be added by defining new subclasses of :class:`Protocol`.
    In particular, several protocol classes can be defined to handle the same
    configuration data.
    """

    @abstractmethod
    def run(self, address: str, text: str, ap: "AddedProtocol"):  # pragma: no cover
        """Configure a module according to this protocol

        :param address: the abstract address of the configuration
        :param text: the text read from the configuration file (without the preamble)
        :param ap: the :class:`AddedProtocol` instance passed by the configurator. Enables access to
            a handler function defined by the client code.
        """
        ...

    @classmethod
    @abstractmethod
    def template_text(cls):
        """Return a basic template configuration for this protocol (without preamble)

        This is intended to give users a starting point when they write a configuration
        file for this protocol.
        """
        ...
