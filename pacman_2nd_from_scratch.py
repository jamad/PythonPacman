from pygame import *
import copy
from math import pi

init()

GRID_H=24 #pixel for unit block 
GRID_W=24 #pixel for unit block
GRID_COUNT_Y=33
GRID_COUNT_X=30 
WIDTH=GRID_COUNT_X*GRID_W
HEIGHT_HUD=32
HEIGHT=GRID_COUNT_Y*GRID_H+HEIGHT_HUD

COLOR_WALL = 'blue' # maze color

FPS=60

screen=display.set_mode([WIDTH,HEIGHT])
clock=time.Clock() # originally variable timer 
myfont=font.Font('freesansbold.ttf',20)

boards_data='''\
┌────────────────────────────┐
│┌────────────┐┌────────────┐│
││············││············││
││·┌──┐·┌───┐·││·┌───┐·┌──┐·││
││■│  │·│   │·││·│   │·│  │■││
││·└──┘·└───┘·└┘·└───┘·└──┘·││
││··························││
││·┌──┐·┌┐·┌──────┐·┌┐·┌──┐·││
││·└──┘·││·└──┐┌──┘·││·└──┘·││
││······││····││····││······││
│└────┐·│└──┐ ││ ┌──┘│·┌────┘│
└────┐│·│┌──┘ └┘ └──┐│·│┌────┘
     ││·││          ││·││     
─────┘│·││ ┌──══──┐ ││·│└─────
──────┘·└┘ │      │ └┘·└──────
       ·   │      │   ·       
──────┐·┌┐ │      │ ┌┐·┌──────
─────┐│·││ └──────┘ ││·│┌─────
     ││·││          ││·││     
┌────┘│·││ ┌──────┐ ││·│└────┐
│┌────┘·└┘ └──┐┌──┘ └┘·└────┐│
││············││············││
││·┌──┐·┌───┐·││·┌───┐·┌──┐·││
││·└─┐│·└───┘·└┘·└───┘·│┌─┘·││
││■··││················││··■││
│└─┐·││·┌┐·┌──────┐·┌┐·││·┌─┘│
│┌─┘·└┘·││·└──┐┌──┘·││·└┘·└─┐│
││······││····││····││······││
││·┌────┘└──┐·││·┌──┘└────┐·││
││·└────────┘·└┘·└────────┘·││
││··························││
│└──────────────────────────┘│
└────────────────────────────┘'''

boards=[list(s) for s in boards_data.split('\n')]# 0 should not be trimmed!
level = copy.deepcopy(boards)

WALL_THICKNESS=2
def draw_board(millisec):
    for i in range(GRID_COUNT_Y):
        for j in range(GRID_COUNT_X):
            c=level[i][j]
            if c=='│':draw.line(   screen, COLOR_WALL, (GRID_W*(j+.5),GRID_H*i),(GRID_W*(j+.5), GRID_H*(i+1)),WALL_THICKNESS)
            if c=='─':draw.line(   screen, COLOR_WALL, (GRID_W*j,GRID_H*(i+.5)),(GRID_W*(j+1), GRID_H*(i+.5)),WALL_THICKNESS)
            if c=='┐':draw.arc(    screen, COLOR_WALL, (GRID_W*(j-.5),GRID_H*(i+.5),GRID_W, GRID_H),0, pi / 2, WALL_THICKNESS)
            if c=='┌':draw.arc(    screen, COLOR_WALL, (GRID_W*(j+.5),GRID_H*(i+.5),GRID_W, GRID_H), pi / 2, pi, WALL_THICKNESS)
            if c=='└':draw.arc(    screen, COLOR_WALL, (GRID_W*(j+.5),GRID_H*(i-.5),GRID_W, GRID_H), pi, 3* pi / 2, WALL_THICKNESS)            
            if c=='┘':draw.arc(    screen, COLOR_WALL, (GRID_W*(j-.5),GRID_H*(i-.5),GRID_W, GRID_H), 3 * pi / 2,2 * pi, WALL_THICKNESS)
            if c=='═':draw.line(   screen, 'white',    (GRID_W*j,GRID_H*(i+.5)), (GRID_W*(j+1), GRID_H*(i+.5)), WALL_THICKNESS)
            if c=='·':draw.circle( screen, 'white',    (GRID_W*(j+.5), GRID_H*(i+.5)), GRID_H//8)
            if c=='■':
               if millisec%(FPS*4)<FPS*2:
                    draw.circle( screen, 'white',    (GRID_W*(j+.5), GRID_H*(i+.5)), GRID_H*5//16)
               else:draw.circle( screen, 'white',    (GRID_W*(j+.5), GRID_H*(i+.5)), GRID_H//4)
            
# image assets
load_image=lambda type,p:transform.scale(image.load(f'assets/{type}_images/{p}.png'),(GRID_W*1, GRID_H*1))
player_images = [load_image('player',i) for i in (1,2,3,2)]# 4 images
ghost_images  = [load_image('ghost',x) for x in 'red pink blue orange'.split()]
spooked_img   = load_image('ghost','powerup') 
dead_img      = load_image('ghost','dead') 

counter=0
player_x=GRID_W*29/2
player_y=GRID_H*24
player_dir=0

def draw_player(milsec,pacman_dir):
     pos=(player_x, player_y)
     img_player=player_images[ (milsec//100) %4 ] #player animation
     if pacman_dir == 0:      screen.blit(img_player, pos)
     elif pacman_dir == 1:    screen.blit(transform.flip(img_player, True, False), pos)
     elif pacman_dir == 2:    screen.blit(transform.rotate(img_player, 90), pos)
     elif pacman_dir == 3:    screen.blit(transform.rotate(img_player, -90), pos)


start_ticks=time.get_ticks()#

mainloop=True
while mainloop:# main loop continues until quit button

     # game time
     clock.tick(FPS)
     millisec=time.get_ticks()-start_ticks # how much milliseconds passed since start

     # user input handling
     for e in event.get():
          if e.type==QUIT:    
               mainloop=False
          elif e.type==KEYDOWN:
               if e.key == K_ESCAPE:mainloop = False
               else:player_dir={K_RIGHT:0,K_LEFT:1,K_UP:2,K_DOWN:3}.get(e.key, player_dir)# change player direction

     
     ###################### draw screen
     screen.fill('black')

     draw_board(millisec)
     draw_player(millisec,player_dir)
     
     display.flip()

quit()




    