Install
=======

To install the ``configoose`` module, use the command

.. code-block:: bash

    python -m pip install git+https://github.com/Gribouillis/configoose.git

Initialization
**************

``configoose`` manages a database. To initialize it you must create
a new directory, called a :emphasis:`marina`.
The syntax depends on your operational system:

.. code-block:: bash

    mkdir /some/new/directory

It is then necessary to configure ``configoose`` so that it uses this
directory for its database. Launch the command

.. code-block:: bash

    python -m configoose conf --marina /some/new/directory

This command creates a new file named :code:`configooseconf.py`
in the first :code:`site-packages` directory of your Python
interpreter.

If you don't have writing permission in the :code:`site-packages`
directory, you can alternatively write a :code:`userconfigooseconf.py`
file in your user :code:`site-packages` directory. For this,
pass the :code:`--user` switch to the previous command.

You could also prefer another directory
:emphasis:`on the Python module search path` to install
the :code:`configooseconf.py` file.
For this pass the :code:`--dest /your/preferred/directory` option
to the previous command.

You can check that everything went well by running the following
command

.. code-block:: bash

    python -m configoose marina-list

The last line of output should resemble

.. code-block:: bash

    MarinaDirInOs(PosixPath('/some/new/directory'), tags={'initial'})

