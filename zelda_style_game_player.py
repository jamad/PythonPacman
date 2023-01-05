from pygame import *

class Player(sprite.Sprite):
    def __init__(self,pos, groups):
        super().__init__(groups)

        self.image= image.load('zelda_style_graphics/player.png').convert_alpha()
        self.rect=self.image.get_rect(topleft=pos)

        self.direction = math.Vector2() # this helps to have .y and .x 
        self.speed=5

    def input(self):
        my_keys=key.get_pressed()
        if my_keys[K_UP]:self.direction.y=-1
        elif my_keys[K_DOWN]:self.direction.y=1
        else:self.direction.y=0

        if my_keys[K_LEFT]:self.direction.x=-1
        elif my_keys[K_RIGHT]:self.direction.x=1
        else:self.direction.x=0

    def move(self, speed):
        if self.direction.magnitude():# without this, normalize gets error
            self.direction = self.direction.normalize() # need to reassign
        self.rect.center += self.direction * speed

    def update(self):
        self.input()
        self.move( self.speed)
        