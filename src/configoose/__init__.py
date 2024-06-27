# top package __init__.py
__version__ = "2024.06.01"

from . import configurator, database
import sys

root_db = database.Db()


class Configurator(configurator.AbstractConfigurator):
    @property
    def database(self):
        return root_db


def init_root_db():
    """Initialize the root_db database"""
    from importlib.util import find_spec
    from pathlib import Path

    marina = database.MarinaDict(tags={"memory"})
    root_db.path.append(marina)

    class Handler:
        def __init__(self, ap, preamble):
            pass

        def add_marina(self, style, **kwargs):
            if style == "os-directory":
                marina = database.MarinaDirInOs(
                    Path(kwargs["path"]), tags=kwargs.get("tags", ())
                )
                root_db.path.append(marina)
            elif extension := kwargs.get("extension", None):
                # ajout d'une marina par un module d'extension
                mod = import_module(extension)
                mod.add_marina(self, style, **kwargs)

    protopath = f"{__name__}.protocol.methodic.Protocol"

    for name, address in [
        (x, x + "-address") for x in (f"{__name__}globalconf", f"{__name__}conf")
    ]:
        if spec := find_spec(name):
            marina[address] = database.mediator_dumps(
                database.FileInOsMediator(Path(spec.origin))
            )
            cfg = Configurator(address)
            cfg.add_protocol(protopath, handler=Handler)
            cfg.run(missing_ok=True)


init_root_db()
