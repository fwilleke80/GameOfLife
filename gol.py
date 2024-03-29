import os
import sys
import time
import random
import optparse
import platform
PLATFORM = platform.system().upper()

# Defauls
DEFAULT_GRID_WIDTH = 80
DEFAULT_GRID_HEIGHT = 30
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
        self.shapeFilename = ''
        self.grid = []
        self.changeGrid = []
        self.ruleSet = ''
        self.ruleSetValSurvive = ''
        self.ruleSetValBirth = ''

    def init(self, settings: dict):
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
        self.shapeFilename = settings['shapefile']
        self.grid = GameOfLife.new_grid(self.gridWidth, self.gridHeight)
        self.changeGrid = GameOfLife.new_grid(
            self.gridWidth, self.gridHeight, defaultValue=True)
        # Ruleset parser
        self.ruleSet, self.ruleSetValSurvive, self.ruleSetValBirth = GameOfLife.parse_ruleset(
            settings['ruleset'])
        self.initialized = True

########################################################
# Conversion
########################################################

    def coord_to_index(self, coord: tuple[int, int]) -> int:
        """Convert XY coordinates to a grid index
        """
        x, y = coord
        x = x % self.gridWidth
        y = y % self.gridHeight
        return self.gridWidth * y + x

    def index_to_coord(self, i: int) -> tuple[int, int]:
        """Convert a grid index to XY coordinates
        """
        return (i % self.gridWidth, i / self.gridWidth)

########################################################
# Get / Set
########################################################

    def get_cell(self, coord: tuple[int, int]) -> bool:
        """Get the value of a cell
        """
        if self.wrap:
            return self.grid[self.coord_to_index(coord)]
        else:
            if self.is_inside_grid(coord):
                return self.grid[self.coord_to_index(coord)]
            return False

    def get_cell_changed(self, coord: tuple[int, int]) -> bool:
        """Look up if the value of a cell has changed in the last advance() call
        """
        if self.wrap:
            return self.changeGrid[self.coord_to_index(coord)]
        else:
            if self.is_inside_grid(coord):
                return self.changeGrid[self.coord_to_index(coord)]
            return False

    def set_cell(self, coord: tuple[int, int], value: bool):
        """Set value of a cell
        """
        if self.is_inside_grid(coord) or self.wrap:
            cellIndex = self.coord_to_index(coord)
            currentValue = self.grid[cellIndex]
            if currentValue != value:
                self.grid[cellIndex] = value
                self.changeGrid[cellIndex] = True
            else:
                self.changeGrid[cellIndex] = False

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

    def draw_shape(self, coord: tuple[int, int], shape: str, drawDeadFiledata: bool=True):
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
        # R-Pentomino
        elif shape == 'r-pentomino':
            self.set_cell((x, y), True)
            self.set_cell((x - 1, y), True)
            self.set_cell((x, y + 1), True)
            self.set_cell((x, y - 1), True)
            self.set_cell((x + 1, y - 1), True)
        # F
        elif shape == 'f':
            self.set_cell((x, y), True)
            self.set_cell((x, y - 1), True)
            self.set_cell((x, y - 2), True)
            self.set_cell((x, y - 3), True)
            self.set_cell((x - 1, y - 3), True)
            self.set_cell((x + 1, y - 3), True)
            self.set_cell((x, y - 4), True)
            self.set_cell((x, y - 5), True)
            self.set_cell((x, y - 6), True)
            self.set_cell((x + 1, y - 6), True)
            self.set_cell((x + 2, y - 6), True)
            self.set_cell((x - 1, y - 6), True)
            self.set_cell((x - 2, y - 6), True)
        # Line
        elif shape == 'line':
            lineLength = 20
            for x1 in range(x - lineLength, x + lineLength):
                self.set_cell((x1, y), True)
                self.set_cell((x1 - 1, y), True)
                self.set_cell((x1 - 2, y), True)
                self.set_cell((x1 - 3, y), True)
                self.set_cell((x1 + 1, y), True)
                self.set_cell((x1 + 2, y), True)
                self.set_cell((x1 + 3, y), True)
        # Load shape from file
        elif shape == 'file':
            shapeData = GameOfLife.load_shape_data(self.shapeFilename)
            offsetX = int(len(shapeData[0]) / 2)
            offsetY = int(len(shapeData) / 2)
            for target_y, shapeLine in enumerate(shapeData):
                for target_x, char in enumerate(shapeLine):
                    if char == 'o':
                        self.set_cell(
                            (x - offsetX + target_x, y - offsetY + target_y), True)
                    elif char == '.' and drawDeadFiledata:
                        self.set_cell((x + target_x, y + target_y), False)

    def fill_grid_shape(self):
        """Put double U shape in center of grid
        """
        self.draw_shape(
            (int(self.gridWidth / 2), int(self.gridHeight / 2)), self.fillshape)

    def fill_grid_checkerboard(self, size: int=1):
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

    def is_inside_grid(self, coord: tuple[int, int]) -> bool:
        """Return True if given coordinates are within the grid
        """
        x, y = coord
        if x < 0 or x >= self.gridWidth or \
           y < 0 or y >= self.gridHeight:
            return False
        return True

    def count_alive_neighbors(self, coord: tuple[int, int]) -> int:
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

    def check_cell(self, coord: tuple[int, int]) -> bool:
        """Check a cell against the rules, return True if
        it should be alive and False if it should be dead
        """
        aliveNeighbors = self.count_alive_neighbors(coord)
        if self.get_cell(coord):
            if aliveNeighbors in self.ruleSetValSurvive:
                return True
        else:
            if aliveNeighbors in self.ruleSetValBirth:
                return True
        return False

    def count_alive(self) -> int:
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
              ('Calc time: ' +
               '{:0.4f}'.format(self.lastCalculationTime) + ' sec').ljust(HUD_COL_WIDTH) +
              ('Resolution: ' + str(self.gridWidth) + 'x' + str(self.gridHeight)).ljust(HUD_COL_WIDTH) +
              '\n' +
              ('Init method: ' + self.initMethod).ljust(HUD_COL_WIDTH) +
              (('Seed: ' + (str(self.seed) if self.seed != 0 else '(random)')).ljust(HUD_COL_WIDTH) if self.initMethod == 'random' else '') +
              (('Threshold: ' + str(self.randomThreshold)).ljust(HUD_COL_WIDTH) if self.initMethod == 'random' else '') +
              (('Shape: ' + str(self.fillshape)).ljust(HUD_COL_WIDTH) if self.initMethod == 'shape' else '') +
              ('Rules: ' + (self.ruleSet if self.ruleSet != 'p' else (''.join(str(x)
                                                                              for x in self.ruleSetValSurvive) + '/' + ''.join(str(x) for x in self.ruleSetValBirth)))).ljust(HUD_COL_WIDTH)
              )
        print('\nPress CTRL+C to quit!')

    def run(self, step=0):
        GameOfLife.clear_screen()
        self.draw()
        while True:
            if step and (self.generation % step == 0):
                GameOfLife.clear_screen()
                self.draw()
                res = raw_input('Reached generation ' + str(self.generation) + '. Do another ' + str(
                    step) + ' [enter], stop [n], or continue forever [c]? [enter/n/c] ').lower()
                if res == 'n':
                    return
                if res == 'c':
                    step = 0
            self.advance_grid()
            GameOfLife.clear_screen()
            self.draw()
            time.sleep(self.sleepTime)

    @staticmethod
    def load_file_plaintext(filename: str) -> list[str]:
        try:
            with open(filename, 'rb') as dataFile:
                lines = dataFile.readlines()
        except:
            print('Error reason from file ' + filename)
            lines = []

        resultLines = []
        for line in lines:
            line = line.decode().lower()
            if len(line) > 0 and line[0] in 'o.':
                resultLines.append(line)

        return resultLines

    @staticmethod
    def load_file_rle(filename: str) -> dict:
        """Load shape data from RLE (Run Length Encoded) file
        """
        try:
            with open(filename, 'rb') as dataFile:
                lines = dataFile.readlines()
        except:
            print('Error reason from file ' + filename)
            lines = []

        rawPattern = ''
        dataDict = {
            'name' : '',
            'author': '',
            'width': 0,
            'height': 0,
            'rule': {},
            'comments' : []
        }

        for line in lines:
            line = line.decode()
            # Parse or comment lines
            if line.startswith('#'):
                if line.upper().startswith('#N'):
                    # Pattern name
                    dataDict['name'] = line.lstrip('#N ').strip(' \n\r\t')
                elif line.upper().startswith('#C'):
                    # Pattern comments
                    dataDict['comments'].append(line.lstrip('#Cc ').strip(' \n\r\t'))
                elif line.upper().startswith('#O'):
                    # Pattern author
                    dataDict['author'] = line.lstrip('#Oo ').strip(' \n\r\t')
                continue

            # Parse meta line
            elif ',' in line:
                # Break up line
                width, height, rule = line.split(',')

                # Parse width and height
                width = int(width.split('=')[1].strip())
                height = int(height.split('=')[1].strip())

                # Parse rule
                r1, r2 = rule.split('=')[1].strip().lower().split('/')
                if r1.startswith('b'):
                    _, ruleSurvive, ruleBirth = GameOfLife.parse_ruleset(r2[1:] + '/' + r1[1:])
                else:
                    _, ruleSurvive, ruleBirth = GameOfLife.parse_ruleset(r1[1:] + '/' + r2[1:])
                
                dataDict['width'] = width
                dataDict['height'] = height
                dataDict['rule'] = { 'birth': ruleBirth, 'survive': ruleSurvive }

                continue

            # Collect cell data
            else:
                rawPattern += line.strip(' \n\r\t')
                
        # Now parse collected cell data
        patternRows = rawPattern.rstrip('!').split('$')
        resultLines = []
        for lineIndex, row in enumerate(patternRows):
            tmpStr = ''
            resultLines.append('')
            for c in row:
                if c.isdigit():
                    tmpStr += c
                else:
                    if tmpStr == '':
                        numCells = 1
                    else:
                        numCells = int(tmpStr)
                    for _ in range(numCells):
                        if c == 'b':
                            resultLines[lineIndex] = resultLines[lineIndex] + '.'
                        else:
                            resultLines[lineIndex] = resultLines[lineIndex] + 'o'
                    tmpStr = ''
        
        dataDict['cells'] = resultLines

        return dataDict

    @staticmethod
    def load_shape_data(filename: str) -> list[str]:
        """Load shape data from ASCII file
        """
        if not os.path.isfile(filename):
            raise IOError('A file called ' + filename + ' does not exist!')

        resultLines = []

        fileExtension = os.path.splitext(filename)[1].lower()
        if fileExtension == '.cells':
            resultLines = GameOfLife.load_file_plaintext(filename)
        elif fileExtension == '.rle':
            resultData = GameOfLife.load_file_rle(filename)
            resultLines = resultData['cells']

        return resultLines

    @staticmethod
    def new_grid(width: int, height: int, defaultValue: bool=False) -> list[bool]:
        return [defaultValue] * width * height

    @staticmethod
    def parse_ruleset(ruleSetString: str) -> tuple:
        ruleSet = ruleSetString.lower()

        # Catch specially named rule sets
        if ruleSet == 'original':
            ruleSet = '23/3'
        elif ruleSet == 'copyworld':
            ruleSet = '1357/1357'

        if '/' in ruleSet:
            (ruleSurvive, ruleBirth) = ruleSet.split('/')
            if not ruleSurvive.isdigit() or not ruleBirth.isdigit():
                sys.exit(
                    'Error: Both parts of the rule string must be numeric! (Format (int)survive/(int)birth)')
            ruleSurvive = [int(n) for n in ruleSurvive]
            ruleBirth = [int(n) for n in ruleBirth]
            ruleSet = 'p'
        else:
            # Could not parse a reasonable rule set
            pass
        return (ruleSet, ruleSurvive, ruleBirth)

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
    optGroup.add_option('--rules', type='str', dest='ruleset',
                        help='Rules of the system ["original", "copyworld", "[s]/[b]"]', metavar='RULESET', default='original')
    optGroup.add_option('--resolution', type='int', dest='resolution', nargs=2,
                        help='Grid resolution', default=(DEFAULT_GRID_WIDTH, DEFAULT_GRID_HEIGHT), metavar='WIDTH HEIGHT')
    optGroup.add_option('--fps', type='int', dest='fps',
                        help='Frames per second', default=DEFAULT_FPS)
    optGroup.add_option('--step', type='int',
                        dest='step', help='Pause every n generations', default=0)
    optGroup.add_option('--wrap', action='store_true', dest='wrap',
                        help='Set for torodial space', default=False)
    parser.add_option_group(optGroup)
    optGroup = optparse.OptionGroup(
        parser, 'Fill options', 'Options for grid initialization')
    optGroup.add_option('--method', type='str', dest='initmethod',
                        help='Method of grid initialization ("random", "shape", "checkerboard")', default='random')
    optGroup.add_option('--seed', type='int', dest='randomseed',
                        help='Random seed', default=time.time(), metavar='SEED')
    optGroup.add_option('--threshold', type='float', dest='randomthreshold',
                        help='Cell threshold for random initialization', default=0.5, metavar='THRESHOLD')
    optGroup.add_option('--shape', type='str', dest='fillshape',
                        help='Shape for filling ("double-u", "r-pentomino", "f", "line", "file")', default='double-u')
    optGroup.add_option('--shapefile', type='str', dest='shapefile',
                        help='Path to an ASCII shape data file', default='')
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
    _ = input(
        'Press ENTER to start the Game of Life!\nPress CTRL+C to cancel!')

    # Play
    game = GameOfLife()
    game.init(settings=optionsDict)
    game.fill_grid()
    game.run(step=options.step)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('Cancelled.')
