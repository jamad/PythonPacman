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

init() # pygame init

# shortcut for debugging F2 to rename variables , F12 to check all usage
debugmode=0

# constants
FPS = 120 # 60 , 240

PLAYER_SPEED = 2

IMG_W = 45 #pixel size for characters
IMG_H = 45
GRID_H = 28
GRID_W = 30
INFO_HEIGHT=50 # space to display score, lives etc

GAP_H = IMG_H-GRID_H # buffer so that player don't hit the cell while there is a space between the edge and the actual wall  (originally num3)
GAP_W = IMG_W-GRID_W


COLOR_WALL = 'blue' # maze color

SCREEN_W=GRID_W*count_C
SCREEN_H=GRID_H*(count_R-1)+INFO_HEIGHT

gate_position=(440  ,0 )

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



#pos_ghost_targets = [ for _ in range(4)] # ghost has each pacman player position!
ghost_speeds = [2]*4

lives = 2

game_over = 0

def handle_game_over():
    global game_over, startup_counter
    
    game_over = 1
    startup_counter=0

class Ghost:
    def __init__(self,  target, speed, img,  id):

        self.id = id # fixed
        self.x_pos = 0 # to draw image
        self.y_pos = 0 # to draw image

        self.ghost_target = target
        self.speed = speed
        self.img = img
        self.dir = 0
        self.dead = 0 # when it gets true???

        self.in_box=1 # start in box
        
        self.center_x =  23 # offset
        self.center_y = 23 # offset
        self.Cell_R=self.Cell_L=self.Cell_U=self.Cell_D=' '
        self.can_move = [0]*4 #RLUD
        

    def update(self):
        
        self.center_x = self.x_pos + 23
        self.center_y = self.y_pos + 23
        self.in_box = (350 < self.x_pos < 550 and 370 < self.y_pos < 480)
        self.can_move  = self.check_collisions()
        self.rect = rect.Rect((self.center_x - 18, self.center_y - 18), (36, 36))

        if debugmode:
            draw.circle(screen, 'green', (self.center_x-1, self.center_y-1), 20, 1) 
            draw.rect(screen, color='red', rect=self.rect, width=1 )


    def draw(self):
        if powerup_phase and not GHOST_spooked[self.id]:# using self.id
            screen.blit(spooked_img, (self.x_pos, self.y_pos))

        elif self.dead:                                 
            screen.blit(dead_img, (self.x_pos, self.y_pos))
        else:
            screen.blit(self.img, (self.x_pos, self.y_pos))
            screen.blit(dead_img, (self.x_pos, self.y_pos)) # move eye position TODO

        if debugmode:
            _mytext=myfont.render(f'{self.dir}', 1, (255,255,0))      
            _myrect=Rect(self.x_pos +10 , self.y_pos +10, 20,20)
            screen.blit(_mytext,_myrect)
        
    def check_collisions(self):
        
        if 0 < self.center_x // 30 < 29:
            row=int( self.center_y // GRID_H )              # don't know why but data was float without int()
            col=int( self.center_x // GRID_W )              # don't know why but data was float without int()
            row_U=int( (self.center_y - GAP_H) // GRID_H )  # don't know why but data was float without int()
            row_D=int( (self.center_y + GAP_H) // GRID_H )  # don't know why but data was float without int()
            col_L=int( (self.center_x - GAP_W) // GRID_W )  # don't know why but data was float without int()
            col_R=int( (self.center_x + GAP_W) // GRID_W )  # don't know why but data was float without int()

            self.Cell_U = cell_U = level[row_U][col]    # up   RADIUS aka num3, GRID_H aka num1, GRID_W aka num2
            self.Cell_D = cell_D = level[row_D][col]    # down
            self.Cell_R = cell_R = level[row][col_R]    # right
            self.Cell_L = cell_L = level[row][col_L]    # left
            
            self.Cell_R = cellF = level[row][col +1]# right side
            self.Cell_L = cellE = level[row][col -1]# left side
            
            if debugmode: # draw rect
                if self.can_move[0] or 1:draw.rect(screen,color=(255,0,0),rect=(col_R*GRID_W , row*GRID_H, GRID_W,GRID_H), width=1) # show right cell 
                if self.can_move[1] or 1:draw.rect(screen,color=(255,0,0),rect=(col_L*GRID_W , row*GRID_H, GRID_W,GRID_H), width=1) # show left cell 
                if self.can_move[2] or 1:draw.rect(screen,color=(255,0,0),rect=(col*GRID_W , row_U*GRID_H, GRID_W,GRID_H), width=1) # show upper cell 
                if self.can_move[3] or 1:draw.rect(screen,color=(255,0,0),rect=(col*GRID_W , row_D*GRID_H, GRID_W,GRID_H), width=1) # show down cell 

            not_alive= (self.in_box or self.dead)

            cellcheck=lambda x:x in ' ·■' or (x=='═' and not_alive)

            is_dirH=self.dir in (0,1)
            is_dirV=self.dir in (2,3)
            in_sweetspot_V= (12 <= self.center_y % GRID_H <= 18)
            in_sweetspot_H= (12 <= self.center_x % GRID_W <= 18)

            self.can_move[0] = cellcheck(cell_R) or (is_dirV and in_sweetspot_V and cellcheck(cellF)) #or (is_dirH and in_sweetspot_V and cellcheck(cellC))
            self.can_move[1] = cellcheck(cell_L) or (is_dirV and in_sweetspot_V and cellcheck(cellE)) #or (is_dirH and in_sweetspot_V and cellcheck(cellB))
            self.can_move[2] = cellcheck(cell_U) or (cell_U == '═' )
            self.can_move[3] = cellcheck(cell_D) or (cell_D == '═' and self.dead) # only 

            if self.dead and cell_D=='═':
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
        #CONDS=[cond0,cond1,cond2,cond3]

        # default behavior
        #if index==0:  # GHOST[0] : clyde doesn't change direction unless hit . if multiple candidates to turn, follow pacman
        if any( (self.dir== i and not self.can_move[i]) for i in (0,1)): # blocked horizontal
            if cond2:self.dir=2 # if can follow pacman above, go up
            elif cond3:self.dir=3
            else: self.dir=(1 - self.dir) # backward direction 
        elif any( (self.dir== i and not self.can_move[i]) for i in (2,3) ): # blocked vertical
            if cond0:self.dir=0
            elif cond1:self.dir=1
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

        # move by direction 
        if self.dir==0: self.x_pos += self.speed
        if self.dir==1: self.x_pos -= self.speed
        if self.dir==2: self.y_pos -= self.speed
        if self.dir==3: self.y_pos += self.speed

        # warp gate
        if self.x_pos < -50:    self.x_pos = SCREEN_W-3
        elif self.x_pos > SCREEN_W:  self.x_pos = -50+3

        return self.x_pos, self.y_pos, self.dir

player_start_posX=(GRID_W*count_C//2) #450 #- GAP_H*2 # centerize
player_start_posY=663

GHOST=[Ghost((player_start_posX,player_start_posY) , ghost_speeds[i], ghost_images[i], i) for i in range(4)] 


# initial declaration
def reset_game():
    global count_dot
    global level,startup_counter, power_counter, powerup_phase # can be first variable 
    global player_x, player_y,player_dir, player_dir_wish, player_can_move
    global GHOST_posX, GHOST_posY, GHOST_dir,GHOST_spooked, GHOST_dead # important!
    
    startup_counter = 0 
    powerup_phase = 0
    power_counter = 0       
    
    player_x = player_start_posX
    player_y = player_start_posY
    
    player_dir =0 # right 
    player_dir_wish = 0 #player_dir : RLUD   ::::   0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
    player_can_move = [0]*4                    # R, L, U, D  open flag for movement

    # ghosts : blinky 0  inky 1  pinky 2 clyde 3   
    for i,ghost in enumerate(GHOST):
        ghost.x_pos=[GRID_W*14, GRID_W*16, GRID_W*14, GRID_W*12][i]
        ghost.y_pos=[GRID_H*13.8, GRID_H*15.5, GRID_H*15.5, GRID_H*15.5] [i]
        ghost.dir=0
        ghost.spooked=0
        ghost.dead=0
    
    count_dot=boards_data.count('·')+boards_data.count('■') # 
    level = copy.deepcopy(boards)

reset_game()

def draw_HUD():
    score_text = myfont.render(f'Score: {score}', True, 'white')
    screen.blit(score_text, (10, 920))
    
    if powerup_phase and debugmode:
        draw.circle(screen, 'blue', (140, 930), 15) # debug

    for i in range(lives):
        screen.blit(transform.scale(player_images[0], (30, 30)), (650 + i * 40, 915))
    
    if game_over or (count_dot==0):
        draw.rect(screen, 'white', [50, 200, 800, 300],0, 10)
        draw.rect(screen, 'dark gray', [70, 220, 760, 260], 0, 10)
        message= game_over and 'Game over! Space bar to restart!' or 'Victory! Space bar to restart!'
        color=game_over and 'red' or 'green'
        gameover_text = myfont.render( message, True, color)
        screen.blit(gameover_text, (100, 300))

def check_eaten_dots():
    global count_dot
    global center_x, center_y , score, powerup_phase, power_counter, GHOST_spooked

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
        GHOST_spooked = [0]*4

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
            
            if debugmode:
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
    global player_can_move
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

    player_can_move = [tR,tL,tU,tD]

def mainloop_event():
    global player_dir_wish, player_dir, game_over, lives, count_dot
    #print(player_dir_wish, player_dir)
    for e in event.get():

        if e.type==QUIT: return False # exit main loop

        elif e.type == KEYDOWN: 
            
            player_dir_wish={K_RIGHT:0,K_LEFT:1,K_UP:2,K_DOWN:3}.get(e.key,-1) # key defines player_dir , if K_SPACE:-1,

        # player_dir : RLUD
        elif e.type == KEYUP:
            if e.key == K_SPACE and (game_over or (count_dot==0)):
                lives -= 1
                reset_game()

                score = 0
                lives = 2
                game_over  = False

            # need to learn why the following was better than simply player_dir_wish= player_dir
            if {K_RIGHT:0,K_LEFT:1,K_UP:2,K_DOWN:3}.get(e.key,-1)==player_dir_wish:
                player_dir_wish= player_dir

    for i in range(4):
        if player_dir_wish == i and player_can_move[i]: 
            player_dir = i

    return True

def display_FPS(): # fps display  ### https://stackoverflow.com/questions/67946230/show-fps-in-pygame
    _fps_t = myfont.render(f'FPS: {timer.get_fps():.3f}' , 1, "green")
    screen.blit(_fps_t,(0,0))

def update_ghost_target():
    global pos_ghost_targets , GHOST_posX, GHOST_posY
    
    GHOST_GOALS=[(380, 400)]*4 # ghost home box  as default

    # update ghost's target (pacman, home or  runaway corner)
    for ghost in GHOST:
        i=ghost.id
        
        in_ghost_home= (350 < ghost.x_pos < 350  + 200  )and (385 - GAP_H*3 < ghost.y_pos < 385 + 100)

        if not GHOST[i].dead:
            if powerup_phase:
                if GHOST_spooked[i]:  # dead ghost
                    GHOST_GOALS[i] = ((player_x, player_y), (450, 200)) [in_ghost_home]
                else: # spooked ghost
                    if i==3:GHOST_GOALS[i] = (450, 450)
                    else:   GHOST_GOALS[i] = ((0,SCREEN_W)[player_x < 450], (0,SCREEN_H)[player_y < 450])# away from pacman 
            else:
                GHOST_GOALS[i] = (400, 100) if in_ghost_home else (player_x + 22, player_y + 22)
        
        if in_ghost_home:
            GHOST_GOALS[i] = (440, 388-100)

    if debugmode:# draw home collision
        draw.rect(screen, color='green', rect=Rect(GRID_W*12 , GRID_H*14  ,GRID_W*6, GRID_H*3),width=1) # box collision
        draw.circle(screen, color='red', center=(380, 400), radius=5 ,width=0) # ghost home
        draw.circle(screen, color='red', center=(450,100), radius=5 ,width=0) # gate target
        for i,goal in enumerate(GHOST_GOALS):
            draw.circle(screen, color=('red','pink','cyan','orange')[i], center=goal, radius=i*2 ,width=1)
            
    pos_ghost_targets = GHOST_GOALS

def check_gameover(): # player hit ghost 
    global lives
    
    if 0 < lives:
        lives -= 1
        reset_game()
    else:
        handle_game_over()

def move_characters():
    global startup_counter, player_x, player_y

    startup_counter += 1

    if startup_counter < 3*60*(60/FPS): return # before 3 seconds
    
    if game_over or count_dot==0:       return # gameover or game_clear
        
    if player_can_move[player_dir]:
        if   player_dir == 0 :  player_x += PLAYER_SPEED
        elif player_dir == 1 :  player_x -= PLAYER_SPEED
        elif player_dir == 2 :  player_y -= PLAYER_SPEED
        elif player_dir == 3 :  player_y += PLAYER_SPEED
        
        # player warp gate
        if player_x > screen.get_width():player_x = -50+3 
        if player_x < -50:player_x = screen.get_width()-3
        
    for ghost in GHOST:
        i=ghost.id
        if ghost.in_box or ghost.dead:
        #if GHOST[i].in_box or GHOST_dead[i]:   
            ghost.x_pos,ghost.y_pos,ghost.dir=GHOST[i].move_G(3) # type3 ghost behavior ?? just 
        else:                                   
            ghost.x_pos,ghost.y_pos,ghost.dir= GHOST[i].move_G(i)

def handling_when_pacman_hit_ghost():
    global score
    if powerup_phase: # pacman eats ghosts

        for ghost in GHOST:
            i=ghost.id
            if player_collision.colliderect(ghost.rect) and not ghost.dead:
                if ghost.spooked: check_gameover() # ghost eat pacman , so game reset
                else: # pacman eat ghost
                    ghost.dead=1
                    ghost.spooked=1

                    #score += (2 ** GHOST_spooked.count(True)) * 100 

    else: # ghost eats pacman
        if any ( player_collision.colliderect(GHOST[i].rect) and  not GHOST[i].dead for i in range(4)):
            check_gameover()

def respawn_ghosts():
    # revive the ghosts if in the home box
    for ghost in GHOST:
        i=ghost.id
        if ghost.in_box and ghost.dead:
        #if GHOST[i].in_box and GHOST_dead[i]:
            GHOST_dead[i] = False

def handling_when_pacman_eat_power():
    global counter, powerup_phase, powerup_blink_on, power_counter, GHOST_spooked, ghost_speeds
    
    powerup_blink_on = (7 < counter)

    if powerup_phase:
        power_counter = (power_counter+1) % 600
        if power_counter==0:
            powerup_phase = 0   # powerup ended

            GHOST_spooked = [0]*4 # ghost is not spooked anymore    

    ghost_speeds = [ (2,1)[powerup_phase] ]*4

    for ghost in GHOST:
        i=ghost.id
        if ghost.spooked: ghost.speed=2
        #if GHOST_spooked[i]:  ghost_speeds[i] = 2 # slower when spooked
        if ghost.dead: ghost.speed =4 # faster when dead

    

while mainloop_event():

    timer.tick(FPS)# clock
    counter =  (counter + 1)%20 # conter increment 

    center_x = player_x + IMG_W//2 -1 # don't know why but without -1, pacman got stuck
    center_y = player_y + IMG_H//2 -1 # don't know why but without -1, pacman got stuck
    player_collision = draw.circle(screen, ((0,0,0,0),'green')[debugmode] , (center_x, center_y), 20, (1,1)[debugmode]) # debug
    check_passable(center_x, center_y)

    # ghost update # need to separate init
    # ghost init update here @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    for ghost in GHOST:
        ghost.update()
    
    update_ghost_target() # Ghost target update
    move_characters()
    check_eaten_dots()
    handling_when_pacman_eat_power()
    handling_when_pacman_hit_ghost()
    respawn_ghosts()

    #######  draw visuals
    screen.fill('black')
    
    draw_board()
    draw_characters()
    draw_HUD()

    if debugmode:display_FPS()
    display.flip()

quit()