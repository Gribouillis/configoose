Quickstart
==========

Install
-------

To install the ``configoose`` module, use the command

.. code-block:: bash

    python -m pip install git+https://github.com/Gribouillis/configoose.git

Initialization
--------------

``configoose`` manages a database. To initialize it you must create
a new directory, called a :emphasis:`marina`.
The syntax depends on your operating system:

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

Simple Example
--------------

Create a configuration file
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Let us create a file using ConfigParser for configuration. Type the following
command in a terminal, it will create a file :code:`spam.cfg` in your
home directory. You can use any other directory or file name if you wish.

.. code-block:: bash

    python -m configoose template configoose.protocol.configparser.Protocol -o ~/spam.cfg

Now edit the new file and populate it with configuration data in the
syntax of configparser. The file is an ordinary configparser file, except that
there is a small Python dictionary at the beginning, called a :emphasis:`preamble`.
Leave this dictionary as it is. Your file's content should resemble this one

.. code-block:: ini

    {
        "address" : "s8dzw5y5anduiodmrdrxdgxaa",
        "protopath" : "configoose.protocol.configparser.Protocol",
    }
    [spam]
    ham =
        slice A
        slice B
        slice C

    [more]
    eggs = 1000

Register the configuration file in configoose's database
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run the command

.. code-block:: bash

    python -m configoose moor initial ~/spam.cfg

This step associates in the configoose database the address
contained in the configuration file to the location of the file.

Create a program that uses the configuration file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

With a code editor, create the following program

.. code-block:: python

    from configoose import Configurator

    cfg = Configurator("s8dzw5y5anduiodmrdrxdgxaa")

    @cfg.add_protocol("configoose.protocol.configparser.Protocol")
    def handler(ap, preamble, parser):
        print('ham = ', parser['spam']['ham'])
        print(f"There are {parser['more']['eggs']} eggs!")

    cfg.run()

Run the program, its output shows that it read the configuration
file correctly

.. code-block:: text

    ham =
    slice A
    slice B
    slice C
    There are 1000 eggs!
