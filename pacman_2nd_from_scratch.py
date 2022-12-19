#screen.blit(transform.rotate(img_player, 90*pacman_dir), pos) # this logic needs RDLU instead of RLUD
debugmode=1

from pygame import *
import copy
from math import pi, cos, sin

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
││■··││·······  ·······││··■││
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

init()
FPS=120

GRID_SIZE=24 #pixel for unit block
HG =GRID_SIZE/2 # half grid

GRID_COUNT_X=len(boards[0])   #30
GRID_COUNT_Y=len(boards)      #33

HEIGHT_HUD=32

COLOR_WALL = 'blue' # maze color
WALL_THICKNESS= 1 ######## better to have the odd number!  3 is better than 2, 7 is better than 8 !!!!

DIR_DICT= {K_RIGHT:0,K_DOWN:1,K_LEFT:2,K_UP:3}# dictionary for direction

screen=display.set_mode([GRID_COUNT_X*GRID_SIZE ,GRID_COUNT_Y*GRID_SIZE+HEIGHT_HUD])
clock=time.Clock() # originally variable timer 

myfont=font.Font('freesansbold.ttf',16)

#################################################### wall parts image creation
from PIL import Image, ImageDraw

# - generate PIL image with transparent background -
size = GRID_SIZE
img_corner = Image.new("RGBA", (GRID_SIZE*2, GRID_SIZE*2))
my_draw = ImageDraw.Draw(img_corner)
my_rect = (0, 0, GRID_SIZE, GRID_SIZE)

segments=48
a=pi/2/ segments


P=[(HG*cos(a*i)  ,HG*sin(a*i))for i in range(segments+1)]
for p1,p2 in zip(P,P[1:]):
     my_draw.line((p1, p2), fill=COLOR_WALL, width=WALL_THICKNESS)

# - convert into PyGame image -
data = img_corner.tobytes()
img_corner = image.fromstring(data, img_corner.size, img_corner.mode)
#################################################### wall parts image end

def draw_board(millisec):
     G=GRID_SIZE
     for i in range(GRID_COUNT_Y):
          for j in range(GRID_COUNT_X):
               c=level[i][j]
               if c=='│':draw.line(   screen, COLOR_WALL, (G*j+HG,G*i),(G*j+HG, G*i+G),WALL_THICKNESS)
               if c=='─':draw.line(   screen, COLOR_WALL, (G*j,G*i+HG),(G*j+G, G*i+HG),WALL_THICKNESS)
               if c=='┘':screen.blit(img_corner, (G*j,G*i))# <- display image
               if c=='┐':screen.blit(transform.rotate(img_corner, 90),     (G*j,G*i-G))
               if c=='┌':screen.blit(transform.rotate(img_corner, 180),    (G*j-G,G*i-G))
               if c=='└':screen.blit(transform.rotate(img_corner, -90),    (G*j-G,G*i))
               if c=='═':draw.line(   screen, 'white', (G*j,G*i+HG), (G*j+G, G*i+HG), WALL_THICKNESS)
               if c=='·':draw.circle( screen, 'white', (G*j+HG, G*i+HG), G//8)
               if c=='■':
                    radius=(G*1.5//4,G*1.5*5//16)[millisec%(FPS*4)<FPS*2]
                    draw.circle( screen, 'white', (G*(j+.5), G*(i+.5)), radius )
                    
# image assets
load_image=lambda type,p:transform.scale(image.load(f'assets/{type}_images/{p}.png'),(GRID_SIZE*1, GRID_SIZE*1))
player_images = [load_image('player',i) for i in (1,2,3,2)]# 4 images
ghost_images  = [load_image('ghost',x) for x in 'red pink blue orange'.split()]
spooked_img   = load_image('ghost','powerup') 
dead_img      = load_image('ghost','dead') 

counter=0

player_x=GRID_SIZE*(GRID_COUNT_X/2)
player_y=GRID_SIZE*24

player_dir=0

PACMAN_CAN_GO=[0]*4# direction

def update_available_direction(player_dir,player_x, player_y):
     player_center_x=int(player_x + GRID_SIZE/2)# prevent float value for level index
     player_center_y=int(player_y + GRID_SIZE/2)# prevent float value for level index

     if GRID_COUNT_X <= (player_x // GRID_SIZE) +1 :return [1,1,0,0] # warping zone

     turns=[0]*4 # RLUD

     visual_offset=(GRID_SIZE) // 2 + 1 # why +3 is best???? actual collision to the visual of the wall # originally num3 
     
     c=player_center_x//GRID_SIZE
     r=player_center_y//GRID_SIZE
     cell_R=level[r][(player_center_x + visual_offset)//GRID_SIZE]
     cell_L=level[r][(player_center_x - visual_offset)//GRID_SIZE]
     cell_U=level[(player_center_y - visual_offset)//GRID_SIZE][c]
     cell_D=level[(player_center_y + visual_offset)//GRID_SIZE][c]
     
     # check passable direction
     if cell_R in ' ·■':turns[0]=1 # moving left, right wall is passable type, right is passable
     if cell_D in ' ·■':turns[1]=1 # moving up, down wall is passable type, down is passable
     if cell_L in ' ·■':turns[2]=1 # moving right, left wall is passable type, left is passable
     if cell_U in ' ·■':turns[3]=1 # moving down, up wall is passable type, up is passable

     # DEBUG DRAW
     if debugmode:
          #_myrect=Rect(player_center_x,player_center_y,GRID_SIZE*10  ,GRID_SIZE*10)
          _myrect=Rect(GRID_SIZE,GRID_SIZE*(GRID_COUNT_Y),GRID_SIZE*10  ,GRID_SIZE*10)
          
          _mystr=f'{PACMAN_CAN_GO},{r},{c},{player_x},{player_center_x},{c*GRID_SIZE}'
          _mytext=myfont.render(_mystr, 1, (255,255,0))             
          screen.blit(_mytext,_myrect)

     draw.circle(screen, color='purple', center=(c*GRID_SIZE,r*GRID_SIZE), radius=5 ,width=0) # player's grid position
     draw.rect(screen, color='purple', rect=(c*GRID_SIZE, r*GRID_SIZE,GRID_SIZE,GRID_SIZE), width=1 ) # 
     draw.circle(screen, color='red', center=(player_center_x,player_center_y), radius=5 ,width=0) # player's center
     
     return turns


def draw_player(milsec,pacman_dir, player_x, player_y):
     player_speed=GRID_SIZE//12
     if PACMAN_CAN_GO[pacman_dir]:# move if pacman can move otherwise, stay
          if pacman_dir==0 :player_x+=player_speed
          if pacman_dir==1 :player_y+=player_speed
          if pacman_dir==2 :player_x-=player_speed
          if pacman_dir==3 :player_y-=player_speed
     
     if GRID_SIZE*GRID_COUNT_X-GRID_SIZE < player_x: 
          player_x= -GRID_SIZE
     if player_x<0:
          player_x=GRID_SIZE*GRID_COUNT_X

     # draw animated pacman at the new position
     pos=(player_x, player_y)
     img_player=player_images[ (milsec//100) %4 ] #player animation
     screen.blit(transform.rotate(img_player, -90*pacman_dir), pos) # this logic needs RDLU instead of RLUD

     return (player_x,player_y)# update player's position

player_wish_dir=-1

start_ticks=time.get_ticks()# game initial time to register
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
               else:player_wish_dir = DIR_DICT.get(e.key, player_dir)# change player direction
          ''' maybe following is not necessary
          elif e.type==KEYUP:
               if e.key == K_ESCAPE:mainloop = False
               elif player_wish_dir == DIR_DICT.get(e.key, player_dir):
                    player_wish_dir = player_dir
          '''
     # change direction if player wish is available 
     for i in range(4):
          if player_wish_dir==i and PACMAN_CAN_GO[i]: # when holding down key 
               if player_x%GRID_SIZE<2 and player_y%GRID_SIZE<2:# if on the grid
                    player_dir = i 
          
     ###################### draw screen
     screen.fill('black')

     PACMAN_CAN_GO=update_available_direction(player_dir,player_x, player_y)
     
     draw_board(millisec)
     (player_x,player_y)=draw_player(millisec,player_dir,player_x,player_y)
     
     display.flip()

quit()