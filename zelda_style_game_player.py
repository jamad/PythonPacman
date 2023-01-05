from pygame import *

class Player(sprite.Sprite):
    def __init__(self,pos, groups):
        super().__init__(groups)

        self.image= image.load('../zelda_style_graphics/player.png').convert_alpha()
        self.rect=self.image.get_rect(topleft=pos)
