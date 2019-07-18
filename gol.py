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
            'shape1': self.fill_grid_shape1,
            'shape2': self.fill_grid_shape2,
            'checkerboard1': self.fill_grid_checkerboard1,
            'checkerboard2': self.fill_grid_checkerboard2
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
        self.grid = GameOfLife.new_grid(self.gridWidth, self.gridHeight)
        self.initialized = True

    def coord_to_index(self, x, y):
        """Convert XY coordinates to a grid index
        """
        x = x % self.gridWidth
        y = y % self.gridHeight
        return self.gridWidth * y + x

    def index_to_coord(self, i):
        """Convert a grid index to XY coordinates
        """
        return (i % self.gridWidth, i / self.gridWidth)

    def fill_grid_random(self):
        """Fill grid randomly
        """
        random.seed(self.seed)
        for y in range(0, self.gridHeight):
            for x in range(0, self.gridWidth):
                tIndex = self.coord_to_index(x, y)
                if random.random() < self.randomThreshold:
                    self.grid[tIndex] = True
                else:
                    self.grid[tIndex] = False

    def fill_grid_shape1(self):
        """Put double U shape in center of grid
        """
        centerX = self.gridWidth / 2
        centerY = self.gridHeight / 2

        # Upper U
        self.grid[self.coord_to_index(centerX - 1, centerY - 1)] = True
        self.grid[self.coord_to_index(centerX - 1, centerY - 2)] = True
        self.grid[self.coord_to_index(centerX - 1, centerY - 3)] = True
        self.grid[self.coord_to_index(centerX, centerY - 3)] = True
        self.grid[self.coord_to_index(centerX + 1, centerY - 3)] = True
        self.grid[self.coord_to_index(centerX + 1, centerY - 2)] = True
        self.grid[self.coord_to_index(centerX + 1, centerY - 1)] = True

        # Lower U
        self.grid[self.coord_to_index(centerX - 1, centerY + 1)] = True
        self.grid[self.coord_to_index(centerX - 1, centerY + 2)] = True
        self.grid[self.coord_to_index(centerX - 1, centerY + 3)] = True
        self.grid[self.coord_to_index(centerX, centerY + 3)] = True
        self.grid[self.coord_to_index(centerX + 1, centerY + 3)] = True
        self.grid[self.coord_to_index(centerX + 1, centerY + 2)] = True
        self.grid[self.coord_to_index(centerX + 1, centerY + 1)] = True

    def fill_grid_shape2(self):
        """Put r-Pentomino in center of grid
        """
        centerX = self.gridWidth / 2
        centerY = self.gridHeight / 2

        self.grid[self.coord_to_index(centerX, centerY)] = True
        self.grid[self.coord_to_index(centerX - 1, centerY)] = True
        self.grid[self.coord_to_index(centerX, centerY + 1)] = True
        self.grid[self.coord_to_index(centerX, centerY - 1)] = True
        self.grid[self.coord_to_index(centerX + 1, centerY - 1)] = True

    def fill_grid_checkerboard1(self):
        """Fill grid with small checkers
        """
        for y in range(0, self.gridHeight):
            for x in range(0, self.gridWidth):
                cellIndex = self.coord_to_index(x, y)
                self.grid[cellIndex] = True if (cellIndex % 2 == 0) else False

    def fill_grid_checkerboard2(self):
        """Fill grid with large checkers
        """
        for y in range(0, self.gridHeight):
            for x in range(0, self.gridWidth):
                cellIndex = self.coord_to_index(x, y)
                self.grid[cellIndex] = True if (
                    (cellIndex / 2) % 2 == 0) else False

    def fill_grid(self):
        """Fill the grid using one of the available methods
        """
        self.initMethods[self.initMethod]()

    def inside_grid(self, x, y):
        """Return True if given coordinates are within the grid
        """
        if x < 0 or x >= self.gridWidth or \
           y < 0 or y >= self.gridHeight:
            return False
        return True

    def get_cell(self, x, y):
        """Get the value of a cell
        """
        if self.wrap:
            return self.grid[self.coord_to_index(x, y)]
        else:
            if self.inside_grid(x, y):
                return self.grid[self.coord_to_index(x, y)]
            return False

    def set_cell(self, x, y, value):
        """Set value of a cell
        """
        if self.inside_grid(x, y) or self.wrap:
            self.grid[self.coord_to_index(x, y)] = value

    def count_alive_neighbors(self, x, y):
        """Count living neighbor cells of given cell
        """
        # Count alive neighbors
        aliveNeighbors = 0
        if self.get_cell(x - 1, y):  # left
            aliveNeighbors += 1
        if self.get_cell(x + 1, y):  # right
            aliveNeighbors += 1
        if self.get_cell(x, y - 1):  # top
            aliveNeighbors += 1
        if self.get_cell(x, y + 1):  # bottom
            aliveNeighbors += 1
        if self.get_cell(x - 1, y - 1):  # top left
            aliveNeighbors += 1
        if self.get_cell(x + 1, y - 1):  # top right
            aliveNeighbors += 1
        if self.get_cell(x - 1, y + 1):  # bottom left
            aliveNeighbors += 1
        if self.get_cell(x + 1, y + 1):  # bottom right
            aliveNeighbors += 1
        return aliveNeighbors

    def check_cell(self, x, y):
        """Check a cell against the rules, return True if
        it should be alive and False if it should be dead
        """
        aliveNeighbors = self.count_alive_neighbors(x, y)
        if self.get_cell(x, y):
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

    def advance_grid(self):
        """Compute a new generation of the grid
        """
        timeStart = time.time()
        tmpGrid = GameOfLife.new_grid(self.gridWidth, self.gridHeight)
        for y in range(0, self.gridHeight):
            for x in range(0, self.gridWidth):
                tmpGrid[self.coord_to_index(x, y)] = self.check_cell(x, y)
        self.grid = tmpGrid
        self.generation += 1
        self.lastCalculationTime = time.time() - timeStart

    def count_alive(self):
        """Count all living cells on the grid
        """
        alive = 0
        for cell in self.grid:
            if cell:
                alive += 1
        return alive

    def draw(self):
        """Draw the grid to the screen
        """
        bufferStr = ''
        for y in range(0, self.gridHeight):
            gridLine = ''
            for x in range(0, self.gridWidth):
                gridIndex = self.coord_to_index(x, y)
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
              ('Calc time: ' + '{:0.4f}'.format(self.lastCalculationTime) + ' sec').ljust(HUD_COL_WIDTH)
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
                res = raw_input('Reached generation ' + str(self.generation) + '. Stop [enter], do another ' + str(pauseInterval) + ' [n], or continue forever [c]? [y/n] ').lower()
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
    parser.add_option('-r', '--resolution', type='int', dest='resolution', nargs=2,
                      help='Grid resolution', default=(DEFAULT_GRID_WIDTH, DEFAULT_GRID_HEIGHT), metavar='WIDTH HEIGHT')
    parser.add_option('-m', '--method', type='str', dest='initmethod',
                      help='Method of grid initialization ("random", "shape1", "shape2", "checkerboard1", "checkerboard2")', default='random')
    parser.add_option('-f', '--fps', type='int', dest='fps',
                      help='Frames per second', default=DEFAULT_FPS)
    parser.add_option('-s', '--seed', type='int', dest='randomseed',
                      help='Random seed', default=0, metavar='SEED')
    parser.add_option('-i', '--interval', type='int',
                      dest='interval', help='Pause every n generations', default=0)
    parser.add_option('-t', '--threshold', type='float', dest='randomthreshold',
                      help='Cell threshold for random initialization', default=0.5, metavar='THRESHOLD')
    parser.add_option('-w', '--wrap', action='store_true', dest='wrap',
                      help='Set to for torodial space', default=False)
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
