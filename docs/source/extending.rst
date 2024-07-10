Extending with new protocols
============================

This advanced section explains how to extend configoose by
defining your own protocol.

We illustrate this by an example showing how to define a
protocol :code:`yourmodule.TomlProtocol` to handle configuration
written in toml language.

To do so, you need to create a subclass of
:code:`configoose.protocol.abc.Protocol` with a :meth:`run`
method and optionally a :meth:`template` method.

Here is the content of :code:`yourmodule.py`

.. code-block:: python

    # file yourmodule.py
    from configoose.protocol import abc
    import tomllib # python >= 3.11

    class TomlProtocol(abc.Protocol):

        def run(self, ap, preamble, text, mediator):
            # parse the toml configuration file
            data = tomllib.loads(text)

            # if the client code defines a handler,
            # call that handler with the parsed data
            if handler := ap.kwargs.get("handler", None):
                handler(ap, preamble, data, mediator))


The arguments received by the :meth:`run` method are an
object :code:`ap` which members :code:`ap.args` and
:code:`ap.kwargs` are the arguments given by client code
to the :meth:`add_protocol` method, an object
:code:`preamble` containing the data read in the
configuration's file preamble, the text following
the preamble in the configuration file and a mediator
which is the object through which the configuration data
was found.  The mediator's :meth:`system_path` method
returns the location where the configuration file was
found in the file system, if it was found in such a location.
