# Build Pac-Man from Scratch in Python with PyGame!!
# done until 1:26:45  , maybe around 3:40 to start then come back with shorter code 

import copy

from pygame import init, display, time, font, transform, image, rect, event, QUIT, KEYDOWN, KEYUP, K_RIGHT, K_LEFT, K_UP, K_DOWN, K_SPACE, draw
from math import pi
from random import randint

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
debugmode=0

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
    
    player_x = 450 - 20 # centerize
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
        
player_can_move = [0]*4                    # R, L, U, D  open flag for movement


counter = powerup_blink_on = score = powerup_phase = power_counter = 0

pause = 1

player_speed = 2
pos_pacman = [(player_x, player_y), (player_x, player_y), (player_x, player_y), (player_x, player_y)] # ghost has each pacman player position!
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
    def __init__(self, x, y, pacman, speed, img, direct, dead,id):
        self.x_pos = x
        self.y_pos = y
        self.center_x = self.x_pos + 23
        self.center_y = self.y_pos + 23
        self.pacman = pacman
        self.speed = speed
        self.img = img
        self.dir = direct
        self.dead = dead
        self.id = id
        self.in_box =0
        self.can_move, self.in_box = self.check_collisions()
        self.rect = self.draw()

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

        self.in_box = (350 < self.x_pos < 550 and 370 < self.y_pos < 480) # ghost is in box or not

        return self.can_move, self.in_box

    def move_G(self, index):   # GHOST[0] : clyde doesn't change direction unless hit . random to left or right

        pacman_x, pacman_y = self.pacman

        # direction : RLUD 
        # direction change if blocked by the wall
        
        if index==0:
            if self.dir == 0 and not self.can_move[0]: # hit the collision
                if self.can_move[2] and self.can_move[3]:  self.dir=(3,2)[self.y_pos < pacman_y] # if both open ,try to follow pacman  
                elif self.can_move[2]: self.dir=2 
                elif self.can_move[3]: self.dir=3
                else: self.dir = 1    # backward
            elif self.dir == 1 and not self.can_move[1]:
                if self.can_move[2] and self.can_move[3]:  self.dir=(3,2)[self.y_pos < pacman_y] # if both open ,try to follow pacman  
                elif self.can_move[2]: self.dir=2 
                elif self.can_move[3]: self.dir=3
                else: self.dir = 0    # backward
            elif self.dir == 2 and not self.can_move[2]:
                if self.can_move[0] and self.can_move[1]:  self.dir=(1,0)[self.x_pos < pacman_x] # if both open ,try to follow pacman
                elif self.can_move[0]: self.dir=0 
                elif self.can_move[1]: self.dir=1
                else: self.dir=3    # backward
            elif self.dir == 3 and not self.can_move[3]:
                if self.can_move[0] and self.can_move[1]:  self.dir=(1,0)[self.x_pos < pacman_x] # if both open ,try to follow pacman
                elif self.can_move[0]: self.dir=0 
                elif self.can_move[1]: self.dir=1
                else: self.dir=2    # backward

        if index==1:# GHOST[1] turns up or down at any point to pursue, but left and right only on collision
            if self.dir == 0:
                if pacman_x > self.x_pos and self.can_move[0]:        pass
                elif not self.can_move[0]:
                    if pacman_y > self.y_pos and self.can_move[3]:    self.dir = 3
                    elif pacman_y < self.y_pos and self.can_move[2]:  self.dir = 2
                    elif pacman_x < self.x_pos and self.can_move[1]:  self.dir = 1
                    elif self.can_move[3]:                        self.dir = 3
                    elif self.can_move[2]:                        self.dir = 2
                    elif self.can_move[1]:                        self.dir = 1
                elif self.can_move[0]:
                    if pacman_y > self.y_pos and self.can_move[3]:    self.dir = 3
                    if pacman_y < self.y_pos and self.can_move[2]:    self.dir = 2
            elif self.dir == 1:
                if pacman_y > self.y_pos and self.can_move[3]:        self.dir = 3
                elif pacman_x < self.x_pos and self.can_move[1]:      pass
                elif not self.can_move[1]:
                    if pacman_y > self.y_pos and self.can_move[3]:    self.dir = 3
                    elif pacman_y < self.y_pos and self.can_move[2]:  self.dir = 2
                    elif pacman_x > self.x_pos and self.can_move[0]:  self.dir = 0
                    elif self.can_move[3]:                                  self.dir = 3
                    elif self.can_move[2]:                                  self.dir = 2
                    elif self.can_move[0]:                                  self.dir = 0
                elif self.can_move[1]:
                    if pacman_y > self.y_pos and self.can_move[3]:    self.dir = 3
                    if pacman_y < self.y_pos and self.can_move[2]:    self.dir = 2
            elif self.dir == 2:
                if pacman_y < self.y_pos and self.can_move[2]:        pass
                elif not self.can_move[2]:
                    if pacman_x > self.x_pos and self.can_move[0]:    self.dir = 0
                    elif pacman_x < self.x_pos and self.can_move[1]:  self.dir = 1
                    elif pacman_y > self.y_pos and self.can_move[3]:  self.dir = 3
                    elif self.can_move[1]:                                  self.dir = 1
                    elif self.can_move[3]:                                  self.dir = 3
                    elif self.can_move[0]:                                  self.dir = 0
            elif self.dir == 3:
                if pacman_y > self.y_pos and self.can_move[3]:        pass
                elif not self.can_move[3]:
                    if pacman_x > self.x_pos and self.can_move[0]:    self.dir = 0
                    elif pacman_x < self.x_pos and self.can_move[1]:  self.dir = 1
                    elif pacman_y < self.y_pos and self.can_move[2]:  self.dir = 2
                    elif self.can_move[2]:                                  self.dir = 2
                    elif self.can_move[1]:                                  self.dir = 1
                    elif self.can_move[0]:                                  self.dir = 0
                    
        if index==2:# GHOST[2] is going to turn left or right whenever advantageous, but only up or down on collision
            if self.dir == 0:
                if pacman_x > self.x_pos and self.can_move[0]:        pass
                elif not self.can_move[0]:
                    if pacman_y > self.y_pos and self.can_move[3]:    self.dir = 3
                    elif pacman_y < self.y_pos and self.can_move[2]:  self.dir = 2
                    elif pacman_x < self.x_pos and self.can_move[1]:  self.dir = 1
                    elif self.can_move[3]:                        self.dir = 3
                    elif self.can_move[2]:                        self.dir = 2
                    elif self.can_move[1]:                        self.dir = 1
            elif self.dir == 1:
                if pacman_y > self.y_pos and self.can_move[3]:                self.dir = 3
                elif pacman_x < self.x_pos and self.can_move[1]:              pass
                elif not self.can_move[1]:
                    if pacman_y > self.y_pos and self.can_move[3]:                        self.dir = 3
                    elif pacman_y < self.y_pos and self.can_move[2]:                        self.dir = 2
                    elif pacman_x > self.x_pos and self.can_move[0]:                        self.dir = 0
                    elif self.can_move[3]:                        self.dir = 3
                    elif self.can_move[2]:                        self.dir = 2
                    elif self.can_move[0]:                        self.dir = 0
            elif self.dir == 2:
                if pacman_x < self.x_pos and self.can_move[1]:                    self.dir = 1
                elif pacman_y < self.y_pos and self.can_move[2]:                    pass
                elif not self.can_move[2]:
                    if pacman_x > self.x_pos and self.can_move[0]:                        self.dir = 0
                    elif pacman_x < self.x_pos and self.can_move[1]:                        self.dir = 1
                    elif pacman_y > self.y_pos and self.can_move[3]:                        self.dir = 3
                    elif self.can_move[1]:                        self.dir = 1
                    elif self.can_move[3]:                        self.dir = 3
                    elif self.can_move[0]:                        self.dir = 0
                elif self.can_move[2]:
                    if pacman_x > self.x_pos and self.can_move[0]:                        self.dir = 0
                    elif pacman_x < self.x_pos and self.can_move[1]:                        self.dir = 1
            elif self.dir == 3:
                if pacman_y > self.y_pos and self.can_move[3]:                pass
                elif not self.can_move[3]:
                    if pacman_x > self.x_pos and self.can_move[0]:                        self.dir = 0
                    elif pacman_x < self.x_pos and self.can_move[1]:                        self.dir = 1
                    elif pacman_y < self.y_pos and self.can_move[2]:                        self.dir = 2
                    elif self.can_move[2]:                        self.dir = 2
                    elif self.can_move[1]:                        self.dir = 1
                    elif self.can_move[0]:                        self.dir = 0
                elif self.can_move[3]:
                    if pacman_x > self.x_pos and self.can_move[0]:    self.dir = 0
                    elif pacman_x < self.x_pos and self.can_move[1]:  self.dir = 1
                    
        if index==3:# GHOST[3] is going to turn whenever advantageous for pursuit
            if self.dir == 0:
                if pacman_x > self.x_pos and self.can_move[0]:   pass
                elif not self.can_move[0]:
                    if pacman_y > self.y_pos and self.can_move[3]:                        self.dir = 3
                    elif pacman_y < self.y_pos and self.can_move[2]:                        self.dir = 2
                    elif pacman_x < self.x_pos and self.can_move[1]:                        self.dir = 1
                    elif self.can_move[3]:                        self.dir = 3
                    elif self.can_move[2]:                        self.dir = 2
                    elif self.can_move[1]:                        self.dir = 1
                elif self.can_move[0]:
                    if pacman_y > self.y_pos and self.can_move[3]:                        self.dir = 3
                    if pacman_y < self.y_pos and self.can_move[2]:                        self.dir = 2
            elif self.dir == 1:
                if pacman_y > self.y_pos and self.can_move[3]:   self.dir = 3
                elif pacman_x < self.x_pos and self.can_move[1]: pass
                elif not self.can_move[1]:
                    if pacman_y > self.y_pos and self.can_move[3]:                        self.dir = 3
                    elif pacman_y < self.y_pos and self.can_move[2]:                        self.dir = 2
                    elif pacman_x > self.x_pos and self.can_move[0]:                        self.dir = 0
                    elif self.can_move[3]:                        self.dir = 3
                    elif self.can_move[2]:                        self.dir = 2
                    elif self.can_move[0]:                        self.dir = 0
                elif self.can_move[1]:
                    if pacman_y > self.y_pos and self.can_move[3]:    self.dir = 3
                    if pacman_y < self.y_pos and self.can_move[2]:    self.dir = 2
            elif self.dir == 2:
                if pacman_x < self.x_pos and self.can_move[1]:        self.dir = 1
                elif pacman_y < self.y_pos and self.can_move[2]:      pass
                elif not self.can_move[2]:
                    if pacman_x > self.x_pos and self.can_move[0]:    self.dir = 0
                    elif pacman_x < self.x_pos and self.can_move[1]:  self.dir = 1
                    elif pacman_y > self.y_pos and self.can_move[3]:  self.dir = 3
                    elif self.can_move[1]:                        self.dir = 1
                    elif self.can_move[3]:                        self.dir = 3
                    elif self.can_move[0]:                        self.dir = 0
                elif self.can_move[2]:
                    if pacman_x > self.x_pos and self.can_move[0]:    self.dir = 0
                    elif pacman_x < self.x_pos and self.can_move[1]:  self.dir = 1
            elif self.dir == 3:
                if pacman_y > self.y_pos and self.can_move[3]:                            pass
                elif not self.can_move[3]:
                    if pacman_x > self.x_pos and self.can_move[0]:                        self.dir = 0
                    elif pacman_x < self.x_pos and self.can_move[1]:self.dir = 1
                    elif pacman_y < self.y_pos and self.can_move[2]:self.dir = 2
                    elif self.can_move[2]:                        self.dir = 2
                    elif self.can_move[1]:                        self.dir = 1
                    elif self.can_move[0]:                        self.dir = 0
                elif self.can_move[3]:
                    if pacman_x > self.x_pos and self.can_move[0]:    self.dir = 0
                    elif pacman_x < self.x_pos and self.can_move[1]:  self.dir = 1

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
        for j in range(len(level[i])):
            n_col=j * COUNT_C
            jc=j+.5 # centrized
            cell=level[i][j]
            
            # 0 = empty , 1 = dot, 2 = big dot, 3 = vertical line, 4 = horizontal line, 5 = top right, 6 = top left, 7 = bot left, 8 = bot right, 9 = gate
            if cell == 1:                       draw.circle(   screen, 'white', (COUNT_C*jc, COUNT_R*ic), 4)
            if cell == 2 and powerup_blink_on:  draw.circle(   screen, 'white', (COUNT_C*jc, COUNT_R*ic), 10)
            if cell == 3:                       draw.line(     screen, m_color, (COUNT_C*jc, i * COUNT_R),  (COUNT_C*jc, (i+1)*COUNT_R), 3)
            if cell == 4:                       draw.line(     screen, m_color, (n_col, COUNT_R*ic),  (n_col + COUNT_C, COUNT_R*ic), 3)
            if cell == 5:                       draw.arc(      screen, m_color, [(n_col - (COUNT_C * 0.4)) - 2, (COUNT_R*ic), COUNT_C, COUNT_R],0, pi / 2, 3)
            if cell == 6:                       draw.arc(      screen, m_color, [COUNT_C*jc, COUNT_R*ic, COUNT_C, COUNT_R], pi / 2, pi, 3)
            if cell == 7:                       draw.arc(      screen, m_color, [COUNT_C*jc, (i-.4)*COUNT_R, COUNT_C, COUNT_R], pi, 3* pi / 2, 3)            
            if cell == 8:                       draw.arc(      screen, m_color, [COUNT_C*(j-.4)- 2, (i-.4) * COUNT_R, COUNT_C, COUNT_R], 3 * pi / 2,2 * pi, 3)
            if cell == 9:                       draw.line(     screen, 'white', (n_col, COUNT_R*ic), (n_col + COUNT_C, COUNT_R*ic), 3)

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

def get_pos_goal(blink_x, blink_y, ink_x, ink_y, pink_x, pink_y, clyd_x, clyd_y):
    GHOST_X=[blink_x, ink_x, pink_x, clyd_x]
    GHOST_Y=[blink_y, ink_y, pink_y, clyd_y]

    runaway_x = (0,900)[player_x < 450]# away from pacman 
    runaway_y = (0,900)[player_y < 450]# away from pacman 
    
    ghost_home = (380, 400) # ghost home box
    
    GHOST_GOALS=[ghost_home]*4

    if powerup_phase:
        for i in range(4):
            at_ghost_home_door= (340 < GHOST_X[i] < 560)and (340 < GHOST_Y[i] < 500)
            if not GHOST[i].dead:
                if G_EATEN[i]:  GHOST_GOALS[i] = (400, 100) if at_ghost_home_door else  (player_x, player_y)
                else: GHOST_GOALS[i] = (450, 450) if i==3 else (runaway_x, runaway_y)
    else:
        for i in range(4):
            if not GHOST[i].dead:
                GHOST_GOALS[i] = (400, 100)if 340 < GHOST_X[i] < 560 and 340 < GHOST_Y[i] < 500 else(player_x, player_y)

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

run = True
while run:

    timer.tick(FPS)# clock

    counter += 1
    counter %= 20
    #print(timer, counter)
    
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
    
    GHOST=[Ghost(GX[i], GY[i], pos_pacman[i], ghost_speeds[i], G_IMG[i], GD[i], G_DEAD[i], i) for i in range(4)]

    draw_HUD()
    pos_pacman = get_pos_goal(GX[0], GY[0], GX[1], GY[1], GX[2], GY[2], GX[3], GY[3]) # targets

    player_can_move = check_passable(center_x, center_y)

    if moving:

        if player_can_move[player_dir]:
            if player_dir == 0:      player_x += player_speed
            elif player_dir == 1 :   player_x -= player_speed
            elif player_dir == 2 :   player_y -= player_speed
            elif player_dir == 3 :   player_y += player_speed
            
        for i in range(3):    GX[i], GY[i], GD[i] = GHOST[i].move_G(i if not G_DEAD[i] and not GHOST[i].in_box else  3)
        GX[3], GY[3], GD[3] = GHOST[3].move_G(3)

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