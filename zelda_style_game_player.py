from pygame import *
from zelda_style_game_settings import *

class Player(sprite.Sprite):
    def __init__(self,pos, groups, collisions):
        super().__init__(groups)

        self.image= image.load('zelda_style_graphics/player.png').convert_alpha()
        self.rect=self.image.get_rect(topleft=pos)
        #self.rect.width=TILESIZE
        #self.rect.height=TILESIZE
        #print(self.rect)

        self.direction = math.Vector2() # this helps to have .y and .x 
        self.speed=8

        self.col_sprites=collisions

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
        
        #self.rect.center += self.direction * speed
        #self.rect.center.x += self.direction.x * speed  ##  << this cause error
        #self.rect.center.y += self.direction.y * speed
        self.rect.x += self.direction.x * speed
        self.collision('horizon')
        self.rect.y += self.direction.y * speed
        self.collision('vertical')


    def collision(self,direction):
        if direction=='horizon':
            for obs in self.col_sprites:
                if obs.rect.colliderect(self.rect):
                    if 0<self.direction.x:
                        self.rect.right=obs.rect.left # clamping the movement by alignment 
                    if self.direction.x <0 :
                        self.rect.left=obs.rect.right # clamping the movement by alignment
        if direction=='vertical':
            for obs in self.col_sprites:
                if obs.rect.colliderect(self.rect):
                    if 0<self.direction.y:
                        self.rect.bottom=obs.rect.top
                    if self.direction.y<0:
                        self.rect.top=obs.rect.bottom


    def update(self):
        self.input()
        self.move( self.speed)
        self.collision(self.direction)

        