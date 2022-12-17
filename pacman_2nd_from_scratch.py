from pygame import *
import copy
from math import pi, cos, sin

init()

GRID_SIZE=24 #pixel for unit block 
GRID_COUNT_Y=33
GRID_COUNT_X=30 
WIDTH=GRID_COUNT_X*GRID_SIZE
HEIGHT_HUD=32
HEIGHT=GRID_COUNT_Y*GRID_SIZE+HEIGHT_HUD

COLOR_WALL = 'blue' # maze color

WALL_THICKNESS= 5 ######## better to have the odd number!  3 is better than 2, 7 is better than 8 !!!!

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

#################################################### wall parts image
from PIL import Image, ImageDraw

# - generate PIL image with transparent background -
size = GRID_SIZE
img_corner = Image.new("RGBA", (GRID_SIZE*2, GRID_SIZE*2))
my_draw = ImageDraw.Draw(img_corner)
my_rect = (0, 0, GRID_SIZE, GRID_SIZE)

segments=48
a=pi/2/ segments
r =GRID_SIZE/2
P=[(r*cos(a*i)  ,r*sin(a*i))for i in range(segments+1)]
for p1,p2 in zip(P,P[1:]):
     my_draw.line((p1, p2), fill=COLOR_WALL, width=WALL_THICKNESS)

# - convert into PyGame image -
data = img_corner.tobytes()
img_corner = image.fromstring(data, img_corner.size, img_corner.mode)
#################################################### wall parts image end

def draw_board(millisec):
     for i in range(GRID_COUNT_Y):
          for j in range(GRID_COUNT_X):
               c=level[i][j]
               if c=='│':draw.line(   screen, COLOR_WALL, (GRID_SIZE*(j+.5),GRID_SIZE*i),(GRID_SIZE*(j+.5), GRID_SIZE*(i+1)),WALL_THICKNESS)
               if c=='─':draw.line(   screen, COLOR_WALL, (GRID_SIZE*j,GRID_SIZE*(i+.5)),(GRID_SIZE*(j+1), GRID_SIZE*(i+.5)),WALL_THICKNESS)
               if c=='┘':screen.blit(img_corner, (GRID_SIZE*(j),GRID_SIZE*(i)))# <- display image
               if c=='┐':screen.blit(transform.rotate(img_corner, 90),  (GRID_SIZE*(j),GRID_SIZE*(i-1)))
               if c=='┌':screen.blit(transform.rotate(img_corner, 180),  (GRID_SIZE*(j-1),GRID_SIZE*(i-1)))
               if c=='└':screen.blit(transform.rotate(img_corner, -90),  (GRID_SIZE*(j-1),GRID_SIZE*(i)))
               if c=='═':draw.line(   screen, 'white',    (GRID_SIZE*j,GRID_SIZE*(i+.5)), (GRID_SIZE*(j+1), GRID_SIZE*(i+.5)), WALL_THICKNESS)
               if c=='·':draw.circle( screen, 'white',    (GRID_SIZE*(j+.5), GRID_SIZE*(i+.5)), GRID_SIZE//8)
               if c=='■':
                    if millisec%(FPS*4)<FPS*2:
                         draw.circle( screen, 'white',    (GRID_SIZE*(j+.5), GRID_SIZE*(i+.5)), GRID_SIZE*5//16)
                    else:draw.circle( screen, 'white',    (GRID_SIZE*(j+.5), GRID_SIZE*(i+.5)), GRID_SIZE//4)

            
# image assets
load_image=lambda type,p:transform.scale(image.load(f'assets/{type}_images/{p}.png'),(GRID_SIZE*1, GRID_SIZE*1))
player_images = [load_image('player',i) for i in (1,2,3,2)]# 4 images
ghost_images  = [load_image('ghost',x) for x in 'red pink blue orange'.split()]
spooked_img   = load_image('ghost','powerup') 
dead_img      = load_image('ghost','dead') 

counter=0
player_x=GRID_SIZE*29/2
player_y=GRID_SIZE*24
player_dir=0

PACMAN_CAN_GO=[1]*4# direction

def update_available_direction(player_dir,player_x, player_y):
     player_center_x=int(player_x+GRID_SIZE/2)# prevent float value for level index
     player_center_y=int(player_y+GRID_SIZE/2)# prevent float value for level index

     turns=[1]*4 # RLUD

     space_visual=(GRID_SIZE - WALL_THICKNESS) // 2  # actual collision to the visual of the wall # originally num3

     if GRID_COUNT_X < player_center_x // GRID_SIZE : # warping
          turns[0]=turns[1]=1
     else:
          cell_L=level[player_center_y//GRID_COUNT_Y][(player_center_x-space_visual)//GRID_COUNT_X]
          cell_R=level[player_center_y//GRID_COUNT_Y][(player_center_x+space_visual)//GRID_COUNT_X]
          cell_U=level[(player_center_y-space_visual)//GRID_COUNT_Y][player_center_x//GRID_COUNT_X]
          cell_D=level[(player_center_y+space_visual)//GRID_COUNT_Y][player_center_x//GRID_COUNT_X]
          
          # check if backward is passable
          if player_dir==1 and cell_R in ' ·■':turns[0]=1 # moving left, right wall is passable type, right is passable
          if player_dir==0 and cell_L in ' ·■':turns[1]=1 # moving right, left wall is passable type, left is passable
          if player_dir==3 and cell_U in ' ·■':turns[2]=1 # moving down, up wall is passable type, up is passable
          if player_dir==2 and cell_D in ' ·■':turns[3]=1 # moving up, down wall is passable type, down is passable

          # check if up and down are passable
          if player_dir in (2,3):
               if GRID_SIZE//2 - 3 <= player_center_x % GRID_COUNT_X <=  GRID_SIZE//2 + 3:
                    if cell_U in ' ·■': turns[2]=1
                    if cell_D in ' ·■': turns[3]=1
               if GRID_SIZE//2 - 3 <= player_center_y % GRID_COUNT_Y <=  GRID_SIZE//2 + 3:
                    if level[player_center_y//GRID_COUNT_Y][player_center_x//GRID_COUNT_X +1] in ' ·■': turns[0]=1 # already center
                    if level[player_center_y//GRID_COUNT_Y][player_center_x//GRID_COUNT_X -1] in ' ·■': turns[1]=1 # already center
     
          # check if up and down are passable
          if player_dir in (0,1):
               if GRID_SIZE//2 - 3 <= player_center_x % GRID_COUNT_X <=  GRID_SIZE//2 + 3:
                    if level[player_center_y//GRID_COUNT_Y-1][player_center_x//GRID_COUNT_X] in ' ·■': turns[2]=1# already center
                    if level[player_center_y//GRID_COUNT_Y+1][player_center_x//GRID_COUNT_X] in ' ·■': turns[3]=1# already center
               if GRID_SIZE//2 - 3 <= player_center_y % GRID_COUNT_Y <=  GRID_SIZE//2 + 3:
                    if cell_R in ' ·■': turns[0]=1 
                    if cell_L in ' ·■': turns[1]=1 
     
     PACMAN_CAN_GO = turns[:]


def draw_player(milsec,pacman_dir, player_x, player_y):
     player_speed=2
     if PACMAN_CAN_GO[pacman_dir]:# move if pacman can move otherwise, stay
          if pacman_dir==0 :
               player_x+=player_speed
          if pacman_dir==1 :
               player_x-=player_speed
          if pacman_dir==2 :
               player_y-=player_speed
          if pacman_dir==3 :
               player_y+=player_speed
     
     #player_x+=2


     pos=(player_x, player_y)
     img_player=player_images[ (milsec//100) %4 ] #player animation
     if pacman_dir == 0:      screen.blit(img_player, pos)
     elif pacman_dir == 1:    screen.blit(transform.flip(img_player, True, False), pos)
     elif pacman_dir == 2:    screen.blit(transform.rotate(img_player, 90), pos)
     elif pacman_dir == 3:    screen.blit(transform.rotate(img_player, -90), pos)

     return (player_x,player_y)


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

     update_available_direction(player_dir,player_x, player_y)

     ###################### draw screen
     screen.fill('black')

     draw_board(millisec)
     (player_x,player_y)=draw_player(millisec,player_dir,player_x,player_y)
     
     display.flip()

quit()




    
