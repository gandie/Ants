# Ants

Simple Pygame-based Ants Simulator

Ants (indicated by blue color) are "stupid" state-machines and can only "see"
neighbouring fields. By laying traces the ants are still able to find efficient
paths to the food sources (red) and bring it back to the nest (green). For each
100 units of food returned to the nest a new ant will spawn.

# Installation

This python package can be installed after requirements have been installed:

Ubuntu:
```bash
pip3 install -r requirements.txt
python3 setup.py install
```

# Usage

Press ARROW-UP to start simulation, ARROW-DOWN to stop.

Use left click to spawn some food, right click to create a blocked field (white)

```
usage: ants [-h] [-g GRIDSIZE] [-c COLONIES] [-s STARTANTS] [-f FOOD]
            [--nospawn]

optional arguments:
  -h, --help            show this help message and exit
  -g GRIDSIZE, --gridsize GRIDSIZE
                        Size of ants grid. Default 25
  -c COLONIES, --colonies COLONIES
                        Number of ant colonies created. Default 1
  -s STARTANTS, --startants STARTANTS
                        Number of ants spawned at start. Default 25
  -f FOOD, --food FOOD  Number of food fields at start. Default 100
  --nospawn             Prevent spawning new ants
```
