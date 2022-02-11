# drogue
Dimly-lit dungeons, deep delving dooms. Rogue in the dark.

## Changelog
(0.9 -> 1.0)
* Characters can now have names
* Various updates
* Finalised mechanics
(0.7 -> 0.9)
* Verbose mode is now default. To use minimised mode use the --quiet or -q flag instead.
* Assorted updates
* Added warding scroll

## What is this?
Drogue is a 1-dimensional roguelike. You can only go in two directions - forward (deeper into the dungeon) and backwards (fleeing to safety). You will receive hints that tell you what encounters remain in each room. If you run away while monsters are still present, they might catch up!

## Installation (Windows users)
Download and run `drogue.exe` from the releases section.

## Installation from source (Mac OS/X, Linux users)
Download `drogue.py`. Run it using Python 3.8 or above. Newcomers are highly encouraged to use the `-vb` flag to show more detailed information.

## How do I play?
### Commands:
* (nothing): next encounter
* r: run to next room
* h: display help
* q: exit dungeon (finalise score)
* u: use item
* c: check status

### Options (use when starting new game from command line):
* `-q`, `--quiet`: compact descriptions
* `--seed`: starting seed
