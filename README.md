# Ants

Simple Pygame-based Ants Simulator

# Installation

This python package can be installed (optionally, but strongly recommended into a <a href="http://docs.python-guide.org/en/latest/dev/virtualenvs/#lower-level-virtualenv">virtualenv</a>)
after requirements have been installed:

```bash
pip3 install -r requirements.txt
python3 setup.py install
```

# Usage

```
usage: ants [-h] [-g GRIDSIZE] [-s STARTANTS] [-f FOOD] [--nospawn]

optional arguments:
  -h, --help            show this help message and exit
  -g GRIDSIZE, --gridsize GRIDSIZE
                        Size of ants grid. Default 25
  -s STARTANTS, --startants STARTANTS
                        Number of ants spawned at start. Default 25
  -f FOOD, --food FOOD  Number of food fields at start. Default 100
  --nospawn             Prevent spawning new ants
```
