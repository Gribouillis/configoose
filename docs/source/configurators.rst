Configurators
=============

Configurators allow a program to run a configuration
defined elsewhere and registred with an abstract address.
The program will create a Configurator and call its
:meth:`run` method

.. code-block:: python

    cfg = Configurator("some-abstract-address")
    cfg.run()

When this code is executed, a lookup is performed in
configoose's database to see if a configuration file has
been registered for the address :code:`"some-abstract-address"`.

If no such file has been registered, an exception is raised
unless :code:`missing_ok=True` is passed to :meth:`run()`.

Adding protocols
****************


The above code alone does not suffice to process the configuration
content that is contained in the file. For this one must declare
one or more protocols in the configurator, so the code now looks like

.. code-block:: python

    cfg = Configurator("some-abstract-address")
    cfg.add_protocol("some.Protocol")
    cfg.add_protocol("some.other.Protocol")
    cfg.run()

Now when the :meth:`run` method is called and a configuration file
is found, configoose will look if the protocol defined in the
configuration file matches one of the protocols that were added to
the :class:`Configurator` instance.

If one of the protocol matches, an instance of the corresponding
subclass of :class:`Protocol` is created and the protocol's
own :meth:`run` method is called with the data found in the configuration
file.

This system enables programs to accept several ways of configuring
themselves, for example a program could accept configuration files
in the form of ini files or json files or toml files by adding three
protocols to the configurator, one for each type of configuration
file.

The first argument in :meth:`add_protocol` is a string representing
a dotted path in Python's modules system to the target protocol class.
For example to use configoose's :code:`raw` configuration protocol,
one would pass :code:`"configoose.protocol.raw.Protocol"` because
the target class is the class :class:`Protocol` defined in
module :mod:`configoose.protocol.raw`.

Handler functions
*****************

What protocols do in their :meth:`run` method is specific to each
protocol class.

A mechanism is provided so that these :meth:`run` method can call
a function provided by the client program, namely the program can
define handler functions when protocols are added. The syntax is

.. code-block:: python

    @cfg.add_protocol("some.protocol")
    def handler(...):
        ...

Another way to declare the same thing is


.. code-block:: python

    cfg.add_protocol("some.protocol", handler=handler)

The arguments of the handler function depend on the protocol, but
typically they include data extracted from the configuration file.

An example with the :code:`raw` protocol
****************************************

The raw protocol accepts arbitrary text in the configuration file
and it passes that text to the handler function. A program could
define the following

.. code-block:: python

    cfg = Configurator("some-abstract-address")

    @cfg.add_protocol("configoose.protocol.raw.Protocol")
    def handler(ap, preamble, text, mediator):
        print(text)

    cfg.run()

The effect of this code is to print the text found in the
configuration file. A configuration file for this Python
program could contain

.. code-block:: text

    {
        "address" : "some-abstract-address",
        "protopath" : "configoose.protocol.raw.Protocol",
    }
    spam spam eggs
    eggs eggs and more spam
    ham * 3

Upon program execution, the following would be printed in the output

.. code-block:: text

    spam spam eggs
    eggs eggs and more spam
    ham * 3
