from abc import ABC, abstractmethod


class Protocol(ABC):
    @abstractmethod
    def run(self, address: str, text: str, ap: "AddedProtocol"):  # pragma: no cover
        """Configure a module from a Source"""
        ...

    @classmethod
    @abstractmethod
    def template_text(cls):
        """Return a template configuration text"""
        ...
