# GameOfLife
A quick Python implementation of Conways Game of Life.

The Game of Life, also known simply as Life, is a cellular automaton devised by the British mathematician John Horton Conway in 1970.

The game is a zero-player game, meaning that its evolution is determined by its initial state, requiring no further input. One interacts with the Game of Life by creating an initial configuration and observing how it evolves, or, for advanced players, by creating patterns with particular properties.

(Introductory text taken from [Wikipedia](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life)).

## Implementation
It has all been written in just a short time, as a test. It's using only python standard libraries, and utilizes the Terminal for drawing. It is not efficient, but easy to understand and quite flexible in usage.

## Usage
The easiest way to run the Game of Life is by typing:  
`python gol.py`

There are, however, several command line options to change what happens:
### General Command line options
* __rules__  
  `gol.py --rules=23/45`  
  Rules are formulated in the notation "S/B", e.g. "23/3". The first value determines how many neighbor cells have to be alive for a cell to survive. The second value means how many neighbor cells have to be alive for a dead cell to be reborn.  
  There are special rule names that can be used for convenience: "original" is the default rule set (23/3) and "copyworld" is a strange world where patterns are reproduced endlessly (1357/1357).

* __resolution__  
  `gol.py --resolution=200 80`  
  This determines the resolution of the cell grid. The default resolution is 120x50.

* __fps__  
  `gol.py --fps=5`  
  Determines the number of evaluations per second. Default is 25.

* __step__  
  `gol.py --step=1`  
  Determines the number of evaluations that are calculated before the program pauses. After each pause, you can choose to continue until the next break, continue forever, or cancel.  
  A step value of 0 will not pause at all, a step value of 1 will pause after every evaluation.

* __wrap__  
  `gol.py --wrap`  
  If this is set, the coordinate system will be torodial: Structures that leave one side of the grid will reappear on the opposite side. If not set, cells outside of the grid perimeter will be considered dead.

### Fill options
* __method__  
  `gol.py --method=random`  
  `gol.py --method=checkerboard`  
  `gol.py --method=shape`  
This determines the method of grid initialization. Default is "random".
  * __random__ will fill the grid randomly. The distribution of random cells can be controlled with the __--seed__ optoins, the relative amount of alive cells can be controlled with the __--threshold__ option.
  * __checkerboard__ will fill the grid with a parametric checkerboard pattern.
  * __shape__ will place a shape (roughly) in the center of the grid. What kind of shape can be controlled with the __--shape__ and __--shapefile__ options.

* __seed__  
  `gol.py --method=random --seed=12345`  
The random seed affects the distribution of alive cells. When using the same seed as before, the same initial distribution will occur. A seed value of "0" will use a random seed value, so the distribution will be unique every time.

* __threshold__  
  `gol.py --method=random --threshold=0.1`  
The threshold value controls the relative amount of alive cells in random initialization. It should be between 0.0 and 1.0. Larger values will produce more initial alive cells.

* __shape__  
  `gol.py --method=shape --shape=double-u`  
  `gol.py --method=shape --shape=r-pentomino`  
  `gol.py --method=shape --shape=f`  
  `gol.py --method=shape --shape=line`  
  `gol.py --method=shape --shape=file`  
There are several different pre-defined shapes to initialize the grid with. However, the most interesting option is "file", as it lets you load a shape from a .cells file (as often used in the [Life Wiki](http://www.conwaylife.com/wiki/Main_Page)).

* __shapefile__  
  `gol.py --method=shape --shape=file --shapefile=cells/p28glidershuttle.cells`  
This option lets you define a file to load for grid initialization. There are some example files in the "cells" subfolder, but you can also write your own, or get more from the [Life Wiki](http://www.conwaylife.com/wiki/Main_Page).

  Supported file formats are:
  * __.cells__  
    A straight-forward plain-text format that anybody can just write.

  * __.rle__  
    A run length encoded file format that is often used for cell patterns.  
    It is often used for larget and more complex patterns, and is the most commonly used file format on the [Life Wiki](http://www.conwaylife.com/wiki/Main_Page).

## Examples
Here are some example calls that lead to interesting results:

* `python gol.py --method=shape --shape=file --shapefile=cells/smiley.cells --rules 1357/1357`  
A copy world that produces reappearing smileys.

* `python gol.py --method=checkerboard --resolution=201 80`  
An evolving picture frame.

* `python gol.py --seed=69 --threshold=0.0005 --rules 1357/1357`  
Fireworks in a copyworld.

* `python gol.py --seed=69 --threshold=0.1`  
Chaotic stuff that kind of stabilizes after around 300 evaluations.
