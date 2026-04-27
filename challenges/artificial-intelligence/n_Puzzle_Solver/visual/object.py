from sys import exit
from typing import Tuple, Union

try:
    import pygame as pg
except ImportError:
    raise ModuleNotFoundError("Error: required 'pygame' library not found, install with: 'pip install pygame-ce'")

from pygame.sprite import Group

import settings

class Main:
    def __init__(self) -> None:
        pg.display.set_caption('N-Puzzle Solver')
        self.window = pg.display.set_mode(settings.WINDOW_SIZE)
        self.display = pg.Surface(settings.WINDOW_SIZE)
        self.clock = pg.time.Clock()
        self.objects: pg.sprite.Group[Object] = pg.sprite.Group()

        self.board = Board(3, self.objects)
    
    def update(self):
        self.display.fill(settings.BG_COLOR)

        self.objects.draw(self.display)
        self.objects.update()
    
    def run(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()

            self.update()
            
            self.window.blit(pg.transform.scale(self.display, self.window.get_size()), (0, 0))
            pg.display.update()
            self.clock.tick(60)

class Object(pg.sprite.Sprite):
    def __init__(self, size: Tuple[int, int], pos: Tuple[int, int], color: Union[Tuple[int, int, int], str], groups: Group[Object]) -> None:
        super().__init__(groups)

        self.size = size
        self.pos = pos

        self.image: pg.Surface = pg.Surface((self.size))
        self.image.fill(color)

        self.rect: pg.Rect = self.image.get_rect(topleft=pos)

# -- Board and Tiles --
class Board(Object):
    def __init__(self, order: int, groups: Group[Object]) -> None:
        super().__init__(settings.BOARD_SIZE, settings.BOARD_POS, settings.BOARD_COLOR, groups)
        self.rect: pg.Rect = self.image.get_rect(center=self.pos)
        if order not in (3, 4):
            return

        self.order = order

        self.tiles = list(range(1 ,self.order ** 2 + 1))
        self.tiles[-1] = 0
        self.tile_size = settings.BOARD_DIMENSION // order

    def generate_tiles(self) -> None:
        
        
class Tile(Object):
    def __init__(self, size: Tuple[int, int], pos: Tuple[int, int], groups: Group[Object]) -> None:
        super().__init__(size, pos, settings.TILE_COLOR, groups)

main = Main()
main.run()