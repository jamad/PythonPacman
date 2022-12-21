#screen.blit(transform.rotate(img_player, 90*player_dir), pos) # this logic needs RDLU instead of RLUD
from pygame import *
import copy
from math import pi, cos, sin

BOARD_DATA='''\
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

LEVEL_TEMPLATE=[list(s) for s in BOARD_DATA.split('\n')]# 0 should not be trimmed!
level = copy.deepcopy(LEVEL_TEMPLATE)

init()
FPS=120
HG =12 # half grid ( minimum : 4 ,  maximum  maybe 16)

G_SIZE=HG*2 # grid size is double of half grid

GRID_COUNT_X=len(LEVEL_TEMPLATE[0])   #30
GRID_COUNT_Y=len(LEVEL_TEMPLATE)      #33

HEIGHT_HUD=32

COLOR_WALL = 'blue' # maze color
WALL_THICKNESS= 1 ######## better to have the odd number!  3 is better than 2, 7 is better than 8 !!!!

DIR_DICT= {K_RIGHT:0,K_DOWN:1,K_LEFT:2,K_UP:3}# dictionary for direction

### global variables
g_player_speed=HG/4 # speed can be float number (for example, 0.25)

g_lives=3
g_score=0
g_player_x=G_SIZE*GRID_COUNT_X//2
g_player_y=G_SIZE*24
g_player_dir=-4
g_player_wish_dir=-1
g_pacman_moving=0 # for pacman animation
g_powerup_phase=0

g_screen=display.set_mode([GRID_COUNT_X*G_SIZE ,GRID_COUNT_Y*G_SIZE+HEIGHT_HUD])
g_clock=time.Clock() # originally variable timer 

g_myfont=font.Font('freesansbold.ttf',G_SIZE//4*3)

#################################################### wall parts image creation
from PIL import Image, ImageDraw

# - generate PIL image with transparent background -
img_corner = Image.new("RGBA", (G_SIZE*2, G_SIZE*2))
g_my_draw = ImageDraw.Draw(img_corner)

ANGLE_SEGMENTS=32 # arc resolution
a=pi/2/ANGLE_SEGMENTS
POINTS=[(HG*cos(a*i)  ,HG*sin(a*i))for i in range(ANGLE_SEGMENTS+1)]
for p1,p2 in zip(POINTS,POINTS[1:]):
     g_my_draw.line((p1, p2), fill=COLOR_WALL, width=WALL_THICKNESS)

# - convert into PyGame image -
corner_img = image.fromstring(img_corner.tobytes(), img_corner.size, img_corner.mode)
#################################################### wall parts image end

# image assets
load_image=lambda type,p:transform.scale(image.load(f'assets/{type}_images/{p}.png'),(G_SIZE*1, G_SIZE*1))
player_images = [load_image('player',i) for i in (1,2,3,2)]# 4 images
ghost_images  = [load_image('ghost',x) for x in 'red pink blue orange'.split()]
spooked_img   = load_image('ghost','powerup') 
dead_img      = load_image('ghost','dead') 

def pacman_eats_dot():
     global g_player_x,g_player_y,g_score, g_powerup_phase
     try:
          Cell_Current=level[int(g_player_y)//G_SIZE][int(g_player_x)//G_SIZE]
          if Cell_Current=='·':
               level[int(g_player_y)//G_SIZE][int(g_player_x)//G_SIZE]=' '
               g_score+=10
          if Cell_Current=='■':
               level[int(g_player_y)//G_SIZE][int(g_player_x)//G_SIZE]=' '
               g_score+=50
               g_powerup_phase=1
     except:
          print('warping now, so no cells exists')

def powerup_handling():
     global g_powerup_phase
     if g_powerup_phase:g_powerup_phase+=1
     g_powerup_phase%=600# when 600, stop powerup phase

def draw_board(millisec):
     G=G_SIZE
     for i in range(GRID_COUNT_Y):
          for j in range(GRID_COUNT_X):
               x,y=G*j,G*i
               c=level[i][j]
               if c=='│':draw.line(   g_screen, COLOR_WALL, (x+HG,y),(x+HG, y+G),WALL_THICKNESS)
               if c=='─':draw.line(   g_screen, COLOR_WALL, (x,y+HG),(x+G, y+HG),WALL_THICKNESS)
               if c=='┘':g_screen.blit(corner_img, (x,y))# <- display image
               if c=='┐':g_screen.blit(transform.rotate(corner_img, 90),     (x,y-G))
               if c=='┌':g_screen.blit(transform.rotate(corner_img, 180),    (x-G,y-G))
               if c=='└':g_screen.blit(transform.rotate(corner_img, -90),    (x-G,y))
               if c=='═':draw.line(   g_screen, 'white', (x,y+HG), (x+G, y+HG), WALL_THICKNESS)
               if c=='·':draw.circle( g_screen, 'white', (x+HG, y+HG), G//8)
               if c=='■':
                    radius=(G*1.5//4,G*1.5*5//16)[millisec%(FPS*4)<FPS*2]
                    draw.circle( g_screen, 'white', (x+HG, y+HG), radius )

def draw_player():
     global g_pacman_moving, g_player_dir, g_player_x, g_player_y
     img_player=player_images[ (g_pacman_moving//8) %4] #player animation
     g_screen.blit(transform.rotate(img_player, -90*g_player_dir), (g_player_x, g_player_y))

def draw_HUD():
     _myrect=Rect(G_SIZE,G_SIZE*(GRID_COUNT_Y),G_SIZE*10  ,G_SIZE*10)
     _mytext=g_myfont.render(f'SCORE : {g_score}', 1, (255,255,0))             
     g_screen.blit(_mytext,_myrect)

     for i in range(g_lives-1):
          g_screen.blit(transform.scale(player_images[0],(HG*2,HG*2)),(G_SIZE*(6+i),G_SIZE*(GRID_COUNT_Y)))

def keyboard_control():
     global g_player_dir,g_player_wish_dir,mainloop# need mainloop to exit by ESC etc
     for e in event.get():
          if e.type==QUIT:
               mainloop=False # x button to close exe
          elif e.type==KEYDOWN:
               if e.key == K_ESCAPE:mainloop = False #Esc key
               else:g_player_wish_dir = DIR_DICT.get(e.key, g_player_dir)# change player direction

def player_direction_change():
     global g_player_x,g_player_y, g_player_wish_dir, g_player_dir
     index_r,index_c=int(g_player_y//G_SIZE),int(g_player_x//G_SIZE)

     if GRID_COUNT_X -2 <= index_c  : # warping zone  R,D,L,U 
          PACMAN_CAN_GO= [1,0,1,0] 
     else:
          PACMAN_CAN_GO= [level[index_r+r][index_c+c]in' ·■' for r,c in ((0,1),(1,0),(0,-1),(-1,0)) ]

     if PACMAN_CAN_GO[g_player_wish_dir]:
          g_player_dir = g_player_wish_dir # change direction if player wish is available 

     return PACMAN_CAN_GO

def player_move():
     global g_player_x, g_player_y, g_pacman_moving
     if PACMAN_CAN_GO[g_player_dir]:          # move if pacman can move otherwise, stay
          dx={0:1,2:-1}.get(g_player_dir,0)
          dy={1:1,3:-1}.get(g_player_dir,0)
          g_player_x+=dx*g_player_speed
          g_player_y+=dy*g_player_speed
          g_pacman_moving+=1 # for animation 
     
     # if warp tunnel
     if g_player_x<-G_SIZE:          g_player_x=G_SIZE*(GRID_COUNT_X)
     elif G_SIZE*(GRID_COUNT_X) < g_player_x: g_player_x=-G_SIZE

def debugdraw():
     global g_powerup_phase, g_player_x, g_player_y
     
     px=int(g_player_x )# prevent float value for level index
     py=int(g_player_y )# prevent float value for level index
     
     index_c=px//G_SIZE
     index_r=py//G_SIZE
     
     _mystr=f'{PACMAN_CAN_GO},{index_r},{index_c},player_x:{px},'
     _mytext=g_myfont.render(_mystr, 1, (255,255,0))             
     _myrect=Rect(G_SIZE*10,G_SIZE*(GRID_COUNT_Y),G_SIZE*10  ,G_SIZE*10)
     g_screen.blit(_mytext,_myrect)

     _mystr2=f'x%G_SIZE:{px%G_SIZE},y%G_SIZE:{py%G_SIZE}, powerup phase : {g_powerup_phase}'
     _mytext2=g_myfont.render(_mystr2, 1, (255,255,0))             
     _myrect2=Rect(G_SIZE*10,G_SIZE*(GRID_COUNT_Y+1),G_SIZE*10  ,G_SIZE*10)
     g_screen.blit(_mytext2,_myrect2)

     draw.circle(g_screen, color='purple', center=(index_c*G_SIZE,index_r*G_SIZE), radius=5 ,width=0) # player's grid position
     draw.rect(g_screen, color='purple', rect=(index_c*G_SIZE, index_r*G_SIZE,G_SIZE,G_SIZE), width=1 ) # 

start_ticks=time.get_ticks()# game initial time to register
mainloop=True
while mainloop:# main loop continues until quit button

     # game time
     g_clock.tick(FPS)
     millisec=time.get_ticks()-start_ticks # how much milliseconds passed since start
     
     keyboard_control() # user key input handling

     if (g_player_x%G_SIZE==g_player_y%G_SIZE==0) :# process on the grid
          PACMAN_CAN_GO=player_direction_change()# direction change + available direciton data update

     player_move()
     pacman_eats_dot()
     powerup_handling()

     ###################### draw screen
     g_screen.fill('black')

     draw_board(millisec)
     draw_player()
     draw_HUD()

     if 1:debugdraw()# DEBUG DRAW
     
     display.flip()

quit()