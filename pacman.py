# Build Pac-Man from Scratch in Python with PyGame!!
# done until 1:26:45  , maybe around 2:02 to start then come back with shorter code 

import copy
from board import boards

from pygame import init, display, time, font, transform, image, rect, event, QUIT, KEYDOWN, KEYUP, K_RIGHT, K_LEFT, K_UP, K_DOWN, K_SPACE, draw
from math import pi

init()

fps = 60
WIDTH = 900
HEIGHT = 950

COUNT_R = (HEIGHT - 50) // 32   # grid row count
COUNT_C = (WIDTH // 30)         # grid column count
RADIUS = 15 # buffer so that player don't hit the cell while there is a space between the edge and the actual wall

screen = display.set_mode([WIDTH, HEIGHT])
timer = time.Clock()
font = font.Font('freesansbold.ttf', 20)
level = copy.deepcopy(boards)
m_color = 'blue'

# image assets
img_size=(45, 45)
player_images = [transform.scale(image.load(f'assets/player_images/{i}.png'),img_size) for i in (1,2,3,2)]# 4 images
G_IMG=          [transform.scale(image.load(f'assets/ghost_images/{x}.png'),img_size) for x in 'red pink blue orange'.split()]
spooked_img =   transform.scale(image.load(f'assets/ghost_images/powerup.png'),img_size)
dead_img =      transform.scale(image.load(f'assets/ghost_images/dead.png'),img_size)

player_x = 450 - 20 # centerize
player_y = 663
player_dir = player_dir_command = 0 #player_dir : RLUD   ::::   0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
can_move = [0]*4                    # R, L, U, D  open flag for movement

# ghosts : blinky 0  inky 1  pinky 2 clyde 3           
GX=[440, 440+45, 440, 440 -45]  # xpos      
GY=[388, 438, 438, 438]         # ypos
GD=[0]*4                        #direction
eaten_ghost = [0]*4             # which ??
G_DEAD= [0]*4                   # ghost dead
G_BOX= [0]*4                    # ghost in spawn box

counter = powerup_blink_on = score = powerup_phase = power_counter = moving = 0
player_speed = 2
targets = [(player_x, player_y), (player_x, player_y), (player_x, player_y), (player_x, player_y)]
ghost_speeds = [2, 2, 2, 2]
startup_counter = 0
lives = 3
game_over = game_won = 0

class Ghost:
    def __init__(self, x, y, target, speed, img, direct, dead, box, id):
        self.x_pos = x
        self.y_pos = y
        self.center_x = self.x_pos + 23
        self.center_y = self.y_pos + 23
        self.target = target
        self.speed = speed
        self.img = img
        self.dir = direct
        self.dead = dead
        self.in_box = box
        self.id = id
        self.turns, self.in_box = self.check_collisions()
        self.rect = self.draw()

    def draw(self):
        img=self.img # regular
        if powerup_phase and not eaten_ghost[self.id]:  img=spooked_img # powerup and not eaten yet
        if self.dead:                                   img=dead_img    # dead condition is the strongest
        
        screen.blit(img, (self.x_pos, self.y_pos))
        return rect.Rect((self.center_x - 18, self.center_y - 18), (36, 36))

    def check_collisions(self):
        self.turns = [0]*4

        if 0 < self.center_x // 30 < 29:
            cellA = level[(self.center_y - RADIUS) // COUNT_R][self.center_x // COUNT_C]
            cellB = level[self.center_y // COUNT_R][(self.center_x - RADIUS) // COUNT_C]
            cellC = level[self.center_y // COUNT_R][(self.center_x + RADIUS) // COUNT_C]
            cellD = level[(self.center_y + RADIUS) // COUNT_R][self.center_x // COUNT_C]
            cellE = level[self.center_y // COUNT_R][(self.center_x - COUNT_C) // COUNT_C]
            cellF = level[self.center_y // COUNT_R][(self.center_x + COUNT_C) // COUNT_C]

            not_alive= (self.in_box or self.dead)

            is_dirV=self.dir in (2,3)
            is_dirH=self.dir in (0,1)
            cellcheck=lambda x:x<3 or (x==9 and not_alive)
            in_sweetspot_V= (12 <= self.center_y % COUNT_R <= 18)
            in_sweetspot_H= (12 <= self.center_x % COUNT_C <= 18)

            self.turns[0] = cellcheck(cellC) or (is_dirV and in_sweetspot_V and cellcheck(cellF)) #or (is_dirH and in_sweetspot_V and cellcheck(cellC))
            self.turns[1] = cellcheck(cellB) or (is_dirV and in_sweetspot_V and cellcheck(cellE)) #or (is_dirH and in_sweetspot_V and cellcheck(cellB))
            self.turns[2] = cellcheck(cellA) or (cellA == 9)
            self.turns[3] = cellcheck(cellD) or (is_dirV and in_sweetspot_H and cellcheck(cellD)) #or (is_dirH and in_sweetspot_H and cellcheck(cellD))

        else: self.turns[0] = self.turns[1] = 1
        self.in_box = (350 < self.x_pos < 550 and 370 < self.y_pos < 480)

        return self.turns, self.in_box


    def move_G0(self):   # GHOST[0] is going to turn whenever colliding with walls, otherwise continue straight
        if self.dir == 0:
            if self.target[0] > self.x_pos and self.turns[0]:                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.dir = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.dir = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.dir = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.dir = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:                self.x_pos += self.speed
        elif self.dir == 1:
            if self.target[0] < self.x_pos and self.turns[1]:                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.dir = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.dir = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.dir = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.dir = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
            elif self.turns[1]:                self.x_pos -= self.speed
        elif self.dir == 2:
            if self.target[1] < self.y_pos and self.turns[2]:
                self.dir = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.dir = 3
                    self.y_pos += self.speed
                elif self.turns[3]:
                    self.dir = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
                elif self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
            elif self.turns[2]:                self.y_pos -= self.speed
        elif self.dir == 3:
            if self.target[1] > self.y_pos and self.turns[3]:                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.dir = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.dir = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
                elif self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
            elif self.turns[3]:                self.y_pos += self.speed
        if self.x_pos < -30:            self.x_pos = 900
        elif self.x_pos > 900:            self.x_pos - 30
        return self.x_pos, self.y_pos, self.dir

    def move_G1(self):# GHOST[1] turns up or down at any point to pursue, but left and right only on collision
        if self.dir == 0:
            if self.target[0] > self.x_pos and self.turns[0]:                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.dir = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.dir = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.dir = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.dir = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.dir = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.dir = 2
                    self.y_pos -= self.speed
                else:                    self.x_pos += self.speed
        elif self.dir == 1:
            if self.target[1] > self.y_pos and self.turns[3]:                self.dir = 3
            elif self.target[0] < self.x_pos and self.turns[1]:                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.dir = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.dir = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.dir = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.dir = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.dir = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.dir = 2
                    self.y_pos -= self.speed
                else:                    self.x_pos -= self.speed
        elif self.dir == 2:
            if self.target[1] < self.y_pos and self.turns[2]:
                self.dir = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.dir = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.dir = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
            elif self.turns[2]:
                self.y_pos -= self.speed
        elif self.dir == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.dir = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.dir = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                self.y_pos += self.speed
        if self.x_pos < -30:            self.x_pos = 900
        elif self.x_pos > 900:            self.x_pos - 30
        return self.x_pos, self.y_pos, self.dir

    def move_G2(self):# GHOST[2] is going to turn left or right whenever advantageous, but only up or down on collision
        if self.dir == 0:
            if self.target[0] > self.x_pos and self.turns[0]:                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.dir = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.dir = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.dir = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.dir = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:                self.x_pos += self.speed
        elif self.dir == 1:
            if self.target[1] > self.y_pos and self.turns[3]:                self.dir = 3
            elif self.target[0] < self.x_pos and self.turns[1]:                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.dir = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.dir = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.dir = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.dir = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
            elif self.turns[1]:                self.x_pos -= self.speed
        elif self.dir == 2:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.dir = 1
                self.x_pos -= self.speed
            elif self.target[1] < self.y_pos and self.turns[2]:
                self.dir = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.dir = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.dir = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
            elif self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
                else:                    self.y_pos -= self.speed
        elif self.dir == 3:
            if self.target[1] > self.y_pos and self.turns[3]:                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.dir = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.dir = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
                else:                    self.y_pos += self.speed
        if self.x_pos < -30:            self.x_pos = 900
        elif self.x_pos > 900:            self.x_pos - 30
        return self.x_pos, self.y_pos, self.dir

    def move_G3(self): # GHOST[3] is going to turn whenever advantageous for pursuit
        if self.dir == 0:
            if self.target[0] > self.x_pos and self.turns[0]:   self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.dir = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.dir = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.dir = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.dir = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.dir = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.dir = 2
                    self.y_pos -= self.speed
                else:                    self.x_pos += self.speed
        elif self.dir == 1:
            if self.target[1] > self.y_pos and self.turns[3]:   self.dir = 3
            elif self.target[0] < self.x_pos and self.turns[1]: self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.dir = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.dir = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.dir = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.dir = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.dir = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.dir = 2
                    self.y_pos -= self.speed
                else:   self.x_pos -= self.speed
        elif self.dir == 2:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.dir = 1
                self.x_pos -= self.speed
            elif self.target[1] < self.y_pos and self.turns[2]:
                self.dir = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.dir = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.dir = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
            elif self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
                else:                    self.y_pos -= self.speed
        elif self.dir == 3:
            if self.target[1] > self.y_pos and self.turns[3]:                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.dir = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.dir = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
                else:self.y_pos += self.speed
        self.x_pos = (self.x_pos < -30 and 900) or ( self.x_pos > 900 and self.x_pos - 30) or self.x_pos            
        return self.x_pos, self.y_pos, self.dir


def draw_misc():
    score_text = font.render(f'Score: {score}', True, 'white')
    screen.blit(score_text, (10, 920))
    
    if powerup_phase:        draw.circle(screen, 'blue', (140, 930), 15)

    for i in range(lives):        screen.blit(transform.scale(player_images[0], (30, 30)), (650 + i * 40, 915))
    
    if game_over or game_won:
        draw.rect(screen, 'white', [50, 200, 800, 300],0, 10)
        draw.rect(screen, 'dark gray', [70, 220, 760, 260], 0, 10)
        message= game_over and 'Game over! Space bar to restart!' or 'Victory! Space bar to restart!'
        color=game_over and 'red' or 'green'
        gameover_text = font.render( message, True, color)
        screen.blit(gameover_text, (100, 300))

def check_collisions(scor, power, power_count, eaten_ghosts):
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
            eaten_ghosts = [0]*4
    return scor, power, power_count, eaten_ghosts

def draw_board():
    for i in range(len(level)):
        ic=i+.5 # centrized
        for j in range(len(level[i])):
            n_col=j * COUNT_C
            jc=j+.5 # centrized
            cell=level[i][j]
            
            # 0 = empty , 1 = dot, 2 = big dot, 3 = vertical line, 4 = horizontal line, 5 = top right, 6 = top left, 7 = bot left, 8 = bot right, 9 = gate
            if cell == 1:                draw.circle(   screen, 'white', (COUNT_C*jc, COUNT_R*ic), 4)
            if cell == 2 and powerup_blink_on:draw.circle(   screen, 'white', (COUNT_C*jc, COUNT_R*ic), 10)
            if cell == 3:                draw.line(     screen, m_color, (COUNT_C*jc, i * COUNT_R),  (COUNT_C*jc, (i+1)*COUNT_R), 3)
            if cell == 4:                draw.line(     screen, m_color, (n_col, COUNT_R*ic),  (n_col + COUNT_C, COUNT_R*ic), 3)
            if cell == 5:                draw.arc(      screen, m_color, [(n_col - (COUNT_C * 0.4)) - 2, (COUNT_R*ic), COUNT_C, COUNT_R],0, pi / 2, 3)
            if cell == 6:                draw.arc(      screen, m_color, [COUNT_C*jc, COUNT_R*ic, COUNT_C, COUNT_R], pi / 2, pi, 3)
            if cell == 7:                draw.arc(      screen, m_color, [COUNT_C*jc, (i-.4)*COUNT_R, COUNT_C, COUNT_R], pi, 3* pi / 2, 3)            
            if cell == 8:                draw.arc(      screen, m_color, [COUNT_C*(j-.4)- 2, (i-.4) * COUNT_R, COUNT_C, COUNT_R], 3 * pi / 2,2 * pi, 3)
            if cell == 9:                draw.line(     screen, 'white', (n_col, COUNT_R*ic), (n_col + COUNT_C, COUNT_R*ic), 3)

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

def move_player(play_x, play_y):
    if can_move[player_dir]:
        if player_dir == 0:      play_x += player_speed
        elif player_dir == 1 :   play_x -= player_speed
        elif player_dir == 2 :   play_y -= player_speed
        elif player_dir == 3 :   play_y += player_speed
    return play_x, play_y

def get_targets(blink_x, blink_y, ink_x, ink_y, pink_x, pink_y, clyd_x, clyd_y):
    if player_x < 450:        runaway_x = 900
    else:        runaway_x = 0
    if player_y < 450:        runaway_y = 900
    else:        runaway_y = 0
    return_target = (380, 400)
    if powerup_phase:
        if not GHOST[0].dead and not eaten_ghost[0]:            blink_target = (runaway_x, runaway_y)
        elif not GHOST[0].dead and eaten_ghost[0]:  blink_target = (400, 100) if 340 < blink_x < 560 and 340 < blink_y < 500 else  (player_x, player_y)
        else:                                       blink_target = return_target
        if not GHOST[1].dead and not eaten_ghost[1]:            ink_target = (runaway_x, player_y)
        elif not GHOST[1].dead and eaten_ghost[1]:
            if 340 < ink_x < 560 and 340 < ink_y < 500:                ink_target = (400, 100)
            else:                ink_target = (player_x, player_y)
        else:            ink_target = return_target
        if not GHOST[2].dead:            pink_target = (player_x, runaway_y)
        elif not GHOST[2].dead and eaten_ghost[2]:
            if 340 < pink_x < 560 and 340 < pink_y < 500:                pink_target = (400, 100)
            else:                pink_target = (player_x, player_y)
        else:            pink_target = return_target
        if not GHOST[3].dead and not eaten_ghost[3]:            clyd_target = (450, 450)
        elif not GHOST[3].dead and eaten_ghost[3]:
            if 340 < clyd_x < 560 and 340 < clyd_y < 500:                clyd_target = (400, 100)
            else:                clyd_target = (player_x, player_y)
        else:            clyd_target = return_target
    else:
        if not GHOST[0].dead:
            if 340 < blink_x < 560 and 340 < blink_y < 500:                blink_target = (400, 100)
            else:                blink_target = (player_x, player_y)
        else:            blink_target = return_target
        if not GHOST[1].dead:
            if 340 < ink_x < 560 and 340 < ink_y < 500:                ink_target = (400, 100)
            else:                ink_target = (player_x, player_y)
        else:            ink_target = return_target
        if not GHOST[2].dead:
            if 340 < pink_x < 560 and 340 < pink_y < 500:                pink_target = (400, 100)
            else:                pink_target = (player_x, player_y)
        else:            pink_target = return_target
        if not GHOST[3].dead:
            if 340 < clyd_x < 560 and 340 < clyd_y < 500:                clyd_target = (400, 100)
            else:                clyd_target = (player_x, player_y)
        else:            clyd_target = return_target
    return [blink_target, ink_target, pink_target, clyd_target]

run = True
while run:
    
    timer.tick(fps)

    counter += 1
    counter %= 20
    
    powerup_blink_on = (7 < counter)

    if powerup_phase and power_counter < 600:
        power_counter += 1
    elif powerup_phase and power_counter >= 600:
        power_counter = 0
        powerup_phase = False
        eaten_ghost = [0]*4
    if startup_counter < 180 and not game_over and not game_won:
        moving = False
        startup_counter += 1
    else:
        moving = True

    screen.fill('black')
    
    draw_board()

    center_x = player_x + 23 # due to 45 pixel image
    center_y = player_y + 23 # due to 45 pixel image

    ghost_speeds = [ powerup_phase and 1 or 2]*4
    for i in range(4):
        if eaten_ghost[i]:ghost_speeds[i] = 2
        if G_DEAD[i]:ghost_speeds[i] = 4

    game_won = True
    for i in range(len(level)):
        if 1 in level[i] or 2 in level[i]:game_won = False

    player_circle = draw.circle(screen, 'black', (center_x, center_y), 20, 2)

    draw_player()
    
    GHOST=[Ghost(GX[i], GY[i], targets[i], ghost_speeds[i], G_IMG[i], GD[i], G_DEAD[i],G_BOX[i], i) for i in range(4)]

    draw_misc()
    targets = get_targets(GX[0], GY[0], GX[1], GY[1], GX[2], GY[2], GX[3], GY[3])

    can_move = check_passable(center_x, center_y)

    if moving:
        player_x, player_y = move_player(player_x, player_y)
        
        if not G_DEAD[0] and not GHOST[0].in_box:
            GX[0], GY[0], GD[0] = GHOST[0].move_G0()
        else:            
            GX[0], GY[0], GD[0] = GHOST[0].move_G3()
        
        if not G_DEAD[2] and not GHOST[2].in_box:            
            GX[2], GY[2], GD[2] = GHOST[2].move_G2()
        else:            
            GX[2], GY[2], GD[2] = GHOST[2].move_G3()
        
        if not G_DEAD[1] and not GHOST[1].in_box:            
            GX[1], GY[1], GD[1] = GHOST[1].move_G1()
        else:            
            GX[1], GY[1], GD[1] = GHOST[1].move_G3()

        GX[3], GY[3], GD[3] = GHOST[3].move_G3()
    score, powerup_phase, power_counter, eaten_ghost = check_collisions(score, powerup_phase, power_counter, eaten_ghost)
    # add to if not powerup_phase to check if eaten ghosts
    if not powerup_phase:
        if any (player_circle.colliderect(x) and not y for x,y in ((GHOST[0].rect, GHOST[0].dead),(GHOST[1].rect, GHOST[1].dead),(GHOST[2].rect, GHOST[2].dead),(GHOST[3].rect, GHOST[3].dead)) ):
            if lives > 0:
                lives -= 1
                startup_counter = powerup_phase = power_counter = 0
                
                player_x = 450
                player_y = 663
                
                player_dir = player_dir_command = 0
                
                GX=[440, 440+45, 440, 440 -45]      
                GY=[388, 438, 438, 438]
                GD=[0]*4        
                
                eaten_ghost = [0]*4
                G_DEAD= [0]*4
            else:
                game_over = 1
                moving = startup_counter = 0

    # active ghost hit pacman
    for i in range(4):
        if powerup_phase and player_circle.colliderect(GHOST[i].rect) and not GHOST[i].dead:
            if eaten_ghost[i]:  # ghost eat pacman , so game reset
                if lives > 0:
                    powerup_phase = False
                    power_counter = 0
                    lives -= 1
                    startup_counter = 0
                    player_x = 450
                    player_y = 663
                    player_dir = player_dir_command = 0
                                
                    GX=[440, 440+45, 440, 440 -45]      
                    GY=[388, 438, 438, 438]
                    GD=[0]*4
                    eaten_ghost = [0]*4
                    G_DEAD= [0]*4
                else:
                    game_over = True
                    moving = False
                    startup_counter = 0
            else: # pacman eat ghost
                G_DEAD[i] = eaten_ghost[i] = True
                score += (2 ** eaten_ghost.count(True)) * 100

    for e in event.get():
        run = (e.type != QUIT) 

        if e.type == KEYDOWN:
            player_dir_command={x:i for i,x in enumerate([K_RIGHT,K_LEFT,K_UP,K_DOWN])}.get(e.key, player_dir_command) # key defines player_dir

            if e.key == K_SPACE and (game_over or game_won):
                powerup_phase = False
                power_counter = 0
                lives -= 1
                startup_counter = 0
                player_x = 450
                player_y = 663
                player_dir = 0
                player_dir_command = 0

                GX=[440, 440+45, 440, 440 -45]      
                GY=[388, 438, 438, 438]
                GD=[0]*4
                
                eaten_ghost = [0]*4
                G_DEAD= [0]*4
                score = 0
                lives = 3
                game_over = game_won = False
                level = copy.deepcopy(boards)

        # player_dir : RLUD
        if e.type == KEYUP:
            if e.key == K_RIGHT and player_dir_command == 0: player_dir_command = player_dir
            if e.key == K_LEFT and player_dir_command == 1:  player_dir_command = player_dir
            if e.key == K_UP and player_dir_command == 2:    player_dir_command = player_dir
            if e.key == K_DOWN and player_dir_command == 3:  player_dir_command = player_dir

    for i in range(4):
        if player_dir_command == i and can_move[i]: player_dir = i

    if player_x > 900:      player_x = -50+3
    elif player_x < -50:    player_x = 900-3

    if GHOST[0].in_box and G_DEAD[0]:   G_DEAD[0] = False
    if GHOST[1].in_box and G_DEAD[1]:       G_DEAD[1] = False
    if GHOST[2].in_box and G_DEAD[2]:     G_DEAD[2] = False
    if GHOST[3].in_box and G_DEAD[3]:     G_DEAD[3] = False

    display.flip()

quit()

# sound effects, restart and winning messages