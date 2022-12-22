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
g_level = copy.deepcopy(LEVEL_TEMPLATE)



init()
FPS=120 # algorithm should be faster to keep FPS!

HG =12 # half grid ( minimum : 4 ,  maximum  maybe 16)

G_SIZE=HG*2 # grid size is double of half grid

GRID_COUNT_X=len(LEVEL_TEMPLATE[0])   #30
GRID_COUNT_Y=len(LEVEL_TEMPLATE)      #33


#### create dictionary for turns! 
from collections import defaultdict
DIRECTION={} #  key : (column, row) 
DIRECTION[(29,15)]=[1, 0, 1, 0] # exception for warp row=15, col=29
Q=[(2,2)]
for (x,y) in Q:
     if (x,y) not in DIRECTION:
          data=[]
          # creat dictionary
          r,c=y,x
          if r<0 or c<0:continue
          for dr,dc in ((0,1),(1,0),(0,-1),(-1,0)): # RDLU
               try:
                    cell=g_level[r+dr][c+dc]
                    if cell in ' ·■═':
                         data.append(2 if cell=='═' else 1)
                         Q.append((c+dc, r+dr)) # new x,y to add
                    else:data.append(0)
               except Exception as e:
                    print(e,r,c)
          DIRECTION[(x,y)]=data

#for k in sorted(DIRECTION):     print(k,DIRECTION[k])
print('DIRECTION data creation done')          

BFS_SOLUTION={} # output : direction , input (x,y, targetx,targety)

HEIGHT_HUD_UPPER=HG*2
HEIGHT_HUD_LOWER=HG*2

COLOR_WALL = 'blue' # maze color
WALL_THICKNESS= 1 ######## better to have the odd number!  3 is better than 2, 7 is better than 8 !!!!


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

g_screen=display.set_mode([GRID_COUNT_X*G_SIZE ,HEIGHT_HUD_UPPER+GRID_COUNT_Y*G_SIZE+HEIGHT_HUD_LOWER])
g_clock=time.Clock() # originally variable timer 

ALL_FONTS=font.get_fonts()
g_myfont=font.SysFont(ALL_FONTS[1], G_SIZE//4*3)

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

# ghost class
class Ghost:
     def __init__(self,id):
          self.id=id
          self.img=ghost_images[id]

          self.x=G_SIZE*(GRID_COUNT_X//2 + id-2)
          self.y=G_SIZE*(GRID_COUNT_Y//2)
          
          self.target_x=0
          self.target_y=0
          self.speed=2
          self.spooked=False
          self.dead=False
          self.inbox=True

          self.wish_direction=3 # up first
          self.direction=-1
          self.turns=[0]*4

     def update(self):
          global g_powerup_phase
          self.inbox=True
          self.spooked=( 0< g_powerup_phase)

          # logic for ghost wish
          self.target_x=g_player_x
          self.target_y=g_player_y

          # use DIRECTION for BSF  # objective : determine self.wish_direction

          x,y=self.x//G_SIZE,self.y//G_SIZE
          
          tx,ty=self.target_x//G_SIZE,self.target_y//G_SIZE
          k=(x,y,tx,ty)
          if k in BFS_SOLUTION:
               self.wish_direction = BFS_SOLUTION[k]
          else:
               Q=[(x,y,[])] 
               SEEN=set()
               for u,v,dir in Q:
                    
                    # when warp tunnel was used
                    u%=GRID_COUNT_X
                    v%=GRID_COUNT_Y 

                    if (u,v)==(tx,ty):
                         BFS_SOLUTION[k] = dir and dir[0] or 0# 0 for safety value when target is same position
                         self.wish_direction = BFS_SOLUTION[k]
                         break

                    #if x<0 or y<0:continue
                    if (u,v)in SEEN:continue
                    SEEN.add((u,v))

                    try:
                         _r,_d,_l,_u = DIRECTION.get((u,v),[1,0,1,0]) #  if data was not found, maybe warp tunnel 
                         if _r:Q.append(( u+1 , v , dir+[0]))
                         if _d:Q.append(( u,  v+1 , dir+[1]))
                         if _l:Q.append(( u-1 , v , dir+[2]))
                         if _u:Q.append(( u  ,v-1 , dir+[3]))
                    except Exception as e:
                         #print(e,(x,y))
                         pass

          # update if on the grid
          if self.x%G_SIZE==self.y%G_SIZE==0:
               index_r,index_c=int(self.y//G_SIZE),int(self.x//G_SIZE)

               self.turns = DIRECTION.get( (index_c,index_r), [1,0,1,0] ) # exception : warping tunnel

               if self.turns[self.wish_direction]:
                    self.direction = self.wish_direction # change direction if player wish is available 

          #print(self.id, self.turns)
          # move ghost
          #if self.turns[self.direction]:self.direction=self.wish_direction
          if self.turns[self.direction]:          # move if pacman can move otherwise, stay
               dx={0:1,2:-1}.get(self.direction,0)
               dy={1:1,3:-1}.get(self.direction,0)
               self.x+=dx*self.speed
               self.y+=dy*self.speed
               
          
          # if warp tunnel
          if self.x<-G_SIZE:          self.x=G_SIZE*(GRID_COUNT_X)
          elif G_SIZE*(GRID_COUNT_X) < self.x: self.x=-G_SIZE

     def draw(self):
          image=self.img
          if self.spooked:    
               image=spooked_img
          if self.dead:       
               image=dead_img

          g_screen.blit(image, (self.x, self.y + HEIGHT_HUD_UPPER, G_SIZE, G_SIZE))

def pacman_eats_dot():
     global g_player_x,g_player_y,g_score, g_powerup_phase
     try:
          Cell_Current=g_level[int(g_player_y)//G_SIZE][int(g_player_x)//G_SIZE]
          if Cell_Current=='·':
               g_level[int(g_player_y)//G_SIZE][int(g_player_x)//G_SIZE]=' '
               g_score+=10
          if Cell_Current=='■':
               g_level[int(g_player_y)//G_SIZE][int(g_player_x)//G_SIZE]=' '
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
          g_screen.blit(transform.scale(player_images[0],(HG*2,HG*2)),(G_SIZE*(1+i),G_SIZE*(GRID_COUNT_Y+.8)))

     value=g_clock.get_fps()
     _fps_t = g_myfont.render(f'FPS: {value:.3f}' , 1, "red" if  value < FPS*.9 else 'green' )
     g_screen.blit(_fps_t,(G_SIZE*(GRID_COUNT_X-5),HG))

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

     if PACMAN_CAN_GO[g_player_wish_dir]==1:# because 2 is only for ghost to pass
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
     
     movable=['RDLU'[i] for i in range(4) if PACMAN_CAN_GO[i]]
     _mystr=f'{index_r:02d},{index_c:02d},player_x:{px},{movable}'
     _mytext=g_myfont.render(_mystr, 1, (255,255,0))             
     _myrect=Rect(G_SIZE*10,G_SIZE*0.5,G_SIZE*10  ,G_SIZE*10)
     g_screen.blit(_mytext,_myrect)

     _mystr2=f'x%G_SIZE:{px%G_SIZE:02d},y%G_SIZE:{py%G_SIZE:02d}, powerup phase : {g_powerup_phase}'
     _mytext2=g_myfont.render(_mystr2, 1, (255,255,0))             
     _myrect2=Rect(G_SIZE*10,G_SIZE*(GRID_COUNT_Y+1),G_SIZE*10  ,G_SIZE*10)
     g_screen.blit(_mytext2,_myrect2)

     draw.circle(g_screen, color='purple', center=(index_c*G_SIZE,index_r*G_SIZE + HEIGHT_HUD_UPPER), radius=5 ,width=0) # player's grid position
     draw.rect(g_screen, color='purple', rect=(index_c*G_SIZE, index_r*G_SIZE + HEIGHT_HUD_UPPER,G_SIZE,G_SIZE), width=1 ) # 

     
     # direction data check
     g_my_small_font=font.SysFont(ALL_FONTS[1], 7)
     for (x,y) in DIRECTION:
          data=DIRECTION[(x,y)]
          if data==[]:data=[0,0,0,0]

          #_mystr=''.join('>v<^'[i] for i in (0,1,2,3) if data[i] ) 
          _mystr=''.join('>v<^'[i] for i in (2,3,1,0) if data[i] )  #'<^v>' was better for debug display
          
          _mytext=g_my_small_font.render(_mystr, 1, (255,255,0))            
          _myrect= Rect(x*G_SIZE, y*G_SIZE + HEIGHT_HUD_UPPER,G_SIZE,G_SIZE)
          g_screen.blit(_mytext,_myrect)

ghosts=[Ghost(i) for i in range(4)] # instantiated 4 ghosts

start_ticks=time.get_ticks()# game initial time to register
g_mainloop=True
while g_mainloop:# main loop continues until quit button

     # game time
     g_clock.tick(FPS)
     g_millisec=time.get_ticks()-start_ticks # how much milliseconds passed since start
     
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
     for ghost in ghosts:ghost.draw()
     draw_HUD()

     if debugmode:debugdraw()# DEBUG DRAW
     
     display.flip()

quit()