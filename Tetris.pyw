from graphics import *
import random
cellSize = 20 # pixels
import time
cells = 20    # along one side
debug = False
gridSize = cellSize * cells # along one side (in pixels)
class Game:
    def __init__(self):
        self.cellSize = 20
        self.height = 20
        self.width = 12
        self.points = 0
        self.spawn_point = (int(self.width/2),1)
        self.grid_width = self.cellSize * self.width
        self.grid_height = self.cellSize * self.height
        self.win = GraphWin("Tetris", self.grid_width, self.grid_height+100 )
        Line(Point(1,1),Point(self.win.getWidth(),1)).draw(self.win)
        Line(Point(1,0),Point(1,self.win.getHeight())).draw(self.win)
        Line(Point(self.win.getWidth(),0), \
             Point(self.win.getWidth(), self.win.getHeight())).draw(self.win)
        Line(Point(0,self.win.getHeight()), \
             Point(self.win.getWidth(),self.win.getHeight())).draw(self.win)
        """ Draws line to separate buttons """
        Line(Point(self.grid_width/3,500),Point(self.grid_width/3,400)).draw(self.win)
        Line(Point(self.grid_width*2/3,500),Point(self.grid_width*2/3,400)).draw(self.win)
        Line(Point(0,400),Point(400,400)).draw(self.win)
        """ Labels buttons """
        Text(Point(40, 475), "Score").draw(self.win)
        Text(Point(self.grid_width-40, 475), "High score").draw(self.win)

        self.occupied_squares = {}
        self.score_display = Text(Point(40, 430), self.points)
        self.score_display.undraw()

    def game_setup(self):
        #clear the board if there are any blocks on it (for example when restarting a game)
        if self.occupied_squares:
            [square.undraw() for square in self.occupied_squares.values()]
        while True: 
            if self.win.checkKey() == "space":
                time.sleep(0.1)
                break
        #required for collision detection
        self.points = 0
        self.unoccupied_squares = set([(x,y) for x in range (self.width) for y in range(self.height)])
        #maps coordinates to the square objects residing there
        self.occupied_squares = {}
        #maps row numbers to the coordinates occupied in them, used to detect line completion
        self.occupied_coords = {}
        self.change_points()
    def change_points(self):
        self.score_display.undraw()
        self.score_display = Text(Point(40, 430), self.points)
        self.score_display.draw(self.win)
        pass

    def generate(self):
        blocks = {
            0:T_block,
            1:S_block,
            2:Z_block,
            3:L_block,
            4:J_block,
            5:I_block,
            6:O_block
            }
        self.block = blocks[random.randint(0,6)](self)
        self.game_over = self.block.end_game
    def occupy(self):
        for element in self.block.squares:
            coords = element[0]
            rect = element[1]
            self.occupied_squares[coords] = rect
            y_coord = coords[1]
            if not self.occupied_coords.get(y_coord):
                self.occupied_coords[y_coord] = [coords]
            else:
                self.occupied_coords[y_coord].append(coords)
    #remove blocks
    def score(self):
        lines = 0
        for y_coord in list(self.occupied_coords.keys()):
            if len(self.occupied_coords[y_coord]) == self.width:
                lines+=1
                for coords in self.occupied_coords[y_coord]:
                    self.unoccupied_squares.add(coords)
                    self.occupied_squares[coords].undraw()
                del self.occupied_coords[y_coord]
                lines_to_be_shifted = [i for i in range(min(self.occupied_coords.keys()),y_coord)][::-1]
                for y in lines_to_be_shifted:
                    #necessary because the coords list gets modified by the .shift method and doing so will make the for loop skip every other square
                    old_coords = self.occupied_coords[y][::1]
                    for coords in old_coords:
                        if self.occupied_squares.get(coords):
                            self.occupied_squares[coords].shift()
        self.points += (lines*(lines+1)/2)*100
        self.change_points()
    def start(self):
        self.game_setup()
        self.generate()
        cycle_start = time.time()
        while True:
            if self.block.set:
                self.occupy()
                self.score()
                self.generate()
                if self.game_over:
                    print("Game over.")
                    while True:
                        key_press = self.win.checkKey()
                        if key_press == "space":
                            return True
                        if key_press:
                            return False
            time_elapsed = time.time() - cycle_start
            a = self.win.checkKey()
            x_dir = 0
            y_dir = 0
            if a == "Left":
                y_dir = 0
                x_dir = -1
                self.block.move(x_dir,y_dir)
            if a == "Right":
                y_dir = 0
                x_dir = 1
                self.block.move(x_dir,y_dir)
            if a == "Down":
                self.block.move()
            if a == "s":
                self.block.rotate()
            if a == "a":
                self.block.rotate(-1)
            if time_elapsed > 0.5:
                self.block.move()
                cycle_start = time.time()
            if a == "space":
                break
        self.close()
    def close(self):
        self.win.close()

class Square(Rectangle):
    def __init__(self,coords,game,colour):
        x = coords[0]
        y = coords[1]
        self.coords = coords
        self.game = game
        point_x = Point(x*game.cellSize,y*game.cellSize)
        point_y = Point((x+1)*game.cellSize,(y+1)*game.cellSize)
        Rectangle.__init__(self,point_x,point_y)
        self.colour = colour
        self.setFill(self.colour)
        if coords in self.game.unoccupied_squares:
            self.draw(game.win)
            self.spawned = True
        else:
            self.spawned = False

    def shift(self):
        self.undraw()
        self.game.unoccupied_squares.add(self.coords)
        self.game.occupied_squares.pop(self.coords)
        self.game.occupied_coords[self.coords[1]].remove(self.coords)
        #new coordinates
        self.coords = (self.coords[0],self.coords[1]+1)
        
        self.__init__(self.coords,self.game,self.colour)
        self.game.unoccupied_squares.remove(self.coords)
        self.game.occupied_squares[self.coords] = self
        if not self.game.occupied_coords.get(self.coords[1]):
            self.game.occupied_coords[self.coords[1]] = [self.coords]
        else:
            self.game.occupied_coords[self.coords[1]].append(self.coords)
    
class Block:
    def __init__(self,game):
        self.game = game
        x = game.spawn_point[0]
        y = game.spawn_point[1]
        self.blocks = [(x+a,y+b) for a,b in self.base]
        self.squares = [(x,Square(x,game,self.colour)) for x in self.blocks]
        for square in self.squares:
            if square[1].spawned:
                self.end_game = False
            else:
                self.end_game = True
                #gotta add the spawned squares to occupied_squares so that game_setup can actually remove them
                for square in self.squares:
                    if square[1].spawned:
                        self.game.occupied_squares[square[0]] = square[1]
                break
        self.set = False
        self.mode = 0
    def move(self,x_dir = 0,y_dir = 1):
        self.old_blocks = self.blocks
        self.blocks = [(x+x_dir,y+y_dir) for x,y in self.blocks]
        self.apply_transform(y_dir==1)
    def apply_transform(self,moved_down = False):
        if set(self.blocks).intersection(self.game.unoccupied_squares) == set(self.blocks):
            [block[1].undraw() for block in self.squares]
            self.squares = [(coords,Square(coords,self.game,self.colour)) for coords in self.blocks]
            return True
        else:
            self.blocks = self.old_blocks
            if moved_down:
                self.game.unoccupied_squares = self.game.unoccupied_squares.difference(self.blocks)
                self.set = True
        pass
    def rotate(self,clockwise = 1):
        a = self.blocks
        #pick the transformation to apply
        if clockwise == 1:
            b = self.transformations[self.mode]
        else:
            #pick the previous transformation to the current mode if it's counter-clockwise
            mode = (self.mode - 1) % self.symmetry
            b = self.transformations[mode]
        c = clockwise
        #apply coordinate transformations
        self.old_blocks = self.blocks
        #if counter-clockwise, reverse the sign of the transformations
        self.blocks = [(a[i][0]+c*b[i][0],a[i][1]+c*b[i][1]) for i in range(4)]
        transform_successful = self.apply_transform()
        #increment mode if trans succeeds
        if transform_successful:
            self.mode += clockwise
            self.mode = self.mode % self.symmetry

class T_block(Block):
    def __init__(self,game):
        self.colour = "orange"
        self.base = [(-1,0),(0,0),(0,-1),(1,0)]
        self.symmetry = 4
        self.transformations = [[(1,-1),(0,0),(1,1),(-1,1)],
                                [(1,1),(0,0),(-1,1),(-1,-1)],
                                [(-1,1),(0,0),(-1,-1),(1,-1)],
                                [(-1,-1),(0,0),(1,-1),(1,1)],
                                ]
        Block.__init__(self, game)
    pass
class Z_block(Block):
    def __init__(self,game):
        self.colour = "grey"
        self.base = [(1,0),(0,0),(0,-1),(-1,-1)]
        self.symmetry = 2
        self.transformations = [[(0,-2),(0,0),(0,0),(2,0)],
                                [(0,2),(0,0),(0,0),(-2,0)]
                                ]
        Block.__init__(self, game)
    pass
class S_block(Block):
    def __init__(self,game):
        self.colour = "purple"
        self.base = [(-1,0),(0,0),(0,-1),(1,-1)]
        self.symmetry = 2
        self.transformations = [[(2,0),(0,0),(0,0),(0,2)],
                                [(-2,0),(0,0),(0,0),(0,-2)]
                                ]
        Block.__init__(self, game)
    pass
class L_block(Block):
    def __init__(self,game):
        self.colour = "brown"
        self.base = [(0,-1),(0,0),(0,1),(-1,1)]
        self.symmetry = 4 
        self.transformations = [[(1,1),(0,0),(-1,-1),(0,-2)],
                                [(-1,1),(0,0),(1,-1),(2,0)],
                                [(-1,-1),(0,0),(1,1),(0,2)],
                                [(1,-1),(0,0),(-1,1),(-2,0)],
                                ]
        Block.__init__(self, game)
    pass
class J_block(Block):
    def __init__(self,game):
        self.colour = "green"
        self.base = [(0,-1),(0,0),(0,1),(1,1)]
        self.symmetry = 4
        self.transformations = [[(1,1),(0,0),(-1,-1),(-2,0)],
                                [(-1,1),(0,0),(1,-1),(0,-2)],
                                [(-1,-1),(0,0),(1,1),(2,0)],
                                [(1,-1),(0,0),(-1,1),(0,2)],
                                ]
        Block.__init__(self, game)
    pass
class I_block(Block):
    def __init__(self,game):
        self.colour = "blue"
        self.base = [(-2,-1),(-1,-1),(0,-1),(1,-1)]
        self.symmetry = 2
        self.transformations = [[(1,1),(0,0),(-1,-1),(-2,-2)],
                                [(-1,-1),(0,0),(1,1),(2,2)]
                                ]
        Block.__init__(self, game)
        
    pass
class O_block(Block):
    def __init__(self,game):
        self.colour = "red"
        self.base = [(-1,-1),(-1,0),(0,-1),(0,0) ]
        Block.__init__(self, game)
    def rotate(self,clockwise = 1):
        pass
    pass
game = Game()
while game.start():
    game
    pass
