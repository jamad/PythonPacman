from pygame import *
import copy
from math import pi

init()

GRID_H=16 #pixel for unit block 
GRID_W=16 #pixel for unit block
GRID_COUNT_Y=33
GRID_COUNT_X=30 
WIDTH=GRID_COUNT_X*GRID_W
HEIGHT_HUD=32
HEIGHT=GRID_COUNT_Y*GRID_H+HEIGHT_HUD

COLOR_WALL = 'blue' # maze color

FPS=60

screen=display.set_mode([WIDTH,HEIGHT])
timer=time.Clock()
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

def draw_board():
    for i in range(GRID_COUNT_Y):
        for j in range(GRID_COUNT_X):
            cell=level[i][j]
            # 0: ' ', 1: '·', 2:'■',3:'│',4:'─',5:'┐',6:'┌',7:'└',8:'┘',9:'═', 
            # 0 = empty , 1 = dot, 2 = power dot, 3 = v line, 4 = h line, 5, 6,7,8 = corners, 9 = home gate
            if cell == '·':draw.circle(   screen, 'white',    (GRID_W*(j+.5), GRID_H*(i+.5)), GRID_H//8)
            if cell == '■':draw.circle(   screen, 'white',    (GRID_W*(j+.5), GRID_H*(i+.5)), GRID_H*5//16 if 1 else GRID_H//4)
            if cell == '│':draw.line(     screen, COLOR_WALL, (GRID_W*(j+.5), i * GRID_H),(GRID_W*(j+.5), (i+1)*GRID_H),3)
            if cell == '─':draw.line(     screen, COLOR_WALL, (GRID_W*j,  GRID_H*(i+.5)), (GRID_W*(j+1), GRID_H*(i+.5)),3)
            if cell == '┐':draw.arc(      screen, COLOR_WALL, (GRID_W*(j-.4)- 2,GRID_H*(i+.5), GRID_W, GRID_H),0, pi / 2, 3)
            if cell == '┌':draw.arc(      screen, COLOR_WALL, (GRID_W*(j+.5),   GRID_H*(i+.5),GRID_W, GRID_H), pi / 2, pi, 3)
            if cell == '└':draw.arc(      screen, COLOR_WALL, (GRID_W*(j+.5),   GRID_H*(i-.4),  GRID_W, GRID_H), pi, 3* pi / 2, 3)            
            if cell == '┘':draw.arc(      screen, COLOR_WALL, (GRID_W*(j-.4)- 2,GRID_H*(i-.4),  GRID_W, GRID_H), 3 * pi / 2,2 * pi, 3)
            if cell == '═':draw.line(     screen, 'white',    (GRID_W*j, GRID_H*(i+.5)), (GRID_W*j + GRID_W, GRID_H*(i+.5)), 3)
            
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

def draw_player():
    pos=(player_x, player_y)
    img_player=player_images[counter // 5]
    if player_dir == 0:      screen.blit(img_player, pos)
    elif player_dir == 1:    screen.blit(transform.flip(img_player, True, False), pos)
    elif player_dir == 2:    screen.blit(transform.rotate(img_player, 90), pos)
    elif player_dir == 3:    screen.blit(transform.rotate(img_player, -90), pos)

while QUIT not in (e.type for e in event.get()):# main loop continues until quit button
     timer.tick(FPS)
     screen.fill('black')
     
     # draw screen
     draw_board()
     draw_player()
     
     display.flip()

quit()




    
