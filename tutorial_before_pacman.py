# https://w3cschoool.com/tutorial/pygame-tutorial

from pygame import init,sprite,Surface,time,display,K_LEFT, K_RIGHT, K_UP, K_DOWN, event,QUIT,key
#import sys

class Sprite(sprite.Sprite):
    def __init__(self, pos):
        sprite.Sprite.__init__(self)
        self.image = Surface([20, 20])
        self.image.fill((255, 0, 255))
        self.rect = self.image.get_rect()
        self.rect.center = pos

fps = 50
size =[300, 300]

init()

clock = time.Clock()
screen = display.set_mode(size)

player = Sprite([40, 50])

# Define keys for player movement
player_speed = 5
player.image.fill((255, 255, 0)) 

wall = Sprite([100, 60])
wall2 = Sprite([160, 60])

wall_group = sprite.Group(wall)
wall_group.add(wall2)

player_group = sprite.Group(player)
#player_group.add(player)

def mainloop():return not any(e.type == QUIT for e in event.get())

def userinput():
    _key_input = key.get_pressed()
    player.rect.x += player_speed *(_key_input[K_RIGHT]-_key_input[K_LEFT])
    player.rect.y += player_speed*(_key_input[K_DOWN]-_key_input[K_UP])

def collisioncheck():
    if sprite.spritecollide(player, wall_group, True):
        player.image.fill((255, 255, 255)) # if collision is detected call a function to destroy

def drawscreen():
    screen.fill([0, 0, 0])
    player_group.draw(screen)
    wall_group.draw(screen)
    display.update()

while mainloop():
    userinput()
    collisioncheck()
    drawscreen()
    clock.tick(fps)
    
print('all done')