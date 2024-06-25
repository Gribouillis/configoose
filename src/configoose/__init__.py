# top package __init__.py
__version__ = "2024.06.17"


def doctopic_assembly():  # pragma: no cover
    from .doc.itopic import doctopic_assembly

    return doctopic_assembly()


from . import configurator, database

root_db = database.Db()


class Configurator(configurator.AbstractConfigurator):
    @property
    def database(self):
        return root_db


def init_root_db():
    """Initialize the root_db database"""
    from importlib import import_module
    from pathlib import Path

    top_address = "l20m9c3k1qhixcv0msrabz09d"
    top_name = __name__
    marina = database.MarinaDict(tags={"memory"})
    root_db.path.append(marina)
    try:
        config_mod = import_module("init_mooring_configuration")
    except ImportError:
        pass
    else:
        marina[top_address] = database.mediator_dumps(
            database.FileInOsMediator(Path(config_mod.__spec__.origin))
        )
    cfg = Configurator(top_address)

    @cfg.add_protocol(f"{top_name}.protocol.methodic.Protocol")
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

    cfg.run()


init_root_db()
