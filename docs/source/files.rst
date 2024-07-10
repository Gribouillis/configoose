Configuration files
===================

Preamble
********

Configuration files are ordinary text files except that
they start with a small Python dictionary called
the preamble. Their structure is

.. code-block:: text

    {
        "address": "some-abstract-address",
        "protopath": "some.protocol",
    }
    blah blah blah
    blah blah blah
    ...

The configuration content that comes after the preamble
can be arbitrary: json, python code, configparser code
etc.

Registration
************

Once written, a configuration file needs to be registered
in the configoose database. This registration is done on
the command line with the :code:`moor` subcommand.

.. code-block:: bash

    python -m configoose moor initial /path/to/config/file

The word :emphasis:`initial` in the previous command is a
tag identifying the initial marina in configoose's database.
See the usage string of the moor command for more.

Find a moored configuration
***************************

Use the command line  with the :code:`find` subcommand

.. code-block:: bash

    python -m configoose find "some-abstract-address"

Unregister
**********

Use the command line with the :code:`unmoor` subcommand

.. code-block:: bash

    python -m configoose unmoor /path/to/config/file

    # or

    python -m configoose unmoor -a "some-abstract-address"
