import random

from sys import exit

try:
    import pygame as pg
except ImportError:
    raise ModuleNotFoundError("Error: required 'pygame' library not found, install with: 'pip install pygame-ce'")

pg.init()
pg.font.init()

from .settings import settings

class GameObject(pg.sprite.Sprite):
    def __init__(self, size, pos, color, group):
        super().__init__(group)

        self.size = size
        self.pos = pos
        self.group = group

        self.image = pg.Surface(size, pg.SRCALPHA)
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=pos)

        self.outline = pg.draw.rect(self.image, settings.OUTLINE_COLOR, self.image.get_rect(), 1)

class PuzzleState:
    def __init__(self, order):
        self.order = order
        self.current_tiles = list(range(1, order ** 2)) + [0]
        self.goal_state = self.current_tiles.copy()
    
    def is_solved(self):
        return self.current_tiles == self.goal_state
    
    def find_empty(self):
        index = self.current_tiles.index(0)
        return divmod(index, self.order)
    
    def move(self, direction):
        directions = {
            'up': (-1, 0),
            'down': (1, 0),
            'left': (0, -1),
            'right': (0, 1)
        }

        if direction.lower() not in directions:
            return
        
        empty_row, empty_col = self.find_empty()

        
class Board(GameObject):
    def __init__(self, order, group):
        super().__init__(settings.BOARD_SIZE, settings.BOARD_POS, settings.BOARD_COLOR, group)
        self.rect = self.image.get_rect(center=self.pos)
        self.order = order

        self.tiles = PuzzleState(self.order)

        self.tiles_sprite = []
        self.tile_dim = settings.BOARD_DIM // self.order
        self.tile_size = (self.tile_dim, self.tile_dim)

        self.shuffle()
        self.create_tiles()
        
    def create_tiles(self):
        board_x, board_y = self.rect.topleft

        for index, tile in enumerate(self.tiles.current_tiles):
            row, col = divmod(index, self.order)

            pos = (
                board_x + col * self.tile_dim,
                board_y + row * self.tile_dim
            )

            current_tile = Tile(self.tile_size, pos, row, col, self.order, tile, self.group)
            self.tiles_sprite.append(current_tile)
    
    def shuffle(self):
        random.shuffle(self.tiles.current_tiles)

        for tile in self.tiles_sprite:
            tile.kill()
        
        self.create_tiles()

class Tile(GameObject):
    def __init__(self, size, pos, row, col, order, number, group):
        super().__init__(size, pos, settings.TILE_COLOR, group)
        self.row = row
        self.col = col
        self.order = order
        self.number = number

        if number == 0:
            self.image.fill(settings.TILE_TRANSPARENT)
        else:
            self.font = pg.font.Font(None, size[0] // 2)
            self.number_surf = self.font.render(str(number), True, settings.TEXT_COLOR)
            self.number_rect = self.number_surf.get_rect(center=(self.size[0] // 2, self.size[1] // 2))
            self.image.blit(self.number_surf, self.number_rect)

class Main:
    def __init__(self):
        pg.display.set_caption('N-Puzzle Solver')
        self.window = pg.display.set_mode(settings.WINDOW_SIZE)
        self.display = pg.Surface(settings.WINDOW_SIZE)
        self.clock = pg.time.Clock()
        self.objects = pg.sprite.Group()

        self.board = Board(3, self.objects)

    def update(self):
        self.display.fill(settings.BG_COLOR)

        self.objects.draw(self.display)
        self.objects.update()

    def run(self):
        while True:
            self.update()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        pg.quit()
                        exit()
                    
                    if event.key == pg.K_r:
                        self.board.shuffle()
            
            self.window.blit(pg.transform.scale(self.display, self.window.get_size()), (0, 0))
            pg.display.update()
            self.clock.tick(60)