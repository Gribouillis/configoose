# configoose

Read the main documentation at [configoose.readthedocs.io](https://configoose.readthedocs.io/en/latest/index.html)

## Install
```
python -m pip install git+https://github.com/Gribouillis/configoose.git
```
Create a new directory to use as initial marina. Choose the path freely
```
mkdir ~/my/marina
```
Initialize configoose's database to use this marina
```
python -m configoose conf --marina ~/my/marina
```
This creates a module `confisgooseconf.py` in your site-packages directory.
To use another directory on the Python module path instead, pass the option
`--dest /other/directory` to the command.
