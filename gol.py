import os
import time
import random
import optparse
import platform
PLATFORM = platform.system().upper()

# Defauls
DEFAULT_GRID_WIDTH = 120
DEFAULT_GRID_HEIGHT = 50
DEFAULT_FPS = 25

# Other constants
HUD_COL_WIDTH = 25


class GameOfLife:
    def __init__(self):
        self.initMethods = {
            'random': self.fill_grid_random,
            'shape': self.fill_grid_shape,
            'checkerboard': self.fill_grid_checkerboard
        }
        self.initialized = False
        self.gridWidth = 0
        self.gridHeight = 0
        self.numGridCells = 0
        self.sleepTime = 0.0
        self.generation = 0
        self.randomThreshold = 0.0
        self.seed = 0
        self.wrap = False
        self.lastCalculationTime = 0.0
        self.initMethod = ''
        self.fillshape = ''
        self.grid = []

    def init(self, settings):
        """Get settings from dictionary, initialize grid
        """
        self.initMethod = settings['initmethod']
        self.gridWidth = settings['resolution'][0]
        self.gridHeight = settings['resolution'][1]
        self.numGridCells = self.gridWidth * self.gridHeight
        self.sleepTime = 1.0 / settings['fps']
        self.generation = 0
        self.randomThreshold = settings['randomthreshold']
        self.seed = settings['randomseed']
        self.wrap = settings['wrap']
        self.lastCalculationTime = 0.0
        self.fillshape = settings['fillshape']
        self.grid = GameOfLife.new_grid(self.gridWidth, self.gridHeight)
        self.initialized = True

########################################################
# Conversion
########################################################

    def coord_to_index(self, coord):
        """Convert XY coordinates to a grid index
        """
        x, y = coord
        x = x % self.gridWidth
        y = y % self.gridHeight
        return self.gridWidth * y + x

    def index_to_coord(self, i):
        """Convert a grid index to XY coordinates
        """
        return (i % self.gridWidth, i / self.gridWidth)

########################################################
# Get / Set
########################################################

    def get_cell(self, coord):
        """Get the value of a cell
        """
        if self.wrap:
            return self.grid[self.coord_to_index(coord)]
        else:
            if self.is_inside_grid(coord):
                return self.grid[self.coord_to_index(coord)]
            return False

    def set_cell(self, coord, value):
        """Set value of a cell
        """
        if self.is_inside_grid(coord) or self.wrap:
            self.grid[self.coord_to_index(coord)] = value

########################################################
# Fill grid
########################################################

    def fill_grid_random(self):
        """Fill grid randomly
        """
        random.seed(self.seed)
        for y in range(0, self.gridHeight):
            for x in range(0, self.gridWidth):
                tIndex = self.coord_to_index((x, y))
                if random.random() < self.randomThreshold:
                    self.grid[tIndex] = True
                else:
                    self.grid[tIndex] = False

    def draw_shape(self, coord, shape):
        x, y = coord
        # Double-U
        if shape == 'double-u':
            # Upper U
            self.set_cell((x - 1, y - 1), True)
            self.set_cell((x - 1, y - 2), True)
            self.set_cell((x - 1, y - 3), True)
            self.set_cell((x, y - 3), True)
            self.set_cell((x + 1, y - 3), True)
            self.set_cell((x + 1, y - 2), True)
            self.set_cell((x + 1, y - 1), True)

            # Lower U
            self.set_cell((x - 1, y + 1), True)
            self.set_cell((x - 1, y + 2), True)
            self.set_cell((x - 1, y + 3), True)
            self.set_cell((x, y + 3), True)
            self.set_cell((x + 1, y + 3), True)
            self.set_cell((x + 1, y + 2), True)
            self.set_cell((x + 1, y + 1), True)
        elif shape == 'r-pentomino':
            self.set_cell((x, y), True)
            self.set_cell((x - 1, y), True)
            self.set_cell((x, y + 1), True)
            self.set_cell((x, y - 1), True)
            self.set_cell((x + 1, y - 1), True)

    def fill_grid_shape(self):
        """Put double U shape in center of grid
        """
        self.draw_shape(
            (self.gridWidth / 2, self.gridHeight / 2), self.fillshape)

    def fill_grid_checkerboard(self, size=1):
        """Fill grid with small checkers
        """
        for y in range(0, self.gridHeight):
            for x in range(0, self.gridWidth):
                cellIndex = self.coord_to_index((x, y))
                self.grid[cellIndex] = True if (
                    (cellIndex / size) % 2 == 0) else False

    def fill_grid(self):
        """Fill the grid using one of the available methods
        """
        self.initMethods[self.initMethod]()

########################################################
# Evaluation
########################################################

    def is_inside_grid(self, coord):
        """Return True if given coordinates are within the grid
        """
        x, y = coord
        if x < 0 or x >= self.gridWidth or \
           y < 0 or y >= self.gridHeight:
            return False
        return True

    def count_alive_neighbors(self, coord):
        """Count living neighbor cells of given cell
        """
        # Unpack coordinates
        x, y = coord

        # Count alive neighbors
        aliveNeighbors = 0
        if self.get_cell((x - 1, y)):  # left
            aliveNeighbors += 1
        if self.get_cell((x + 1, y)):  # right
            aliveNeighbors += 1
        if self.get_cell((x, y - 1)):  # top
            aliveNeighbors += 1
        if self.get_cell((x, y + 1)):  # bottom
            aliveNeighbors += 1
        if self.get_cell((x - 1, y - 1)):  # top left
            aliveNeighbors += 1
        if self.get_cell((x + 1, y - 1)):  # top right
            aliveNeighbors += 1
        if self.get_cell((x - 1, y + 1)):  # bottom left
            aliveNeighbors += 1
        if self.get_cell((x + 1, y + 1)):  # bottom right
            aliveNeighbors += 1
        return aliveNeighbors

    def check_cell(self, coord):
        """Check a cell against the rules, return True if
        it should be alive and False if it should be dead
        """
        aliveNeighbors = self.count_alive_neighbors(coord)
        if self.get_cell(coord):
            # If cell is alive
            if aliveNeighbors < 2:
                return False  # Die out
            elif aliveNeighbors >= 2 and aliveNeighbors <= 3:
                return True  # Live on
            elif aliveNeighbors > 3:
                return False  # Die due to overpopulation
        else:
            # If cell is dead
            if aliveNeighbors == 3:
                return True
        return False

    def count_alive(self):
        """Count all living cells on the grid
        """
        alive = 0
        for cell in self.grid:
            if cell:
                alive += 1
        return alive

########################################################
# Action
########################################################

    def advance_grid(self):
        """Compute a new generation of the grid
        """
        timeStart = time.time()
        tmpGrid = GameOfLife.new_grid(self.gridWidth, self.gridHeight)
        for y in range(0, self.gridHeight):
            for x in range(0, self.gridWidth):
                tmpGrid[self.coord_to_index((x, y))] = self.check_cell((x, y))
        self.grid = tmpGrid
        self.generation += 1
        self.lastCalculationTime = time.time() - timeStart

    def draw(self):
        """Draw the grid to the screen
        """
        bufferStr = ''
        for y in range(0, self.gridHeight):
            gridLine = ''
            for x in range(0, self.gridWidth):
                gridIndex = self.coord_to_index((x, y))
                gridLine += u'\u2588' if self.grid[gridIndex] else u' '
            bufferStr = bufferStr + '\n' + gridLine
        print(bufferStr)
        print('\n' +
              ('Generation: ' + str(self.generation)).ljust(HUD_COL_WIDTH) +
              ('Alive: ' + str(self.count_alive())).ljust(HUD_COL_WIDTH) +
              ('Resolution: ' + str(self.gridWidth) + 'x' + str(self.gridHeight)).ljust(HUD_COL_WIDTH) +
              ('Init method: ' + self.initMethod).ljust(HUD_COL_WIDTH) +
              (('Seed: ' + (str(self.seed) if self.seed != 0 else '(random)')).ljust(HUD_COL_WIDTH) if self.initMethod == 'random' else '') +
              (('Threshold: ' + str(self.randomThreshold)).ljust(HUD_COL_WIDTH) if self.initMethod == 'random' else '') +
              ('Calc time: ' +
               '{:0.4f}'.format(self.lastCalculationTime) + ' sec').ljust(HUD_COL_WIDTH)
              )
        print('\nPress CTRL+C to quit!')

    def run(self, pauseInterval=0):
        while True:
            GameOfLife.clear_screen()
            self.draw()
            self.advance_grid()
            time.sleep(self.sleepTime)
            if pauseInterval and (self.generation % pauseInterval == 0):
                GameOfLife.clear_screen()
                self.draw()
                res = raw_input('Reached generation ' + str(self.generation) + '. Stop [enter], do another ' + str(
                    pauseInterval) + ' [n], or continue forever [c]? [y/n] ').lower()
                if res == 'y':
                    return
                if res == 'c':
                    pauseInterval = 0

    @staticmethod
    def new_grid(width, height):
        return [False] * width * height

    @staticmethod
    def clear_screen():
        """Clear screen
        """
        if PLATFORM == 'NT':
            # Call 'CLS' on Windows
            os.system('cls')
        else:
            # Call 'CLEAR' on OSX and Linux
            os.system('clear')


def setup_options():
    parser = optparse.OptionParser()
    optGroup = optparse.OptionGroup(
        parser, 'General options', 'Options for the simulation engine')
    optGroup.add_option('-r', '--resolution', type='int', dest='resolution', nargs=2,
                        help='Grid resolution', default=(DEFAULT_GRID_WIDTH, DEFAULT_GRID_HEIGHT), metavar='WIDTH HEIGHT')
    optGroup.add_option('-f', '--fps', type='int', dest='fps',
                        help='Frames per second', default=DEFAULT_FPS)
    optGroup.add_option('-i', '--interval', type='int',
                        dest='interval', help='Pause every n generations', default=0)
    optGroup.add_option('-w', '--wrap', action='store_true', dest='wrap',
                        help='Set to for torodial space', default=False)
    parser.add_option_group(optGroup)
    optGroup = optparse.OptionGroup(
        parser, 'Fill options', 'Options for grid initialization')
    optGroup.add_option('-m', '--method', type='str', dest='initmethod',
                        help='Method of grid initialization ("random", "shape", "checkerboard")', default='random')
    optGroup.add_option('-s', '--seed', type='int', dest='randomseed',
                        help='Random seed', default=0, metavar='SEED')
    optGroup.add_option('-t', '--threshold', type='float', dest='randomthreshold',
                        help='Cell threshold for random initialization', default=0.5, metavar='THRESHOLD')
    optGroup.add_option('-p', '--shape', type='str', dest='fillshape',
                        help='Shape for filling ("double-u", "r-pentomino")', default='double-u')
    parser.add_option_group(optGroup)

    return parser


def main():
    # Set up
    parser = setup_options()
    options, _ = parser.parse_args()
    optionsDict = vars(options)

    # Welcome
    print('Game of Life')
    print('\nSettings:')
    print(str(optionsDict))
    _ = raw_input(
        'Press ENTER to start the Game of Life!\nPress CTRL+C to cancel!')

    # Play
    game = GameOfLife()
    game.init(settings=optionsDict)
    game.fill_grid()
    game.run(pauseInterval=options.interval)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('Cancelled.')
