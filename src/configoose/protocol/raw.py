from . import abc


class Protocol(abc.Protocol):
    """Protocol to handle configurations in raw format

    Running this protocol calls a handler method if the client
    code has registered one. The arguments passed to the handler method are

    * the :class:`AddedProtocol` instance that was registered by the configurator
    * the :class:`Preamble` extracted from the configuration file
    * the text contained in the configuration
    * the :class:`Mediator` instance used to access the configuration
    """

    def run(self, ap, preamble, text, med):
        if handler := ap.kwargs.get("handler", None):
            handler(ap, preamble, text, med)
