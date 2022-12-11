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
player.move = [K_LEFT, K_RIGHT, K_UP, K_DOWN]
player.vx = 5
player.vy = 5
player.image.fill((255, 255, 0)) 

wall = Sprite([100, 60])

wall_group = sprite.Group()
wall_group.add(wall)

player_group = sprite.Group()
player_group.add(player)

def mainloop():
    if any(e.type == QUIT for e in event.get()):return 0
    return 1

def userinput():
    k = key.get_pressed()
    for i in range(2):
        if k[player.move[i]]:       player.rect.x += player.vx * [-1, 1][i]

    for i in range(2):
        if k[player.move[2:4][i]]:  player.rect.y += player.vy * [-1, 1][i]

def collisioncheck():
    hit = sprite.spritecollide(player, wall_group, True)
    if hit:
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