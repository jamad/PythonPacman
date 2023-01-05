from pygame import *
from zelda_style_game_settings import *

class Player(sprite.Sprite):
    def __init__(self,pos, groups, collisions):
        super().__init__(groups)

        self.image= image.load('zelda_style_graphics/player.png').convert_alpha()
        self.rect=self.image.get_rect(topleft=pos)

        self.direction = math.Vector2() # this helps to have .y and .x 
        self.speed=1

        self.col_sprites=collisions

        #player collision to reduce
        self.hitbox=self.rect.inflate(-16,-32) # LR 1,1 and UD 5,5 reduce the pixel size 

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

        #self.rect.x += self.direction.x * speed
        self.hitbox.x += self.direction.x * speed
        self.collision('horizon')
        #self.rect.y += self.direction.y * speed
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')

        self.rect.center=self.hitbox.center# without it, player cannot move!


    def collision(self,direction):
        if direction=='horizon':
            for obs in self.col_sprites:
                if obs.rect.colliderect(self.hitbox):
                    if 0<self.direction.x:
                        self.hitbox.right=obs.rect.left # clamping the movement by alignment 
                    if self.direction.x <0 :
                        self.hitbox.left=obs.rect.right # clamping the movement by alignment
        if direction=='vertical':
            for obs in self.col_sprites:
                if obs.rect.colliderect(self.hitbox):
                    if 0<self.direction.y:
                        self.hitbox.bottom=obs.rect.top
                    if self.direction.y<0:
                        self.hitbox.top=obs.rect.bottom


    def update(self):
        self.input()
        self.move( self.speed)
        self.collision(self.direction)

        