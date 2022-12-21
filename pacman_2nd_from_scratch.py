#screen.blit(transform.rotate(img_player, 90*player_dir), pos) # this logic needs RDLU instead of RLUD
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
NIMINUM_UNIT=4 # quarter of grid ( minimum : 2 ,  maximum  maybe 8)

HG =NIMINUM_UNIT*2 # half grid 

GRID_SIZE=HG*2 #pixel for unit block

GRID_COUNT_X=len(boards[0])   #30
GRID_COUNT_Y=len(boards)      #33

HEIGHT_HUD=32

COLOR_WALL = 'blue' # maze color
WALL_THICKNESS= 1 ######## better to have the odd number!  3 is better than 2, 7 is better than 8 !!!!

DIR_DICT= {K_RIGHT:0,K_DOWN:1,K_LEFT:2,K_UP:3}# dictionary for direction

### global variables
player_speed=GRID_SIZE/16 # can be 1 

score=0
player_x=GRID_SIZE*GRID_COUNT_X//2
player_y=GRID_SIZE*24
player_dir=-4
player_wish_dir=-1

pacman_moving=0 # for pacman animation
powerup_phase=0

screen=display.set_mode([GRID_COUNT_X*GRID_SIZE ,GRID_COUNT_Y*GRID_SIZE+HEIGHT_HUD])
clock=time.Clock() # originally variable timer 

myfont=font.Font('freesansbold.ttf',GRID_SIZE//4*3)

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

# image assets
load_image=lambda type,p:transform.scale(image.load(f'assets/{type}_images/{p}.png'),(GRID_SIZE*1, GRID_SIZE*1))
player_images = [load_image('player',i) for i in (1,2,3,2)]# 4 images
ghost_images  = [load_image('ghost',x) for x in 'red pink blue orange'.split()]
spooked_img   = load_image('ghost','powerup') 
dead_img      = load_image('ghost','dead') 
     

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
                    
def update_available_direction():
     global player_dir,player_x, player_y

     if player_x%GRID_SIZE or player_y%GRID_SIZE: # 
          return PACMAN_CAN_GO

     if GRID_COUNT_X <= (player_x // GRID_SIZE) +2 :
          return [1,0,1,0] # warping zone  R,D,L,U 

     turns=[0]*4 # RLUD

     index_c=int(player_x//GRID_SIZE)
     index_r=int(player_y//GRID_SIZE)
     cell_R=level[index_r][index_c+1]
     cell_D=level[index_r+1][index_c]
     cell_L=level[index_r][index_c-1]
     cell_U=level[index_r-1][index_c]
     
     # check passable direction
     if cell_R in ' ·■':turns[0]=1 # moving left, right wall is passable type, right is passable
     if cell_D in ' ·■':turns[1]=1 # moving up, down wall is passable type, down is passable
     if cell_L in ' ·■':turns[2]=1 # moving right, left wall is passable type, left is passable
     if cell_U in ' ·■':turns[3]=1 # moving down, up wall is passable type, up is passable
     
     return turns

def draw_player(milsec):
     global pacman_moving, player_dir, player_x, player_y

     if PACMAN_CAN_GO[player_dir]:          # move if pacman can move otherwise, stay
          pacman_moving+=1 # for animation 
          if player_dir==0 :               player_x+=player_speed
          if player_dir==1 :               player_y+=player_speed
          if player_dir==2 :               player_x-=player_speed
          if player_dir==3 :               player_y-=player_speed
     else:
          #print('pacman stopped!')
          pass
     
     if player_x<0:
          player_x=GRID_SIZE*GRID_COUNT_X-GRID_SIZE
     elif GRID_SIZE*GRID_COUNT_X-GRID_SIZE < player_x: 
          #player_x= -GRID_SIZE
          player_x=0

     # draw animated pacman at the new position
     img_player=player_images[ (pacman_moving//8) %4] #player animation
     screen.blit(transform.rotate(img_player, -90*player_dir), (player_x, player_y)) # this logic needs RDLU instead of RLUD

def pacman_eats_dot():
     global player_x,player_y,score, powerup_phase
     Cell_Current=level[int(player_y)//GRID_SIZE][int(player_x)//GRID_SIZE]
     if Cell_Current=='·':
          level[int(player_y)//GRID_SIZE][int(player_x)//GRID_SIZE]=' '
          score+=10
     if Cell_Current=='■':
          level[int(player_y)//GRID_SIZE][int(player_x)//GRID_SIZE]=' '
          score+=50
          powerup_phase=1

def powerup_handling():
     global powerup_phase
     if powerup_phase:powerup_phase+=1
     powerup_phase%=600# when 600, stop powerup phase


def draw_HUD():
     #_myrect=Rect(player_center_x,player_center_y,GRID_SIZE*10  ,GRID_SIZE*10)
     _myrect=Rect(GRID_SIZE,GRID_SIZE*(GRID_COUNT_Y),GRID_SIZE*10  ,GRID_SIZE*10)
     _mytext=myfont.render(f'SCORE : {score}', 1, (255,255,0))             
     screen.blit(_mytext,_myrect)

     lives=3
     for i in range(lives-1):
          screen.blit(transform.scale(player_images[0],(HG*2,HG*2)),(GRID_SIZE*(6+i),GRID_SIZE*(GRID_COUNT_Y)))

def keyboard_control():
     global player_dir,player_wish_dir,mainloop ,player_x,player_y# need mainloop to exit by ESC etc
     for e in event.get():
          if e.type==QUIT:
               mainloop=False # x button to close exe
          elif e.type==KEYDOWN:
               if e.key == K_ESCAPE:mainloop = False #Esc key
               else:player_wish_dir = DIR_DICT.get(e.key, player_dir)# change player direction
     # change direction if player wish is available 

     if not (player_x%GRID_SIZE==0 and player_y%GRID_SIZE==0) : return # direction should not change if not on the grid

     if player_dir==player_wish_dir:return # already player wish     
     for i in range(4):
          if player_wish_dir==i and PACMAN_CAN_GO[i]:player_dir = i # when holding down key 

def debugdraw():
     global powerup_phase
     
     player_center_x=int(player_x + HG)# prevent float value for level index
     player_center_y=int(player_y + HG)# prevent float value for level index
     
     index_c=player_center_x//GRID_SIZE
     index_r=player_center_y//GRID_SIZE
     
     _mystr=f'{PACMAN_CAN_GO},{index_r},{index_c},player_x:{player_x},player_center_x:{player_center_x},'
     _mytext=myfont.render(_mystr, 1, (255,255,0))             
     _myrect=Rect(GRID_SIZE*10,GRID_SIZE*(GRID_COUNT_Y),GRID_SIZE*10  ,GRID_SIZE*10)
     screen.blit(_mytext,_myrect)

     _mystr2=f'{player_x%GRID_SIZE},{player_y%GRID_SIZE}, powerup phase : {powerup_phase}'
     _mytext2=myfont.render(_mystr2, 1, (255,255,0))             
     _myrect2=Rect(GRID_SIZE*10,GRID_SIZE*(GRID_COUNT_Y+1),GRID_SIZE*10  ,GRID_SIZE*10)
     screen.blit(_mytext2,_myrect2)

     draw.circle(screen, color='purple', center=(index_c*GRID_SIZE,index_r*GRID_SIZE), radius=5 ,width=0) # player's grid position
     draw.rect(screen, color='purple', rect=(index_c*GRID_SIZE, index_r*GRID_SIZE,GRID_SIZE,GRID_SIZE), width=1 ) # 
     draw.circle(screen, color='red', center=(player_center_x,player_center_y), radius=5 ,width=0) # player's center

     #powerup counter

start_ticks=time.get_ticks()# game initial time to register
mainloop=True
while mainloop:# main loop continues until quit button

     # game time
     clock.tick(FPS)
     millisec=time.get_ticks()-start_ticks # how much milliseconds passed since start

     PACMAN_CAN_GO=update_available_direction() # need to check collision before control (but only on grid)
     
     keyboard_control() # user key input handling

     pacman_eats_dot()
     powerup_handling()

     ###################### draw screen
     screen.fill('black')

     draw_board(millisec)
     draw_player(millisec)
     draw_HUD()
     
     # DEBUG DRAW
     if debugmode:debugdraw()
     
     display.flip()

quit()