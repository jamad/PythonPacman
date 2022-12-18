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

print()
init()

GRID_SIZE=24 #pixel for unit block

GRID_COUNT_X=len(boards[0])   #30
GRID_COUNT_Y=len(boards)      #33

HEIGHT_HUD=32

COLOR_WALL = 'blue' # maze color
WALL_THICKNESS= 5 ######## better to have the odd number!  3 is better than 2, 7 is better than 8 !!!!

FPS=60

screen=display.set_mode([GRID_COUNT_X*GRID_SIZE ,GRID_COUNT_Y*GRID_SIZE+HEIGHT_HUD])
clock=time.Clock() # originally variable timer 
myfont=font.Font('freesansbold.ttf',20)


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

player_x=GRID_SIZE*2
player_y=GRID_SIZE*2

player_dir=0

PACMAN_CAN_GO=[0]*4# direction

def update_available_direction(player_dir,player_x, player_y):
     player_center_x=int(player_x + GRID_SIZE/2)# prevent float value for level index
     player_center_y=int(player_y + GRID_SIZE/2)# prevent float value for level index

     if GRID_COUNT_X <= (player_x // GRID_SIZE) +1 :return [1,1,0,0] # warping zone

     turns=[0]*4 # RLUD

     space_visual=(GRID_SIZE - WALL_THICKNESS) // 2  # actual collision to the visual of the wall # originally num3
     c=player_center_x//GRID_SIZE
     r=player_center_y//GRID_SIZE
     cell_L=level[r][(player_center_x - space_visual)//GRID_SIZE]
     cell_R=level[r][(player_center_x + space_visual)//GRID_SIZE]
     cell_U=level[(player_center_y - space_visual)//GRID_SIZE][c]
     cell_D=level[(player_center_y + space_visual)//GRID_SIZE][c]
     
     # check passable direction
     if cell_R in ' ·■':turns[0]=1 # moving left, right wall is passable type, right is passable
     if cell_L in ' ·■':turns[1]=1 # moving right, left wall is passable type, left is passable
     if cell_U in ' ·■':turns[2]=1 # moving down, up wall is passable type, up is passable
     if cell_D in ' ·■':turns[3]=1 # moving up, down wall is passable type, down is passable


     # DEBUG DRAW

     _myrect=Rect(player_center_x,player_center_y,GRID_SIZE*10  ,GRID_SIZE*10)
     _mystr=f'{PACMAN_CAN_GO},{r},{c},{player_x},{player_center_x},{c*GRID_SIZE}'
     _mytext=font.Font('freesansbold.ttf', 12).render(_mystr, 1, (255,255,0))             
     screen.blit(_mytext,_myrect)

     
     draw.circle(screen, color='purple', center=(c*GRID_SIZE,r*GRID_SIZE), radius=5 ,width=0) # player's grid position
     draw.rect(screen, color='purple', rect=(c*GRID_SIZE, r*GRID_SIZE,GRID_SIZE,GRID_SIZE), width=1 ) # 
     draw.circle(screen, color='red', center=(player_center_x,player_center_y), radius=5 ,width=0) # player's center
     

     return turns


def draw_player(milsec,pacman_dir, player_x, player_y):
     
     player_speed=GRID_SIZE//6
     if PACMAN_CAN_GO[pacman_dir]:# move if pacman can move otherwise, stay
          if pacman_dir==0 :player_x+=player_speed
          if pacman_dir==1 :player_x-=player_speed
          if pacman_dir==2 :player_y-=player_speed
          if pacman_dir==3 :player_y+=player_speed

     pos=(player_x, player_y)
     img_player=player_images[ (milsec//100) %4 ] #player animation
     if pacman_dir == 0:      screen.blit(img_player, pos)
     elif pacman_dir == 1:    screen.blit(transform.flip(img_player, True, False), pos)
     elif pacman_dir == 2:    screen.blit(transform.rotate(img_player, 90), pos)
     elif pacman_dir == 3:    screen.blit(transform.rotate(img_player, -90), pos)

     return (player_x,player_y)

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
               else:player_dir={K_RIGHT:0,K_LEFT:1,K_UP:2,K_DOWN:3}.get(e.key, player_dir)# change player direction


     ###################### draw screen
     screen.fill('black')

     PACMAN_CAN_GO=update_available_direction(player_dir,player_x, player_y)
     

     draw_board(millisec)
     (player_x,player_y)=draw_player(millisec,player_dir,player_x,player_y)
     
     
     display.flip()

quit()




    
