# top package __init__.py
__version__ = "2024.06.02"

from . import configurator, database
import sys

root_db = database.Db()


class Configurator(configurator.AbstractConfigurator):
    """Concrete configurator class using default database"""

    @property
    def database(self):
        return root_db


def init_root_db():
    """Initialize the root_db database"""
    from importlib import import_module
    from importlib.util import find_spec
    from pathlib import Path

    # add a marina in memory to reference our configuration files
    marina = database.MarinaDict(tags={"memory"})
    root_db.path.append(marina)

    # configuration handler. Exposes the add_marina() operation
    # that can be used by configuration files.
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
                # add a marina through an extension module
                mod = import_module(extension)
                mod.add_marina(self, style, **kwargs)

    protopath = f"{__name__}.protocol.methodic.Protocol"

    # Attempt to load and handle configooseglobalconf.py and configooseconf.py
    # These files are discovered by the importlib machinery.
    for name, address in [
        (x, x + "-address") for x in (f"{__name__}globalconf", f"{__name__}conf")
    ]:
        if spec := find_spec(name):
            # add discovered file to marina
            marina[address] = database.mediator_dumps(
                database.FileInOsMediator(Path(spec.origin))
            )
            # perform configuration with the methodic protocol
            cfg = Configurator(address)
            cfg.add_protocol(protopath, handler=Handler)
            cfg.run(missing_ok=True)


init_root_db()
