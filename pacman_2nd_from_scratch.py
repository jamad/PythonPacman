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
HG =8 # half grid ( minimum : 4 ,  maximum  maybe 16)

G_SIZE=HG*2 # grid size is double of half grid

GRID_COUNT_X=len(boards[0])   #30
GRID_COUNT_Y=len(boards)      #33

HEIGHT_HUD=32

COLOR_WALL = 'blue' # maze color
WALL_THICKNESS= 1 ######## better to have the odd number!  3 is better than 2, 7 is better than 8 !!!!

DIR_DICT= {K_RIGHT:0,K_DOWN:1,K_LEFT:2,K_UP:3}# dictionary for direction

### global variables
player_speed=G_SIZE/16 # can be 1 

score=0
player_x=G_SIZE*GRID_COUNT_X//2
player_y=G_SIZE*24
player_dir=-4
player_wish_dir=-1

pacman_moving=0 # for pacman animation
powerup_phase=0

screen=display.set_mode([GRID_COUNT_X*G_SIZE ,GRID_COUNT_Y*G_SIZE+HEIGHT_HUD])
clock=time.Clock() # originally variable timer 

myfont=font.Font('freesansbold.ttf',G_SIZE//4*3)

#################################################### wall parts image creation
from PIL import Image, ImageDraw

# - generate PIL image with transparent background -
size = G_SIZE
img_corner = Image.new("RGBA", (G_SIZE*2, G_SIZE*2))
my_draw = ImageDraw.Draw(img_corner)
my_rect = (0, 0, G_SIZE, G_SIZE)

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
load_image=lambda type,p:transform.scale(image.load(f'assets/{type}_images/{p}.png'),(G_SIZE*1, G_SIZE*1))
player_images = [load_image('player',i) for i in (1,2,3,2)]# 4 images
ghost_images  = [load_image('ghost',x) for x in 'red pink blue orange'.split()]
spooked_img   = load_image('ghost','powerup') 
dead_img      = load_image('ghost','dead') 

def draw_board(millisec):
     G=G_SIZE
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

     if player_x%G_SIZE or player_y%G_SIZE: # if not on the grid, no change
          return PACMAN_CAN_GO

     if GRID_COUNT_X <= (player_x // G_SIZE) +2 : # warping zone  R,D,L,U 
          return [1,0,1,0] 

     ir,ic=int(player_y//G_SIZE),int(player_x//G_SIZE)
     return [level[r][c]in ' ·■' for r,c in ((ir,ic+1),(ir+1,ic),(ir,ic-1),(ir-1,ic)) ]# RLUD

def draw_player(milsec):
     global pacman_moving, player_dir, player_x, player_y

     if PACMAN_CAN_GO[player_dir]:          # move if pacman can move otherwise, stay
          pacman_moving+=1 # for animation 
          if player_dir==0 :player_x+=player_speed
          if player_dir==1 :player_y+=player_speed
          if player_dir==2 :player_x-=player_speed
          if player_dir==3 :player_y-=player_speed
     else:
          #print('pacman stopped!')
          pass
     
     if player_x<0:
          player_x=G_SIZE*GRID_COUNT_X-G_SIZE
     elif G_SIZE*GRID_COUNT_X-G_SIZE < player_x: 
          #player_x= -GRID_SIZE
          player_x=0

     # draw animated pacman at the new position
     img_player=player_images[ (pacman_moving//8) %4] #player animation
     screen.blit(transform.rotate(img_player, -90*player_dir), (player_x, player_y)) # this logic needs RDLU instead of RLUD

def pacman_eats_dot():
     global player_x,player_y,score, powerup_phase
     Cell_Current=level[int(player_y)//G_SIZE][int(player_x)//G_SIZE]
     if Cell_Current=='·':
          level[int(player_y)//G_SIZE][int(player_x)//G_SIZE]=' '
          score+=10
     if Cell_Current=='■':
          level[int(player_y)//G_SIZE][int(player_x)//G_SIZE]=' '
          score+=50
          powerup_phase=1

def powerup_handling():
     global powerup_phase
     if powerup_phase:powerup_phase+=1
     powerup_phase%=600# when 600, stop powerup phase


def draw_HUD():
     #_myrect=Rect(player_center_x,player_center_y,GRID_SIZE*10  ,GRID_SIZE*10)
     _myrect=Rect(G_SIZE,G_SIZE*(GRID_COUNT_Y),G_SIZE*10  ,G_SIZE*10)
     _mytext=myfont.render(f'SCORE : {score}', 1, (255,255,0))             
     screen.blit(_mytext,_myrect)

     lives=3
     for i in range(lives-1):
          screen.blit(transform.scale(player_images[0],(HG*2,HG*2)),(G_SIZE*(6+i),G_SIZE*(GRID_COUNT_Y)))

def keyboard_control():
     global player_dir,player_wish_dir,mainloop ,player_x,player_y# need mainloop to exit by ESC etc
     for e in event.get():
          if e.type==QUIT:
               mainloop=False # x button to close exe
          elif e.type==KEYDOWN:
               if e.key == K_ESCAPE:mainloop = False #Esc key
               else:player_wish_dir = DIR_DICT.get(e.key, player_dir)# change player direction
     # change direction if player wish is available 

     if not (player_x%G_SIZE==0 and player_y%G_SIZE==0) : return # direction should not change if not on the grid

     if player_dir==player_wish_dir:return # already player wish     
     for i in range(4):
          if player_wish_dir==i and PACMAN_CAN_GO[i]:player_dir = i # when holding down key 

def debugdraw():
     global powerup_phase, player_x, player_y
     
     player_x=int(player_x )# prevent float value for level index
     player_y=int(player_y )# prevent float value for level index
     
     index_c=player_x//G_SIZE
     index_r=player_y//G_SIZE
     
     _mystr=f'{PACMAN_CAN_GO},{index_r},{index_c},player_x:{player_x},'
     _mytext=myfont.render(_mystr, 1, (255,255,0))             
     _myrect=Rect(G_SIZE*10,G_SIZE*(GRID_COUNT_Y),G_SIZE*10  ,G_SIZE*10)
     screen.blit(_mytext,_myrect)

     _mystr2=f'x%G_SIZE:{player_x%G_SIZE},y%G_SIZE:{player_y%G_SIZE}, powerup phase : {powerup_phase}'
     _mytext2=myfont.render(_mystr2, 1, (255,255,0))             
     _myrect2=Rect(G_SIZE*10,G_SIZE*(GRID_COUNT_Y+1),G_SIZE*10  ,G_SIZE*10)
     screen.blit(_mytext2,_myrect2)

     draw.circle(screen, color='purple', center=(index_c*G_SIZE,index_r*G_SIZE), radius=5 ,width=0) # player's grid position
     draw.rect(screen, color='purple', rect=(index_c*G_SIZE, index_r*G_SIZE,G_SIZE,G_SIZE), width=1 ) # 

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