# https://w3cschoool.com/tutorial/pygame-tutorial

from pygame import init,sprite,Surface,time,display,K_LEFT, K_RIGHT, K_UP, K_DOWN, event,QUIT,key, transform
#import sys

class Sprite(sprite.Sprite):
    def __init__(self, pos):
        sprite.Sprite.__init__(self)
        self.image = Surface([16, 16])
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
player_speed = 1
player.image.fill((255, 255, 0)) 

player_group = sprite.Group(player)

wall_group = sprite.Group()
for i in range(10):
    for j in range(10):
        wall=Sprite([100+20*i,100+20*j])
        wall_group.add(wall)

def mainloop():return not any(e.type == QUIT for e in event.get())

def userinput():
    _key_input = key.get_pressed()
    player.rect.x += player_speed *(_key_input[K_RIGHT]-_key_input[K_LEFT])
    player.rect.y += player_speed*(_key_input[K_DOWN]-_key_input[K_UP])


def collisioncheck():
    if sprite.spritecollide(player, wall_group, True):# the last True means player destroy walls
        width,height=player.image.get_size()
        posX,posY=player.rect.x, player.rect.y
        #print()
        player.image = Surface( [width*1.1,  height*1.1])
        player.image.fill((255, 255, 255)) # if collision is detected call a function to destroy
        
        player.rect = player.image.get_rect()
        player.rect.center=(posX+width//2,posY+height//2)

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