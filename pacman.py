# Build Pac-Man from Scratch in Python with PyGame!!
# done until 1:26:45  , maybe around 3:40 to start then come back with shorter code 

from pygame import init, display, time, font, transform, image, rect, event, draw , Rect, QUIT, KEYDOWN, KEYUP, K_RIGHT, K_LEFT, K_UP, K_DOWN, K_SPACE
import copy
from math import pi

# 0:empty, 1:dot, 2:big dot,3:lineV,4:lineH,5:up right,6:up left,7:low left,8:low right,9:gate
# 0: ' ', 1: '·', 2:'■',3:'│',4:'─',5:'┐',6:'┌',7:'└',8:'┘',9:'═', 
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
count_R,count_C=len(boards),len(boards[0]) # 33 row, 30 columns

init() # pygame init . # time.get_ticks() start from here

# shortcut for debugging F2 to rename variables , F12 to check all usage
debugmode=1
debugmode_board=0

# constants
FPS = 60 # 120, 60 , 240

PLAYER_SPEED = 2

IMG_W = 45 #pixel size for characters
IMG_H = 45

GRID_H = 28
GRID_W = 30

INFO_HEIGHT=50 # space to display score, lives etc

GAP_H = GRID_H//2 #IMG_H - GRID_H  # buffer so that player don't hit the cell while there is a space between the edge and the actual wall  (originally num3)
GAP_W = GRID_W//2 #IMG_W - GRID_W
print(GAP_H,GAP_W)

DIRECTION_DICT={K_RIGHT:0,K_LEFT:1,K_UP:2,K_DOWN:3}

COLOR_WALL = 'blue' # maze color

SCREEN_W=GRID_W*count_C
SCREEN_H=GRID_H*(count_R-1)+INFO_HEIGHT

player_start_posX=(GRID_W*count_C//2) #450 #- GAP_H*2 # centerize
player_start_posY=663

gate_position=(440  ,0 )
GHOST_HOME=(380, 400)

screen = display.set_mode([SCREEN_W, SCREEN_H])
timer = time.Clock()
myfont = font.Font('freesansbold.ttf', 20)
mydebugfont = font.Font('freesansbold.ttf', 9)

# image assets
load_image=lambda type,p:transform.scale(image.load(f'assets/{type}_images/{p}.png'),(IMG_W, IMG_H))
player_images = [load_image('player',i) for i in (1,2,3,2)]# 4 images
ghost_images  = [load_image('ghost',x) for x in 'red pink blue orange'.split()]
spooked_img   = load_image('ghost','powerup') 
dead_img      = load_image('ghost','dead') 

counter = powerup_blink_on = score = powerup_phase = power_counter = 0

lives = 2
game_over = 0

def handle_game_over():
    global game_over
    
    game_over = 1
    
    init() # timer initialized ????
    #time.set_timer(0,0)

class Ghost:
    def __init__(self,   id):

        self.id = id # fixed
        self.img = ghost_images[id]

        self.x_pos = 0 # to draw image
        self.y_pos = 0 # to draw image

        self.ghost_target = (player_start_posX,player_start_posY)
        self.speed = 2
        self.dir = 0
        self.dead = 0 # when it gets true???
        self.eaten_by_pacman=0

        self.in_box=1 # start in box
        
        self.center_x =  23 # offset
        self.center_y = 23 # offset
        #self.Cell_R=self.Cell_L=self.Cell_U=self.Cell_D=' '
        self.can_move = [0]*4 #RLUD

        self.rect = rect.Rect((self.x_pos + 23 - 18, self.y_pos + 23 - 18), (36, 36))
        
    def update(self):
        self.center_x = self.x_pos + 23
        self.center_y = self.y_pos + 23
        self.in_box = (350 < self.x_pos < 550 and 370 < self.y_pos < 480)

        self.can_move  = self.check_collisions()

        self.rect = rect.Rect((self.center_x - 18, self.center_y - 18), (36, 36))




        self.ghost_target=(380, 400)# ghost home box  as default
        
        self.in_box= (350 < self.x_pos < 350  + 200  )and (385 - GAP_H*3 < self.y_pos < 385 + 100)

        if not self.dead:
            if powerup_phase:
                if self.eaten_by_pacman: # home returning ghost
                    if self.in_box:
                        self.ghost_target=(player_x, player_y)
                    else:
                        self.ghost_target=(450, 200)
                else: # running away ghost
                    if self.id==3:
                        self.ghost_target = (450, 450)
                    else:   self.ghost_target = ((0,SCREEN_W)[player_x < 450], (0,SCREEN_H)[player_y < 450])# away from pacman 
            else:
                self.ghost_target = (400, 100) if self.in_box else (player_x + 22, player_y + 22)
        else:# ghost is dead
            self.ghost_target=GHOST_HOME

        
        if self.in_box:
            self.ghost_target = (440, 388-100)

            if  self.dead: self.dead=0 # respawn_ghosts

            
        self.x_pos,self.y_pos,self.dir=self.move_G(3 if self.in_box or self.dead else self.id ) # type3 ghost behavior ?? just 
        
        self.speed=2
        if powerup_phase:self.speed=1# slow if powerup phase
        if self.dead: self.speed =4 # faster when dead

        if debugmode:# draw home collision
 
            _myrect=Rect(GRID_W*12 , GRID_H*14  ,GRID_W*6, GRID_H*3)
            draw.rect(screen, color='green', rect=_myrect,width=1) # home box    
            _mytext=font.Font('freesansbold.ttf', 12).render(f'home box', 1, (255,255,0))             
            screen.blit(_mytext,Rect(GRID_W*12 , GRID_H*14  ,GRID_W*12, GRID_H*6))


            draw.circle(screen, color='red', center=(380, 400), radius=5 ,width=0) # ghost home
            draw.circle(screen, color='red', center=(450,100), radius=5 ,width=0) # gate target

            draw.circle(screen, color=('red','pink','cyan','orange')[self.id], center=self.ghost_target, radius=(self.id)*5 ,width=1) #target
            
            draw.circle(screen, 'green', (self.center_x-1, self.center_y-1), 20, 1)  # rect

            draw.rect(screen, color='purple', rect=self.rect, width=1 ) # ghost rect

    def draw(self):
        
        if powerup_phase and not self.eaten_by_pacman:# using self.id
            screen.blit(spooked_img, (self.x_pos, self.y_pos))

        elif self.dead:                                 
            screen.blit(dead_img, (self.x_pos, self.y_pos))
        else:
            screen.blit(self.img, (self.x_pos, self.y_pos))
            screen.blit(dead_img, (self.x_pos, self.y_pos)) # move eye position TODO

        if debugmode:
            _mytext=myfont.render(f'{self.dir}', 1, (255,255,0))      
            _myrect=Rect(self.x_pos +10 , self.y_pos +20, 20,20)
            screen.blit(_mytext,_myrect)
        
    def check_collisions(self):
        
        if 0 < self.center_x // 30 < 29:
            row=int( self.center_y // GRID_H )              # data was float without int() !!!!!!
            col=int( self.center_x // GRID_W )              
            row_U=int( (self.center_y - GAP_H) // GRID_H )  
            row_D=int( (self.center_y + GAP_H) // GRID_H )  
            col_L=int( (self.center_x - GAP_W) // GRID_W )  
            col_R=int( (self.center_x + GAP_W) // GRID_W )  

            self.Cell_U = level[row_U][col]    # up   RADIUS aka num3, GRID_H aka num1, GRID_W aka num2
            self.Cell_D = level[row_D][col]    # down
            self.Cell_R = level[row][col_R]    # right
            self.Cell_L = level[row][col_L]    # left
            
            self.cellF = level[row][col +1] # right side
            self.cellE = level[row][col -1] # left side
            
            if debugmode: # draw rect
                COLOR_TOGGLE=('purple','green')
                draw.rect(screen,color=COLOR_TOGGLE[self.can_move[0]],rect=(col_R*GRID_W , row*GRID_H, GRID_W,GRID_H), width=1) # show right cell 
                draw.rect(screen,color=COLOR_TOGGLE[self.can_move[1]],rect=(col_L*GRID_W , row*GRID_H, GRID_W,GRID_H), width=1) # show left cell 
                draw.rect(screen,color=COLOR_TOGGLE[self.can_move[2]],rect=(col*GRID_W , row_U*GRID_H, GRID_W,GRID_H), width=1) # show upper cell 
                draw.rect(screen,color=COLOR_TOGGLE[self.can_move[3]],rect=(col*GRID_W , row_D*GRID_H, GRID_W,GRID_H), width=1) # show down cell 

            not_alive= (self.in_box or self.dead)

            cellcheck=lambda x:x in ' ·■' or (x=='═' and not_alive)

            is_dirH=self.dir in (0,1)
            is_dirV=self.dir in (2,3)
            in_sweetspot_V= (12 <= self.center_y % GRID_H <= 18)
            in_sweetspot_H= (12 <= self.center_x % GRID_W <= 18)

            self.can_move[0] = cellcheck(self.Cell_R) or (is_dirV and in_sweetspot_V and cellcheck(self.cellF)) or (is_dirH and in_sweetspot_V and cellcheck(self.Cell_R))
            self.can_move[1] = cellcheck(self.Cell_L) or (is_dirV and in_sweetspot_V and cellcheck(self.cellE)) or (is_dirH and in_sweetspot_V and cellcheck(self.Cell_L))
            self.can_move[2] = cellcheck(self.Cell_U) or (self.Cell_U == '═' )
            self.can_move[3] = cellcheck(self.Cell_D) or (self.Cell_D == '═' and self.dead) # only 

            if self.dead and self.Cell_D=='═':
                self.dir=3 # if ghost is dead and down is 9 (home entry) > move down to enter ghost home ##### BUGFIX
        
        else: self.can_move[0] = self.can_move[1] = 1

        return self.can_move

    def move_G(self, index):  
        
        ghost_target_x,ghost_target_y = gate_position if self.in_box else self.ghost_target # packman or home gate

        # direction : RLUD 
        # direction change if blocked by the wall

        # default movement regardless index

        cond0=self.x_pos < ghost_target_x and self.can_move[0] # goal is right and can move right
        cond1=ghost_target_x < self.x_pos and self.can_move[1] # goal is left and can move left

        #  NB!!!!!!!!!!!!    for pygame, smaller number means upper!!!! becaue topleft is (0,0)!
        cond2=ghost_target_y < self.y_pos and self.can_move[2] # goal is up and can move up
        cond3=ghost_target_y > self.y_pos and self.can_move[3] # goal is down and can move down

        # default behavior
        #if index==0:  # GHOST[0] : clyde doesn't change direction unless hit . if multiple candidates to turn, follow pacman
        if any( (self.dir== i and not self.can_move[i]) for i in (0,1)): # blocked horizontal
            if cond2:self.dir=2 # if can follow pacman above, go up
            elif cond3:self.dir=3
            elif self.can_move[2]:self.dir=2
            elif self.can_move[3]:self.dir=3
            else: self.dir=(1 - self.dir) # backward direction 
        elif any( (self.dir== i and not self.can_move[i]) for i in (2,3) ): # blocked vertical
            if cond0:self.dir=0
            elif cond1:self.dir=1
            elif self.can_move[0]:self.dir=0
            elif self.can_move[1]:self.dir=1
            else:self.dir= (5 - self.dir)  # backward  if 3 then 2. if 2 then 3
        
        ### now all same behavior because disabled the following
        # original was move_clyde(self) for index==3
        '''
        if index==2 or index==3:# GHOST[2] GHOST[3] is going to turn left or right whenever advantageous
            if cond1 and self.can_move[1]:   self.dir = 1
            if cond0 and self.can_move[0]:   self.dir = 0
                    
        if index==1 or index==3:# GHOST[1] GHOST[3] turns up or down at any point to pursue
            if cond3 and self.can_move[3]:    self.dir = 3
            if cond2 and self.can_move[2]:    self.dir = 2
        '''

        # home gate handling
        if self.Cell_D=='═' and self.dead and self.can_move[3]:    self.dir=3
        if self.Cell_U=='═' and self.in_box  and self.can_move[2] :self.dir=2

        if index==3 or 1:
            dist_to_pacman_x=abs(player_x - self.center_x)
            dist_to_pacman_y=abs(player_y - self.center_y)
            
            if dist_to_pacman_x < dist_to_pacman_y:
                # priority is vertical
                
                if cond2:self.dir=2
                elif cond3:self.dir=3
            else:
                if cond1:self.dir=1
                elif cond0:self.dir=0


                if   cond0 and self.can_move[0]:self.dir=0
                elif cond3 and self.can_move[3]:self.dir=3
                elif cond1 and self.can_move[1]:self.dir=1
                elif cond2 and self.can_move[2]:self.dir=2
                elif self.can_move[0]:self.dir=0
                elif self.can_move[3]:self.dir=3
                elif self.can_move[1]:self.dir=1
                elif self.can_move[2]:self.dir=2

        # move by direction 
        if self.dir==0: self.x_pos += self.speed
        if self.dir==1: self.x_pos -= self.speed
        if self.dir==2: self.y_pos -= self.speed
        if self.dir==3: self.y_pos += self.speed

        # warp gate
        if self.x_pos < -50:    self.x_pos = SCREEN_W-3
        elif self.x_pos > SCREEN_W:  self.x_pos = -50+3

        return self.x_pos, self.y_pos, self.dir


GHOST=[Ghost(i) for i in range(4)] 

# initial declaration
def reset_game():
    global count_dot
    global level, power_counter, powerup_phase # can be first variable 
    global player_x, player_y,player_dir, player_dir_wish, player_can_move
    
    powerup_phase = 0
    power_counter = 0       
    
    player_x = player_start_posX
    player_y = player_start_posY
    
    player_dir =0 # right 
    player_dir_wish = 0 #player_dir : RLUD   ::::   0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
    player_can_move = [0]*4                    # R, L, U, D  open flag for movement

    # ghosts : blinky 0  inky 1  pinky 2 clyde 3   
    for ghost in GHOST:
        ghost.x_pos=[GRID_W*14, GRID_W*16, GRID_W*14, GRID_W*12][ghost.id]
        ghost.y_pos=[GRID_H*13.8, GRID_H*15.5, GRID_H*15.5, GRID_H*15.5][ghost.id]
        ghost.dir=0
        ghost.eaten_by_pacman=0
        ghost.dead=0
    
    count_dot=boards_data.count('·')+boards_data.count('■') # 
    level = copy.deepcopy(boards)



def draw_HUD():
    score_text = myfont.render(f'Score: {score}', True, 'white')
    screen.blit(score_text, (10, 920))
    
    if powerup_phase and debugmode:
        draw.circle(screen, 'blue', (140, 930), 15) # debug

    for i in range(lives):
        screen.blit(transform.scale(player_images[0], (30, 30)), (650 + i * 40, 915))
    
    # game over message
    if game_over or (count_dot==0):
        PANEL_W=320
        PANEL_H=160
        PANEL_X=450-PANEL_W//2
        PANEL_Y=435-PANEL_H//2
        draw.rect(screen, 'white', [PANEL_X, PANEL_Y, PANEL_W, PANEL_H],0, 10)
        draw.rect(screen, 'dark gray', [PANEL_X+20, PANEL_Y+20, PANEL_W-40, PANEL_H-40], 0, 10)
        message= game_over and 'GAME OVER! Hit Space Bar' or 'VICTORY! Hit Space Bar'
        color=game_over and 'red' or 'green'
        gameover_text = myfont.render( message, True, color)
        screen.blit(gameover_text, (PANEL_X+40, 425))

def check_eaten_dots():
    global count_dot
    global center_x, center_y , score, powerup_phase, power_counter

    if player_x<0:          return
    if SCREEN_W-30<player_x:return

    idx1=int( center_y // GRID_H )
    idx2=int( center_x // GRID_W )

    cell=level[idx1][idx2]

    if cell == '·':  # normal dot
        count_dot-=1
        level[idx1][idx2] = ' '   # remove dot
        score += 10
    elif cell == '■':  # power dot
        count_dot-=1
        level[idx1][idx2] = ' '   # remove dot
        score += 50
        powerup_phase = True
        power_counter = 0

        for ghost in GHOST:
            ghost.eaten_by_pacman=0 

def draw_board():
    for i in range(count_R):
        for j in range(count_C):
            cell=level[i][j]
            # 0: ' ', 1: '·', 2:'■',3:'│',4:'─',5:'┐',6:'┌',7:'└',8:'┘',9:'═', 
            # 0 = empty , 1 = dot, 2 = power dot, 3 = v line, 4 = h line, 5, 6,7,8 = corners, 9 = home gate
            if cell == '·':draw.circle(   screen, 'white',    (GRID_W*(j+.5), GRID_H*(i+.5)), 4)
            if cell == '■':draw.circle(   screen, 'white',    (GRID_W*(j+.5), GRID_H*(i+.5)), 10 if powerup_blink_on else 8)
            if cell == '│':draw.line(     screen, COLOR_WALL, (GRID_W*(j+.5), i * GRID_H),(GRID_W*(j+.5), (i+1)*GRID_H),3)
            if cell == '─':draw.line(     screen, COLOR_WALL, (GRID_W*j,  GRID_H*(i+.5)), (GRID_W*(j+1), GRID_H*(i+.5)),3)
            if cell == '┐':draw.arc(      screen, COLOR_WALL, (GRID_W*(j-.4)- 2,GRID_H*(i+.5), GRID_W, GRID_H),0, pi / 2, 3)
            if cell == '┌':draw.arc(      screen, COLOR_WALL, (GRID_W*(j+.5),   GRID_H*(i+.5),GRID_W, GRID_H), pi / 2, pi, 3)
            if cell == '└':draw.arc(      screen, COLOR_WALL, (GRID_W*(j+.5),   GRID_H*(i-.4),  GRID_W, GRID_H), pi, 3* pi / 2, 3)            
            if cell == '┘':draw.arc(      screen, COLOR_WALL, (GRID_W*(j-.4)- 2,GRID_H*(i-.4),  GRID_W, GRID_H), 3 * pi / 2,2 * pi, 3)
            if cell == '═':draw.line(     screen, 'white',    (GRID_W*j, GRID_H*(i+.5)), (GRID_W*j + GRID_W, GRID_H*(i+.5)), 3)
            
            if debugmode_board:
                draw.rect(screen,color=(0,32,0),rect=(j*GRID_W, i*GRID_H, GRID_W,GRID_H), width=1) # grid cell draw 
                
                #_mytext=mydebugfont.render(f'{cell}',1, (0,128,0))      
                #_myrect=Rect(j*GRID_W +2 , i*GRID_H +20, 20,20)
                #screen.blit(_mytext,_myrect)

                _mytext=mydebugfont.render(f'{j},{i}',1, (0,128,0))      
                _myrect=Rect(j*GRID_W +2 , i*GRID_H +10, 20,20)
                screen.blit(_mytext,_myrect)
                
def draw_characters():
    pos=(player_x, player_y)
    img_player=player_images[counter // 5]
    if player_dir == 0:      screen.blit(img_player, pos)
    elif player_dir == 1:    screen.blit(transform.flip(img_player, True, False), pos)
    elif player_dir == 2:    screen.blit(transform.rotate(img_player, 90), pos)
    elif player_dir == 3:    screen.blit(transform.rotate(img_player, -90), pos)

    # ghost to draw
    for ghost in GHOST:
        ghost.draw()

# check collisions based on center x and center y of player +/- RADIUS number
def check_passable(col, row):  # originally check_position
    if 29 <= col // 30 : return [1,1,0,0] # only horizontal warp is passable

    index_R=int(row // GRID_H)
    index_C=int(col // GRID_W)

    cell_R=level[index_R][int(col + GAP_W) // GRID_W]
    cell_L=level[index_R][int(col - GAP_W) // GRID_W]
    cell_U=level[int(row - GAP_H) // GRID_H][index_C]
    cell_D=level[int(row + GAP_H) // GRID_H][index_C]
    dir_H= player_dir in(0,1)
    dir_V= player_dir in(2,3)

    tR = (dir_H and cell_R in ' ·■') or ( dir_V and( 12 <= row % GRID_H <= 18)and(level[index_R][index_C + 1] in ' ·■')) 
    tL = (dir_H and cell_L in ' ·■') or ( dir_V and( 12 <= row % GRID_H <= 18)and(level[index_R][index_C - 1] in ' ·■'))     
    tU = (dir_V and cell_U in ' ·■') or ( dir_H and( 12 <= col % GRID_W <= 18)and(level[index_R - 1][index_C] in ' ·■')) 
    tD = (dir_V and cell_D in ' ·■') or ( dir_H and( 12 <= col % GRID_W <= 18)and(level[index_R + 1][index_C] in ' ·■')) 

    if debugmode:
        pass
        # draw rect

    return [tR,tL,tU,tD]

def display_FPS(): # fps display  ### https://stackoverflow.com/questions/67946230/show-fps-in-pygame
    _fps_t = myfont.render(f'FPS: {timer.get_fps():.3f}' , 1, "green")
    screen.blit(_fps_t,(0,0))

def check_gameover(): # player hit ghost 
    global lives
    
    if 0 < lives:
        lives -= 1
        reset_game()
    else:
        handle_game_over()

def move_characters():
    global player_x, player_y

    if time.get_ticks()<2000: # 2000 miliseconds == 3 seconds
        #print('get_time', timer.get_time(), 'get_ticks',time.get_ticks())
        return # before 3 seconds
    
    if game_over or count_dot==0:       return # gameover or game_clear
        
    if player_can_move[player_dir]:
        if   player_dir == 0 :  player_x += PLAYER_SPEED
        elif player_dir == 1 :  player_x -= PLAYER_SPEED
        elif player_dir == 2 :  player_y -= PLAYER_SPEED
        elif player_dir == 3 :  player_y += PLAYER_SPEED
        
        # player warp gate
        if player_x > screen.get_width():player_x = -50+3 
        if player_x < -50:player_x = screen.get_width()-3
        
    for ghost in GHOST:ghost.update()

def handling_when_pacman_hit_ghost():
    global score
    if powerup_phase: # pacman eats ghosts

        for ghost in GHOST:
            i=ghost.id
            if player_collision.colliderect(ghost.rect) and not ghost.dead:
                if ghost.eaten_by_pacman: 
                    check_gameover() # ghost eat pacman , so game reset
                else: # pacman eat ghost
                    ghost.dead=1
                    ghost.eaten_by_pacman=1

                    score += (2 ** sum(ghost.eaten_by_pacman for ghost in GHOST)) * 100 

    else: # ghost eats pacman
        if any ( player_collision.colliderect(ghost.rect) and  not ghost.dead for ghost in GHOST):
            check_gameover()


def handling_when_pacman_eat_power():
    global counter, powerup_phase, powerup_blink_on, power_counter, ghost_speeds
    
    powerup_blink_on = (7 < counter)

    if powerup_phase:
        power_counter = (power_counter+1) % 600
        if power_counter==0:
            powerup_phase = 0   # powerup ended
            for ghost in GHOST:
                ghost.eaten_by_pacman=0 


def mainloop_event():
    global player_dir_wish, player_dir, game_over, lives, count_dot
    for e in event.get():

        if e.type==QUIT: return False # exit main loop

        elif e.type == KEYDOWN: 
            
            player_dir_wish=DIRECTION_DICT.get(e.key,-1) # key defines player_dir , if K_SPACE:-1,

        # player_dir : RLUD
        elif e.type == KEYUP:
            if e.key == K_SPACE and (game_over or (count_dot==0)):
                lives -= 1
                reset_game()

                score = 0
                lives = 2
                game_over  = False

            # need to learn why the following was better than simply player_dir_wish= player_dir
            if DIRECTION_DICT.get(e.key,-1)==player_dir_wish:
                player_dir_wish= player_dir

    for i in range(4):
        if player_dir_wish == i and player_can_move[i]: 
            player_dir = i

    return True


reset_game()

while mainloop_event():

    if debugmode:
        screen.fill('black')

    timer.tick(FPS)# clock
    counter =  (counter + 1)%20 # conter increment 

    center_x = player_x + IMG_W//2 -1 # don't know why but without -1, pacman got stuck
    center_y = player_y + IMG_H//2 -1 # don't know why but without -1, pacman got stuck
    player_collision = draw.circle(screen, ((0,0,0,0),'green')[debugmode] , (center_x, center_y), 20, (1,1)[debugmode]) # debug
    player_can_move = check_passable(center_x, center_y)

    move_characters()
    
    
    check_eaten_dots()
    handling_when_pacman_eat_power()
    handling_when_pacman_hit_ghost()


    #######  draw visuals
    
    draw_board()
    draw_characters()
    draw_HUD()

    if not debugmode:
        screen.fill('black')

    if debugmode:display_FPS()
    display.flip()

quit()


######### TODO  ghost behavior should be fixed in check_collisions(self):
######### TODO arrange packman class to see if the logic can simpler or not
######### TODO arrange gamemanager class to see if the logic can simpler or not