from pygame import *


class Level:
    def __init__(self) -> None:

        self.display_surface = display.get_surface() # get display surface
        self.visible_sprintes=sprite.Group()
        self.col_sprites=sprite.Group()

    def run(self):
        pass
