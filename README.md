# configoose

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
python -m pip configoose conf --marina ~/my/marina
```
This creates a module `confisgooseconf.py` in your user site-packages directory.
To use another directory on the Python module path instead, pass the option
`--dest /other/directory` to the command.
