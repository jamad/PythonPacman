#screen.blit(transform.rotate(img_player, 90*player_dir), pos) # this logic needs RDLU instead of RLUD
from pygame import *
import copy
from math import pi, cos, sin

debugmode=0

DIR_DICT= {K_RIGHT:0,K_DOWN:1,K_LEFT:2,K_UP:3}# dictionary for direction 

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
──────┘·└┘ │!!!!!!│ └┘·└──────
       ·   │!!!!!!│   ·       
──────┐·┌┐ │!!!!!!│ ┌┐·┌──────
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
#g_level = copy.deepcopy(LEVEL_TEMPLATE)

init()
FPS=120 # algorithm should be faster to keep FPS!  # maybe 120 is maximum as 240 did not work

HG =12 # half grid ( minimum : 4 ,  maximum  maybe 16)

G_SIZE=HG*2 # grid size is double of half grid
G_COUNT_X=len(LEVEL_TEMPLATE[0])   #30
G_COUNT_Y=len(LEVEL_TEMPLATE)      #33
RX=range(G_COUNT_X)
RY=range(G_COUNT_Y)

#### create dictionary for turns! 
DIRECTION={} #  key : (column, row)   # exception for warp row=15, col=29
for x in RX:
     for y in RY:
          if LEVEL_TEMPLATE[y][x] not in ' ·■═!':
               DIRECTION[(x,y)]=[0]*4 # in the wall
          else : 
               DIRECTION[(x,y)]=[{' ':1,'·':1,'■':1,'═':2,'!':3}.get(LEVEL_TEMPLATE[(y+dy)%G_COUNT_Y][(x+dx)%G_COUNT_X],0) for dy,dx in ((0,1),(1,0),(0,-1),(-1,0))]     # creat dictionary

print('DIRECTION data creation done',len(DIRECTION))
print(DIRECTION[(12,17)])

#inf=99 # largest number because G_COUNT_X + G_COUNT_Y < 99

DP=[[[[99 for ct in RX]for rt in RY] for c in RX] for r in RY]# [r][c][rt][ct] has minimum cell count for (r,c) to reach (rt,ct)

print('DP initialized')

for r in RY:
     print(r)
     for c in RX:
          if DIRECTION[(c,r)]==[0,0,0,0]:continue # in the wall
          DP[r][c][r][c]=0# same cell
          Q=[(r,c,r,c,0)]
          for r,c,rt,ct,count in Q:
               RDLU=((rt,ct+1),(rt+1,ct),(rt,ct-1),(rt-1,ct))
               TURN=DIRECTION[(ct,rt)]
               for u,v in (RDLU[i] for i in range(4) if TURN[i]):
                    u%=G_COUNT_Y
                    v%=G_COUNT_X
                    cur=DP[r][c][u][v]
                    tmp=count+1
                    if tmp<cur:# new record
                         DP[r][c][u][v]=tmp
                         Q.append((r,c,u,v,tmp))

print('DP created. the following is the example')
for R in  DP[16][12]:print(' '.join([f'{x:02}' if x<99 else '--' for x in R]))
for R in  DP[17][12]:print(' '.join([f'{x:02}' if x<99 else 'xx' for x in R]))
#for R in  DP[2][2]:print(' '.join([f'{x:02}' if x<99 else '--' for x in R]))



BFS_SOLUTION={} # output : direction , input (x,y, targetx,targety)  # better to calculate here if possible

for x,y in DIRECTION:
     Q=[(x,y,[])] 
     VISITED=set()
     for u,v,_direction in Q:
          u%=G_COUNT_X # very important , without it, index can be expanded infinitely
          v%=G_COUNT_Y # very important , without it, index can be expanded infinitely

          k=(x,y,u,v)
          if k in VISITED:continue # no need to update because count should be smaller by first found in BFS
          VISITED.add(k)

          BFS_SOLUTION[k]=_direction and _direction[0] or 0 # first direction
          _r,_d,_l,_u = DIRECTION[(u,v)]
          if _r:Q.append(( u+1 , v , _direction+[0]))
          if _d:Q.append(( u,  v+1 , _direction+[1]))
          if _l:Q.append(( u-1 , v , _direction+[2]))
          if _u:Q.append(( u  ,v-1 , _direction+[3]))
          
print('len(BFS_SOLUTION)',len(BFS_SOLUTION))

HEIGHT_HUD_UPPER=HG*2
HEIGHT_HUD_LOWER=HG*2

COLOR_WALL = 'blue' # maze color
WALL_THICKNESS= 1 ######## better to have the odd number!  3 is better than 2, 7 is better than 8 !!!!

### global variables
g_player_speed=HG/4 # speed can be float number (for example, 0.25)

g_screen=display.set_mode([G_COUNT_X*G_SIZE ,HEIGHT_HUD_UPPER+G_COUNT_Y*G_SIZE+HEIGHT_HUD_LOWER])
g_clock=time.Clock() # originally variable timer 

ALL_FONTS=font.get_fonts()
g_myfont=font.SysFont(ALL_FONTS[1], G_SIZE//4*3)
g_my_small_font=font.SysFont(ALL_FONTS[1], 7)
g_my_bonus_font=font.SysFont(ALL_FONTS[1], 14)

#################################################### wall parts image creation
from PIL import Image, ImageDraw
img_corner = Image.new("RGBA", (G_SIZE*2, G_SIZE*2)) # - generate PIL image with transparent background -
my_draw = ImageDraw.Draw(img_corner)

ANGLE_SEGMENTS=32 # arc resolution
a=pi/2/ANGLE_SEGMENTS
POINTS=[(HG*cos(a*i)  ,HG*sin(a*i))for i in range(ANGLE_SEGMENTS+1)]
for p1,p2 in zip(POINTS,POINTS[1:]):
     my_draw.line((p1, p2), fill=COLOR_WALL, width=WALL_THICKNESS)

# - convert into PyGame image -
corner_image = image.fromstring(img_corner.tobytes(), img_corner.size, img_corner.mode)
#################################################### wall parts image end

# image assets
load_image=lambda type,p:transform.scale(image.load(f'assets/{type}_images/{p}.png'),(G_SIZE, G_SIZE))
player_images = [load_image('player',i) for i in (1,2,3,2)]# 4 images
ghost_images  = [load_image('ghost',x) for x in 'red pink blue orange'.split()]
spooked_img   = load_image('ghost','powerup') 
dead_img      = load_image('ghost','dead') 

def restart_game():
     global g_score, g_lives, g_level
     g_score=0
     g_lives=3
     
     g_level = copy.deepcopy(LEVEL_TEMPLATE)


def reset_game():
     # 207:29
     global ghosts, g_lives, g_score, g_counter_eaten_ghost, g_player_x, g_player_y, g_player_dir, g_player_wish_dir, g_pacman_moving, g_powerup_phase     
     g_counter_eaten_ghost=0
     g_player_x=G_SIZE*G_COUNT_X//2
     g_player_y=G_SIZE*24
     g_player_dir=-4
     g_player_wish_dir=-1
     g_pacman_moving=0 # for pacman animation
     g_powerup_phase=0
     
     ghosts=[Ghost(i) for i in range(4)] # instantiated 4 ghosts


# ghost class
class Ghost:
     def __init__(self,id):
          self.id=id
          self.img=ghost_images[id]

          self.x=G_SIZE*(G_COUNT_X//2 + id-3)
          self.y=G_SIZE*(G_COUNT_Y//2)
          
          self.target_x=0
          self.target_y=0
          self.speed=2
          self.spooked=False
          self.dead=False

          self.direction=-1
          self.turns=[0]*4      
          self.rect=None # dummy

     def update(self):
          global g_powerup_phase

          # logic for ghost wish
          self.target_x=g_player_x  if not self.spooked else  (G_SIZE*2,G_SIZE*27)[g_player_x<G_SIZE*G_COUNT_X//2]
          self.target_y=g_player_y  if not self.spooked else (G_SIZE*2,G_SIZE*27)[g_player_y<G_SIZE*G_COUNT_Y//2]

          if self.dead:
               self.target_x=380
               self.target_y=400

          x,y=int(self.x//G_SIZE),int(self.y//G_SIZE)
          tx,ty=int(self.target_x//G_SIZE),int(self.target_y//G_SIZE)
          
          if self.x%G_SIZE==self.y%G_SIZE==0: # update if on the grid

               # the following can solve exception : warping tunnel
               x%=G_COUNT_X
               y%=G_COUNT_Y
               tx%=G_COUNT_X
               ty%=G_COUNT_Y
               
               # if ghost is in box. no more dead, no more spooked
               if g_level[y][x]=='!':
                    self.dead=False
                    self.spooked=False

               k=(x,y,tx,ty)
               wish_direction =BFS_SOLUTION.get(k,[0,0,0,0])

               # disabled the following because ghost move got worse with DP
               #CR=(DP[y][x+1][ty][tx],0)
               #CD=(DP[y+1][x][ty][tx],1)
               #CL=(DP[y][x+1][ty][tx],2)
               #CU=(DP[y-1][x][ty][tx],3)
               #LIST=( CR,CD,CL,CU )
               #wish_direction=min( LIST )[1]

               self.turns = DIRECTION[(x,y)] 

               if self.turns[wish_direction]:
                    self.direction = wish_direction # change direction if  wish is available 
               
          # speed change 
          if self.dead: 
               self.speed=4  
               self.x=self.x//4 * 4 # warp a bit so that on the grid
               self.y=self.y//4 * 4 # warp a bit so that on the grid
          elif self.spooked:self.speed=1  # half
          else: self.speed=2

          # move ghost
          if self.turns[self.direction]:          # move if pacman can move otherwise, stay
               dx={0:1,2:-1}.get(self.direction,0)
               dy={1:1,3:-1}.get(self.direction,0)
               self.x+=dx*self.speed 
               self.y+=dy*self.speed 
          
          # if warp tunnel
          if self.x<-G_SIZE:          self.x=G_SIZE*G_COUNT_X
          if G_SIZE*G_COUNT_X < self.x: self.x=-G_SIZE

     def draw(self):
          image=self.img
          if self.spooked:    image=spooked_img
          if self.dead:       image=dead_img
          self.rect = g_screen.blit(image, (self.x, self.y + HEIGHT_HUD_UPPER, G_SIZE, G_SIZE))

def pacman_eats_dot():
     global g_player_x,g_player_y,g_score, g_powerup_phase, g_level ,g_counter_eaten_ghost

     y=int(g_player_y)//G_SIZE
     x=int(g_player_x)//G_SIZE
     y%=G_COUNT_Y
     x%=G_COUNT_X
     Cell_Current=g_level[y][x]
     if Cell_Current=='·':
          g_level[y][x]=' '
          g_score+=10
     if Cell_Current=='■':
          g_level[y][x]=' '
          g_score+=50
          g_powerup_phase=1
          g_counter_eaten_ghost=0 #reset the counter for score 
          for g in ghosts:    g.spooked=True # make the ghost spook here

def powerup_handling():
     global g_powerup_phase
     if g_powerup_phase:g_powerup_phase+=1

     g_powerup_phase%=600# when 600, stop powerup phase

     if g_powerup_phase==0:
          for g in ghosts:
               g.spooked=False # powerup effect was gone!

def draw_board(millisec):
     G=G_SIZE
     for i in RY:
          for j in RX:
               x,y=G*j,G*i + HEIGHT_HUD_UPPER
               c=g_level[i][j]
               if c=='│':draw.line(   g_screen, COLOR_WALL, (x+HG,y),(x+HG, y+G),WALL_THICKNESS)
               if c=='─':draw.line(   g_screen, COLOR_WALL, (x,y+HG),(x+G, y+HG),WALL_THICKNESS)
               if c=='┘':g_screen.blit(corner_image, (x,y))# <- display image
               if c=='┐':g_screen.blit(transform.rotate(corner_image, 90),     (x,y-G))
               if c=='┌':g_screen.blit(transform.rotate(corner_image, 180),    (x-G,y-G))
               if c=='└':g_screen.blit(transform.rotate(corner_image, -90),    (x-G,y))
               if c=='═':draw.line(   g_screen, 'white', (x,y+HG), (x+G, y+HG), WALL_THICKNESS)
               if c=='·':draw.circle( g_screen, 'white', (x+HG, y+HG), G//8)
               if c=='■':
                    radius=(G*1.5//4,G*1.5*5//16)[millisec%(FPS*4)<FPS*2]
                    draw.circle( g_screen, 'white', (x+HG, y+HG), radius )

def draw_player():
     global g_pacman_moving, g_player_dir, g_player_x, g_player_y
     img_player=player_images[ (g_pacman_moving//8) %4] #player animation
     g_screen.blit(transform.rotate(img_player, -90*g_player_dir), (g_player_x, g_player_y + HEIGHT_HUD_UPPER))

def draw_HUD():
     global g_lives
     _myrect=Rect(G_SIZE,G_SIZE*(.5),G_SIZE*10  ,G_SIZE*10)
     _mytext=g_myfont.render(f'SCORE : {g_score}', 1, (255,255,0))             
     g_screen.blit(_mytext,_myrect)

     for i in range(g_lives-1):
          g_screen.blit(transform.scale(player_images[0],(HG*2,HG*2)),(G_SIZE*(1+i),G_SIZE*(G_COUNT_Y+.8)))

     value=g_clock.get_fps()
     _fps_t = g_myfont.render(f'FPS: {value:.1f}' , 1, "red" if  value < FPS*.9 else 'green' )
     g_screen.blit(_fps_t,(G_SIZE*(G_COUNT_X-5),HG))

def keyboard_control():
     global g_player_dir,g_player_wish_dir,g_mainloop# need mainloop to exit by ESC etc
     for e in event.get():
          if e.type==QUIT:
               g_mainloop=False # x button to close exe
          elif e.type==KEYDOWN:
               if e.key == K_ESCAPE:g_mainloop = False #Esc key
               else:g_player_wish_dir = DIR_DICT.get(e.key, g_player_dir)# change player direction

def player_direction_change():
     global g_player_x,g_player_y, g_player_wish_dir, g_player_dir
     index_r,index_c=int(g_player_y//G_SIZE),int(g_player_x//G_SIZE)

     PACMAN_CAN_GO = DIRECTION.get( (index_c,index_r), [1,0,1,0] ) # exception : warping tunnel

     if PACMAN_CAN_GO[g_player_wish_dir]==1: # because 2 is only for ghost to pass
          g_player_dir = g_player_wish_dir   # change direction if player wish is available 

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
     if g_player_x<-G_SIZE:        g_player_x=G_SIZE*G_COUNT_X
     elif G_SIZE*G_COUNT_X <  g_player_x: g_player_x=-G_SIZE

def debugdraw():
     global g_powerup_phase, g_player_x, g_player_y
     
     px=int(g_player_x )# prevent float value for level index
     py=int(g_player_y )# prevent float value for level index
     
     index_c=px//G_SIZE
     index_r=py//G_SIZE
     
     movable=['RDLU'[i] for i in range(4) if PACMAN_CAN_GO[i]]
     _mystr=f'{index_r:02d},{index_c:02d},player_x:{px},{movable}'
     _mytext=g_myfont.render(_mystr, 1, (255,255,0))             
     _myrect=Rect(G_SIZE*10,G_SIZE*0.5,G_SIZE*10  ,G_SIZE*10)
     g_screen.blit(_mytext,_myrect)

     _mystr2=f'x%G_SIZE:{px%G_SIZE:02d},y%G_SIZE:{py%G_SIZE:02d}, powerup phase : {g_powerup_phase}'
     _mytext2=g_myfont.render(_mystr2, 1, (255,255,0))             
     _myrect2=Rect(G_SIZE*10,G_SIZE*(G_COUNT_Y+1),G_SIZE*10  ,G_SIZE*10)
     g_screen.blit(_mytext2,_myrect2)

     draw.circle(g_screen, color='purple', center=(index_c*G_SIZE,index_r*G_SIZE + HEIGHT_HUD_UPPER), radius=5 ,width=0) # player's grid position
     draw.rect(g_screen, color='purple', rect=(index_c*G_SIZE, index_r*G_SIZE + HEIGHT_HUD_UPPER,G_SIZE,G_SIZE), width=1 ) # 

     # direction data check
     for (x,y) in DIRECTION:
          data=DIRECTION[(x,y)]
          if data==[]:data=[0,0,0,0]

          #_mystr=''.join('>v<^'[i] for i in (0,1,2,3) if data[i] ) 
          _mystr=''.join('>v<^'[i] for i in (2,3,1,0) if data[i] )  #'<^v>' was better for debug display
          
          _mytext=g_my_small_font.render(_mystr, 1, (255,255,0))            
          _myrect= Rect(x*G_SIZE, y*G_SIZE + HEIGHT_HUD_UPPER,G_SIZE,G_SIZE)
          g_screen.blit(_mytext,_myrect)

restart_game()
reset_game()

pause=0

start_ticks=time.get_ticks()# game initial time to register
g_mainloop=True
while g_mainloop:# main loop continues until quit button

     # game time
     
     g_clock.tick(FPS)

     g_millisec=time.get_ticks()-start_ticks # how much milliseconds passed since start
     
     if pause:
          pause-=1
          continue

     keyboard_control() # user key input handling

     if g_player_x%G_SIZE==g_player_y%G_SIZE==0 :# process on the grid
          PACMAN_CAN_GO=player_direction_change()# direction change + available direciton data update

     player_move()
     pacman_eats_dot()
     powerup_handling()

     ###################### draw screen
     g_screen.fill('black')

     for ghost in ghosts:ghost.update() # for debug

     draw_board(g_millisec)
     draw_player()

     for ghost in ghosts: ghost.draw()
     draw_HUD()

     if debugmode:debugdraw()# DEBUG DRAW
     
     # draw pacman collision 
     player_collision = draw.circle(g_screen, 'pink', (g_player_x + HG,g_player_y + HG +HEIGHT_HUD_UPPER),21,2)
     for g in ghosts:
          if player_collision.colliderect( g.rect ):
               
               if g.dead:continue # nothing happens

               pause=FPS # 1 sec pause when collision except for dead

               if g.spooked:
                    g_counter_eaten_ghost+=1
                    g.dead=True # now ghost is dead
                    print('add score here')
                    
                    bonus=100*2**(g_counter_eaten_ghost)
                    g_score+=bonus
                    
                    _mytext=g_my_bonus_font.render(f'{bonus}', 1, (255,255,0))            
                    _myrect= Rect(g.x, g.y + HEIGHT_HUD_UPPER,G_SIZE,G_SIZE)
                    g_screen.blit(_mytext,_myrect)
               else:     
                    #pacman dead
                    g_lives -=1
                    if g_lives==0:
                         print('game over')
                         restart_game()
                    
                    reset_game()

     display.flip()

quit()

# todo : gameover message
# create 3 variation movement
# sound effect, restart, winning message