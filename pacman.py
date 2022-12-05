# Build Pac-Man from Scratch in Python with PyGame!!
# done until 1:26:45  , maybe around 3:40 to start then come back with shorter code 

from pygame import init, display, time, font, transform, image, rect, event, QUIT, KEYDOWN, KEYUP, K_RIGHT, K_LEFT, K_UP, K_DOWN, K_SPACE, draw , Rect
import copy
from math import pi

# 0 = empty, 1 = dot, 2 = big dot, 3 = lineV, 4 = lineH, 5 = top right, 6 = top left, 7 = bot left, 8 = bot right,  9 = gate
boards_data='''\
644444444444444444444444444445
364444444444445644444444444453
331111111111113311111111111133
331644516444513316444516445133
332300313000313313000313003233
331744817444817817444817448133
331111111111111111111111111133
331644516516444444516516445133
331744813317445644813317448133
331111113311113311113311111133
374444513744503306448316444483
744445313644807807445313644448
000003313300000000003313300000
444448313306449944503313744444
444444817803000000307817444444
000000010003000000300010000000
444444516503000000306516444444
444445313307444444803313644444
000003313300000000003313300000
644448313306444444503313744445
364444817807445644807817444453
331111111111113311111111111133
331644516444513316444516445133
331745317444817817444813648133
332113311111111111111113311233
374513316516444444516513316483
364817813317445644813317817453
331111113311113311113311111133
331644448744513316448744445133
331744444444817817444444448133
331111111111111111111111111133
374444444444444444444444444483
744444444444444444444444444448'''

boards=[list(map(int,s)) for s in boards_data.split()]

# variable difinition F12
debugmode=1

init()

# constants
FPS = 120 # 60 , 240
WIDTH = 900
HEIGHT = 950

RADIUS = 15 # buffer so that player don't hit the cell while there is a space between the edge and the actual wall  (originally num3)

COUNT_R = (HEIGHT - 50) // 32   # grid row count    ( originally  num1)
COUNT_C = (WIDTH // 30)         # grid column count

screen = display.set_mode([WIDTH, HEIGHT])
timer = time.Clock()
myfont = font.Font('freesansbold.ttf', 20)

m_color = 'blue'

# image assets
img_size=(45, 45)
player_images = [transform.scale(image.load(f'assets/player_images/{i}.png'),img_size) for i in (1,2,3,2)]# 4 images
G_IMG=          [transform.scale(image.load(f'assets/ghost_images/{x}.png'),img_size) for x in 'red pink blue orange'.split()]
spooked_img =   transform.scale(image.load(f'assets/ghost_images/powerup.png'),img_size)
dead_img =      transform.scale(image.load(f'assets/ghost_images/dead.png'),img_size)

# initial declaration
def reset_game():
    global level
    global startup_counter, power_counter, powerup_phase # can be first variable 
    global player_x, player_y,player_dir, player_dir_command, GX, GY, GD,G_EATEN, G_DEAD # important!
    
    startup_counter = 0 
    powerup_phase = 0
    power_counter = 0       
    
    player_x = 450 - RADIUS*2 # centerize
    player_y = 663
    player_dir =0 
    player_dir_command = 0 #player_dir : RLUD   ::::   0-RIGHT, 1-LEFT, 2-UP, 3-DOWN

    # ghosts : blinky 0  inky 1  pinky 2 clyde 3   
    GX=[440, 440+45, 440, 440 -45]  # xpos
    GY=[388, 438, 438, 438]         # ypos
    GD=[0]*4                        #direction
    G_EATEN = [0]*4                 # which ??
    G_DEAD= [0]*4                   # ghost dead
    
    level = copy.deepcopy(boards)

reset_game()

gate_position=(440  ,0 )

player_can_move = [0]*4                    # R, L, U, D  open flag for movement

counter = powerup_blink_on = score = powerup_phase = power_counter = 0

player_speed = 2
pos_ghost_targets = [(player_x, player_y) for _ in range(4)] # ghost has each pacman player position!
ghost_speeds = [2]*4

lives = 2

game_over = 0
game_won = 0

def handle_game_over():
    global game_over, moving, startup_counter
    
    game_over = 1
    moving = 0
    startup_counter = 0

class Ghost:
    def __init__(self, x, y, pacman, speed, img, dir, dead, id):
        self.x_pos = x
        self.y_pos = y
        self.center_x = self.x_pos + 23
        self.center_y = self.y_pos + 23
        self.ghost_target = pacman
        self.speed = speed
        self.img = img
        self.dir = dir
        self.dead = dead
        self.id = id
        self.in_box = (350 < self.x_pos < 550 and 370 < self.y_pos < 480)
        self.can_move  = self.check_collisions()
        self.rect = self.draw()

        if debugmode:
            draw.circle(screen, 'green', (self.x_pos + 22, self.y_pos + 22), 20, 1) 
            draw.rect(screen, color='red', rect=self.rect, width=1 )

    def draw(self):
        img=self.img # regular
        if powerup_phase and not G_EATEN[self.id]:  img=spooked_img # powerup and not eaten yet
        if self.dead:                                   img=dead_img    # dead condition is the strongest
        
        screen.blit(img, (self.x_pos, self.y_pos))

            
        return rect.Rect((self.center_x - 18, self.center_y - 18), (36, 36))

    def check_collisions(self):
        self.can_move = [0]*4 #RLUD

        if 0 < self.center_x // 30 < 29:

            cellA = level[(self.center_y - RADIUS) // COUNT_R][self.center_x // COUNT_C]    # up   RADIUS aka num3, COUNT_R aka num1, COUNT_C aka num2
            cellB = level[self.center_y // COUNT_R][(self.center_x - RADIUS) // COUNT_C]    # left
            cellC = level[self.center_y // COUNT_R][(self.center_x + RADIUS) // COUNT_C]    # right
            cellD = level[(self.center_y + RADIUS) // COUNT_R][self.center_x // COUNT_C]    # down
            
            cellE = level[self.center_y // COUNT_R][(self.center_x - COUNT_C) // COUNT_C]
            cellF = level[self.center_y // COUNT_R][(self.center_x + COUNT_C) // COUNT_C]

            not_alive= (self.in_box or self.dead)

            cellcheck=lambda x:x<3 or (x==9 and not_alive)

            is_dirH=self.dir in (0,1)
            is_dirV=self.dir in (2,3)
            in_sweetspot_V= (12 <= self.center_y % COUNT_R <= 18)
            in_sweetspot_H= (12 <= self.center_x % COUNT_C <= 18)

            self.can_move[0] = cellcheck(cellC) or (is_dirV and in_sweetspot_V and cellcheck(cellF)) #or (is_dirH and in_sweetspot_V and cellcheck(cellC))
            self.can_move[1] = cellcheck(cellB) or (is_dirV and in_sweetspot_V and cellcheck(cellE)) #or (is_dirH and in_sweetspot_V and cellcheck(cellB))
            self.can_move[2] = cellcheck(cellA) or (cellA == 9)
            self.can_move[3] = cellcheck(cellD) or (cellD == 9) 

            if self.dead and cellD==9:self.dir=3 # if ghost is dead and down is 9 (home entry) > move down to enter ghost home ##### BUGFIX
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
        CONDS=[cond0,cond1,cond2,cond3]

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

        def decide_dir(a,b,c):
            for i in (a,b,c):
                if self.can_move[i]:self.dir=i
            for i in (a,b,c):
                if CONDS[i]:self.dir=i

        if index==2 or index==3:# GHOST[2] GHOST[3] is going to turn left or right whenever advantageous
            if cond1:   self.dir = 1
            if cond0:   self.dir = 0
                    
        if index==1 or index==3:# GHOST[1] GHOST[3] turns up or down at any point to pursue
            if cond3:    self.dir = 3
            if cond2:    self.dir = 2
            

        # move by direction 
        if self.dir==0: self.x_pos += self.speed
        if self.dir==1: self.x_pos -= self.speed
        if self.dir==2: self.y_pos -= self.speed
        if self.dir==3: self.y_pos += self.speed

        # warp gate
        if self.x_pos < -50:    self.x_pos = 900-3
        elif self.x_pos > 900:  self.x_pos = -50+3

        return self.x_pos, self.y_pos, self.dir

def draw_HUD():
    score_text = myfont.render(f'Score: {score}', True, 'white')
    screen.blit(score_text, (10, 920))
    
    if powerup_phase and debugmode:
        draw.circle(screen, 'blue', (140, 930), 15) # debug

    for i in range(lives):
        screen.blit(transform.scale(player_images[0], (30, 30)), (650 + i * 40, 915))
    
    if game_over or game_won:
        draw.rect(screen, 'white', [50, 200, 800, 300],0, 10)
        draw.rect(screen, 'dark gray', [70, 220, 760, 260], 0, 10)
        message= game_over and 'Game over! Space bar to restart!' or 'Victory! Space bar to restart!'
        color=game_over and 'red' or 'green'
        gameover_text = myfont.render( message, True, color)
        screen.blit(gameover_text, (100, 300))

def check_collisions(scor, power, power_count, G_EATENs):
    if 0 < player_x < 870:
        idx1=center_y // COUNT_R
        idx2=center_x // COUNT_C
        if level[idx1][idx2] == 1:  # normal dot
            level[idx1][idx2] = 0   # remove dot
            scor += 10
        if level[idx1][idx2] == 2:  # power dot
            level[idx1][idx2] = 0   # remove dot
            scor += 50
            power = True
            power_count = 0
            G_EATENs = [0]*4
    return scor, power, power_count, G_EATENs

def draw_board():
    for i in range(len(level)):
        ic=i+.5 # centrized
        for j in range(len(level[0])):
            
            if debugmode:
                draw.rect(screen,color=(0,32,0),rect=(i*COUNT_C, j*COUNT_R, COUNT_C,COUNT_R), width=1)
            

            n_col=j * COUNT_C
            jc=j+.5 # centrized

            

            cell=level[i][j]
            
            # 0 = empty , 1 = dot, 2 = big dot, 3 = vertical line, 4 = horizontal line, 5 = top right, 6 = top left, 7 = bot left, 8 = bot right, 9 = gate
            if cell == 1:   draw.circle(   screen, 'white', (COUNT_C*jc, COUNT_R*ic), 4)
            if cell == 2:   draw.circle(   screen, 'white', (COUNT_C*jc, COUNT_R*ic), 10 if powerup_blink_on else 5)
            if cell == 3:   draw.line(     screen, m_color, (COUNT_C*jc, i * COUNT_R),  (COUNT_C*jc, (i+1)*COUNT_R), 3)
            if cell == 4:   draw.line(     screen, m_color, (n_col, COUNT_R*ic),  (n_col + COUNT_C, COUNT_R*ic), 3)
            if cell == 5:   draw.arc(      screen, m_color, [(n_col - (COUNT_C * 0.4)) - 2, (COUNT_R*ic), COUNT_C, COUNT_R],0, pi / 2, 3)
            if cell == 6:   draw.arc(      screen, m_color, [COUNT_C*jc, COUNT_R*ic, COUNT_C, COUNT_R], pi / 2, pi, 3)
            if cell == 7:   draw.arc(      screen, m_color, [COUNT_C*jc, (i-.4)*COUNT_R, COUNT_C, COUNT_R], pi, 3* pi / 2, 3)            
            if cell == 8:   draw.arc(      screen, m_color, [COUNT_C*(j-.4)- 2, (i-.4) * COUNT_R, COUNT_C, COUNT_R], 3 * pi / 2,2 * pi, 3)
            if cell == 9:   draw.line(     screen, 'white', (n_col, COUNT_R*ic), (n_col + COUNT_C, COUNT_R*ic), 3)
            
            

def draw_player():
    pos=(player_x, player_y)
    img_player=player_images[counter // 5]
    if player_dir == 0:      screen.blit(img_player, pos)
    elif player_dir == 1:    screen.blit(transform.flip(img_player, True, False), pos)
    elif player_dir == 2:    screen.blit(transform.rotate(img_player, 90), pos)
    elif player_dir == 3:    screen.blit(transform.rotate(img_player, -90), pos)

# check collisions based on center x and center y of player +/- RADIUS number
def check_passable(col, row):  # originally check_position
    if 29 <= col // 30 : return [1,1,0,0] # only horizontal warp is passable

    cell_R=level[row // COUNT_R][(col + RADIUS) // COUNT_C]
    cell_L=level[row // COUNT_R][(col - RADIUS) // COUNT_C]
    cell_U=level[(row - RADIUS) // COUNT_R][col // COUNT_C]
    cell_D=level[(row + RADIUS) // COUNT_R][col // COUNT_C]
    dir_H= player_dir in(0,1)
    dir_V= player_dir in(2,3)

    tR = (player_dir in(0,1)and cell_R < 3) or ( dir_V and( 12 <= row % COUNT_R <= 18)and(level[row // COUNT_R][col // COUNT_C + 1] < 3)) 
    tL = (player_dir in(0,1)and cell_L < 3) or ( dir_V and( 12 <= row % COUNT_R <= 18)and(level[row // COUNT_R][col // COUNT_C - 1] < 3))     
    tU = (player_dir in(2,3)and cell_U < 3) or ( dir_H and( 12 <= col % COUNT_C <= 18)and(level[row // COUNT_R - 1][col // COUNT_C] < 3)) 
    tD = (player_dir in(2,3)and cell_D < 3) or ( dir_H and( 12 <= col % COUNT_C <= 18)and(level[row // COUNT_R + 1][col // COUNT_C] < 3)) 

    return [tR,tL,tU,tD]

def get_pos_goal(gR_x, gR_y, gP_x, gP_y, gB_x, gB_y, gY_x, gY_y):
    GHOST_X=[gR_x, gP_x, gB_x, gY_x]
    GHOST_Y=[gR_y, gP_y, gB_y, gY_y]
    
    GHOST_GOALS=[(380, 400)]*4 # ghost home box  as default

    # update ghost's target (pacman, home or  runaway corner)
    for i in range(4):
        in_ghost_home= (350 < GHOST_X[i] < 350  + 200  )and (385 - RADIUS*3 < GHOST_Y[i] < 385 + 100)
        if not GHOST[i].dead:
            if powerup_phase:
                if G_EATEN[i]:  # dead ghost
                    GHOST_GOALS[i] = ((player_x, player_y), (450, 200)) [in_ghost_home]
                else: # spooked ghost
                    GHOST_GOALS[i] = (450, 450) if i==3 else ((0,900)[player_x < 450], (0,900)[player_y < 450])# away from pacman 
            else:
                GHOST_GOALS[i] = (400, 100) if in_ghost_home else (player_x + 22, player_y + 22)
        
        if in_ghost_home:
            GHOST_GOALS[i] = (440, 388-100)


    if debugmode:# draw home collision
        draw.rect(screen, color='green', rect=Rect(350 , 385  ,200, 100),width=1) # box collision
        draw.circle(screen, color='red', center=(380, 400), radius=5 ,width=0) # ghost home
        draw.circle(screen, color='red', center=(450,100), radius=5 ,width=0) # gate target
        for i,goal in enumerate(GHOST_GOALS):
            draw.circle(screen, color=('red','pink','cyan','orange')[i], center=goal, radius=i*2 ,width=1)
            
    return GHOST_GOALS

def player_direction_update():
    global player_dir_command, player_dir, game_over, game_won, lives, run

    for e in event.get():
        run = (e.type != QUIT) 

        if e.type == KEYDOWN:
            player_dir_command={x:i for i,x in enumerate([K_RIGHT,K_LEFT,K_UP,K_DOWN])}.get(e.key, player_dir_command) # key defines player_dir

            if e.key == K_SPACE and (game_over or game_won):
                lives -= 1
                reset_game()

                score = 0
                lives = 2
                game_over = game_won = False

        # player_dir : RLUD
        if e.type == KEYUP:
            if e.key == K_RIGHT and player_dir_command == 0: player_dir_command = player_dir
            if e.key == K_LEFT and player_dir_command == 1:  player_dir_command = player_dir
            if e.key == K_UP and player_dir_command == 2:    player_dir_command = player_dir
            if e.key == K_DOWN and player_dir_command == 3:  player_dir_command = player_dir

    for i in range(4):
        if player_dir_command == i and player_can_move[i]: player_dir = i

def display_FPS():
    # fps display  ### https://stackoverflow.com/questions/67946230/show-fps-in-pygame
    #clock.tick()
    _fps_t = myfont.render(f'FPS: {timer.get_fps():.3f}' , 1, "green")
    screen.blit(_fps_t,(0,0))

def update_ghost_target():
    global pos_ghost_targets
    pos_ghost_targets = get_pos_goal(GX[0], GY[0], GX[1], GY[1], GX[2], GY[2], GX[3], GY[3]) 

run = True
while run:

    timer.tick(FPS)# clock

    counter += 1
    counter %= 20
    
    powerup_blink_on = (7 < counter)

    if powerup_phase:
        power_counter += 1
        power_counter %= 600
        if power_counter==0:
            powerup_phase = 0
            G_EATEN = [0]*4     

    moving = True
    #if startup_counter < 180 and not game_over and not game_won:
    if startup_counter < 180:
        moving = False
        startup_counter += 1
        
    screen.fill('black')
    
    draw_board()
    center_x = player_x + 23 # due to 45 pixel image
    center_y = player_y + 23 # due to 45 pixel image

    ghost_speeds = [ (2,1)[powerup_phase] ]*4

    for i in range(4):
        if G_EATEN[i]:  ghost_speeds[i] = 2 # slower when spooked
        if G_DEAD[i]:   ghost_speeds[i] = 4 # faster when dead

    level_1D=sum(level,[])
    count_dot=level_1D.count(1)
    count_powerdot=level_1D.count(2)
    game_won = (count_dot + count_powerdot == 0)

    player_collision = draw.circle(screen, ((0,0,0,0),'green')[debugmode] , (center_x, center_y), 20, (1,1)[debugmode]) # debug
    draw_player()
    
    # ghost update
    GHOST=[Ghost(GX[i], GY[i], pos_ghost_targets[i], ghost_speeds[i], G_IMG[i], GD[i], G_DEAD[i], i) for i in range(4)]

    draw_HUD()

    # Ghost target update
    update_ghost_target()
    

    player_can_move = check_passable(center_x, center_y)

    if moving:

        if player_can_move[player_dir]:
            if player_dir == 0:      player_x += player_speed
            elif player_dir == 1 :   player_x -= player_speed
            elif player_dir == 2 :   player_y -= player_speed
            elif player_dir == 3 :   player_y += player_speed
            
        for i in range(4):    
            if GHOST[i].in_box or G_DEAD[i]: # if 
                GX[i], GY[i], GD[i] = GHOST[i].move_G(3)
            else:
                GX[i], GY[i], GD[i] = GHOST[i].move_G(i)



    score, powerup_phase, power_counter, G_EATEN = check_collisions(score, powerup_phase, power_counter, G_EATEN)
    # add to if not powerup_phase to check if eaten ghosts
    if not powerup_phase:
        if any ( player_collision.colliderect(GHOST[i].rect) and not GHOST[i].dead for i in range(4)):
            if 0 < lives:
                lives -= 1       
                reset_game()
            else:
                handle_game_over()
    else: # i.e. powerup_phase

        # active ghost hit pacman
        for i in range(4):
            if player_collision.colliderect(GHOST[i].rect) and not GHOST[i].dead:
                if G_EATEN[i]:  # ghost eat pacman , so game reset
                    if 0 < lives:
                        lives -= 1
                        reset_game()
                    else:
                        handle_game_over()
                        
                else: # pacman eat ghost
                    G_DEAD[i] = G_EATEN[i] = True
                    score += (2 ** G_EATEN.count(True)) * 100

    player_direction_update()

    # player warp gate
    if player_x > 900:      player_x = -50+3
    elif player_x < -50:    player_x = 900-3
    
    # revive the ghosts if in the home box
    for i in range(4):
        if GHOST[i].in_box and G_DEAD[i]:
            G_DEAD[i] = False

    display_FPS()

    display.flip()

quit()