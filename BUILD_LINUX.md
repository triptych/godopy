## Installing dependencies
```
sudo apt-get install python3-venv python3-dev
sudo apt-get build-dep python3.8
```

## Setting environment variables
```
export GODOT_BUILD=<path to Godot source folder>
```
> Replace `<path to Godot source folder>` with an actual path. Godot source should be compiled.


## Building internal Python interpreter and libraries
```
$ cd godopy
$ ./build_python.py
$ deps/python/build/bin/python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install -U pip Cython numpy ipython
(venv) $ # Use pip to install any Python dependencies you want
(venv) $ deactivate
```


## Building GodoPy
```
$ python3 -m venv setup
$ source setup/bin/activate
(setup) $ pip install -r dev-requirements.txt
(setup) $ ./bootstrap.py && ./clean.sh
(setup) $ scons  # scons -j4 only_cython=yes && scons -j4
(setup) $ deactivate
```
> Sometimes it is required to deactivate and reactivate the virtual environment before running scons
> If you want to run an initial build with a -j option, build with "only_cython=yes" first, otherwise the required headers will be missing
> Python wheels inside `dist/` can be created with `python -m pep517.build .` command


## Setting up GodoPy development environment
```
$ cd .. # return to the project's root
$ python3 -m venv tools
$ source tools/bin/activate
(tools) $ cd godopy
(tools) $ python setup.py develop
```
> When you finish working with a virtual environment, run the `deactivate` command
