# Build Pac-Man from Scratch in Python with PyGame!!
# done until 1:26:45

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
G0_img = transform.scale(image.load(f'assets/ghost_images/red.png'),img_size)
G2_img = transform.scale(image.load(f'assets/ghost_images/pink.png'),img_size)
G1_img = transform.scale(image.load(f'assets/ghost_images/blue.png'),img_size)
G3_img = transform.scale(image.load(f'assets/ghost_images/orange.png'),img_size)
spooked_img = transform.scale(image.load(f'assets/ghost_images/powerup.png'),img_size)
dead_img = transform.scale(image.load(f'assets/ghost_images/dead.png'),img_size)

player_x = 450 - 20 # centerize
player_y = 663
player_dir = player_dir_command = 0 #player_dir : RLUD   ::::   0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
can_move = [0]*4 # R, L, U, D  open flag for movement

# ghosts : blinky 0  inky 1  pinky 2 clyde 3           
G0_x = 440 
G1_x = 440 + 45
G2_x = 440
G3_x = 440 - 45
G0_y = 388
G1_y = G2_y = G3_y = 438
G0_player_dir = G1_player_dir = G2_player_dir = G3_player_dir = 0

counter = 0  
powerup_show = False

player_speed = 2
score = 0
powerup = False
power_counter = 0
eaten_ghost = [False, False, False, False]
targets = [(player_x, player_y), (player_x, player_y), (player_x, player_y), (player_x, player_y)]
G0_dead = G1_dead = G3_dead = G2_dead = False
G0_box = G1_box = G3_box = G2_box = False
moving = False
ghost_speeds = [2, 2, 2, 2]
startup_counter = 0
lives = 3
game_over = game_won = False

class Ghost:
    def __init__(self, x_coord, y_coord, target, speed, img, direct, dead, box, id):
        self.x_pos = x_coord
        self.y_pos = y_coord
        self.center_x = self.x_pos + 22
        self.center_y = self.y_pos + 22
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
        if (not powerup and not self.dead) or (eaten_ghost[self.id] and powerup and not self.dead):            screen.blit(self.img, (self.x_pos, self.y_pos))
        elif powerup and not self.dead and not eaten_ghost[self.id]:            screen.blit(spooked_img, (self.x_pos, self.y_pos))
        else:            screen.blit(dead_img, (self.x_pos, self.y_pos))
        ghost_rect = rect.Rect((self.center_x - 18, self.center_y - 18), (36, 36))
        return ghost_rect

    def check_collisions(self):
        self.turns = [False, False, False, False]
        if 0 < self.center_x // 30 < 29:
            if level[(self.center_y - RADIUS) // COUNT_R][self.center_x // COUNT_C] == 9:                self.turns[2] = True
            if level[self.center_y // COUNT_R][(self.center_x - RADIUS) // COUNT_C] < 3 or (level[self.center_y // COUNT_R][(self.center_x - RADIUS) // COUNT_C] == 9 and (self.in_box or self.dead)):self.turns[1] = True
            if level[self.center_y // COUNT_R][(self.center_x + RADIUS) // COUNT_C] < 3 or (level[self.center_y // COUNT_R][(self.center_x + RADIUS) // COUNT_C] == 9 and (self.in_box or self.dead)):self.turns[0] = True
            if level[(self.center_y + RADIUS) // COUNT_R][self.center_x // COUNT_C] < 3 or (level[(self.center_y + RADIUS) // COUNT_R][self.center_x // COUNT_C] == 9 and (self.in_box or self.dead)):self.turns[3] = True
            if level[(self.center_y - RADIUS) // COUNT_R][self.center_x // COUNT_C] < 3 or (level[(self.center_y - RADIUS) // COUNT_R][self.center_x // COUNT_C] == 9 and (self.in_box or self.dead)):self.turns[2] = True

            if self.dir == 2 or self.dir == 3:
                if 12 <= self.center_x % COUNT_C <= 18:
                    if level[(self.center_y + RADIUS) // COUNT_R][self.center_x // COUNT_C] < 3 or (level[(self.center_y + RADIUS) // COUNT_R][self.center_x // COUNT_C] == 9 and (self.in_box or self.dead)):self.turns[3] = True
                    if level[(self.center_y - RADIUS) // COUNT_R][self.center_x // COUNT_C] < 3 or (level[(self.center_y - RADIUS) // COUNT_R][self.center_x // COUNT_C] == 9 and (self.in_box or self.dead)):self.turns[2] = True
                if 12 <= self.center_y % COUNT_R <= 18:
                    if level[self.center_y // COUNT_R][(self.center_x - COUNT_C) // COUNT_C] < 3 or (level[self.center_y // COUNT_R][(self.center_x - COUNT_C) // COUNT_C] == 9 and (self.in_box or self.dead)):self.turns[1] = True
                    if level[self.center_y // COUNT_R][(self.center_x + COUNT_C) // COUNT_C] < 3 or (level[self.center_y // COUNT_R][(self.center_x + COUNT_C) // COUNT_C] == 9 and (self.in_box or self.dead)):self.turns[0] = True

            if self.dir == 0 or self.dir == 1:
                if 12 <= self.center_x % COUNT_C <= 18:
                    if level[(self.center_y + RADIUS) // COUNT_R][self.center_x // COUNT_C] < 3 or (level[(self.center_y + RADIUS) // COUNT_R][self.center_x // COUNT_C] == 9 and (self.in_box or self.dead)):self.turns[3] = True
                    if level[(self.center_y - RADIUS) // COUNT_R][self.center_x // COUNT_C] < 3 or (level[(self.center_y - RADIUS) // COUNT_R][self.center_x // COUNT_C] == 9 and (self.in_box or self.dead)):self.turns[2] = True
                if 12 <= self.center_y % COUNT_R <= 18:
                    if level[self.center_y // COUNT_R][(self.center_x - RADIUS) // COUNT_C] < 3 or (level[self.center_y // COUNT_R][(self.center_x - RADIUS) // COUNT_C] == 9 and (self.in_box or self.dead)):self.turns[1] = True
                    if level[self.center_y // COUNT_R][(self.center_x + RADIUS) // COUNT_C] < 3 or (level[self.center_y // COUNT_R][(self.center_x + RADIUS) // COUNT_C] == 9 and (self.in_box or self.dead)):self.turns[0] = True
        else: self.turns[0] = self.turns[1] = 1
        self.in_box = (350 < self.x_pos < 550 and 370 < self.y_pos < 480)
        return self.turns, self.in_box

    def move_G3(self): # G3 is going to turn whenever advantageous for pursuit
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
                else:
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
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
                else:self.y_pos += self.speed
        self.x_pos = (self.x_pos < -30 and 900) or ( self.x_pos > 900 and self.x_pos - 30) or self.x_pos            
        return self.x_pos, self.y_pos, self.dir

    def move_G0(self):   # G0 is going to turn whenever colliding with walls, otherwise continue straight
        if self.dir == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
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
                self.x_pos += self.speed
        elif self.dir == 1:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
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
                self.x_pos -= self.speed
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
                elif self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
                elif self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
            elif self.turns[3]:
                self.y_pos += self.speed
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos - 30
        return self.x_pos, self.y_pos, self.dir

    def move_G1(self):# G1 turns up or down at any point to pursue, but left and right only on collision
        if self.dir == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
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
                else:
                    self.x_pos += self.speed
        elif self.dir == 1:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.dir = 3
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
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
                else:
                    self.x_pos -= self.speed
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
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos - 30
        return self.x_pos, self.y_pos, self.dir

    def move_G2(self):# G2 is going to turn left or right whenever advantageous, but only up or down on collision
        if self.dir == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
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
                self.x_pos += self.speed
        elif self.dir == 1:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.dir = 3
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
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
                self.x_pos -= self.speed
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
                else:
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
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.dir = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.dir = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos += self.speed
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos - 30
        return self.x_pos, self.y_pos, self.dir

def draw_misc():
    score_text = font.render(f'Score: {score}', True, 'white')
    screen.blit(score_text, (10, 920))
    
    if powerup:        draw.circle(screen, 'blue', (140, 930), 15)

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
        if level[idx1][idx2] == 1:
            level[idx1][idx2] = 0
            scor += 10
        if level[idx1][idx2] == 2:
            level[idx1][idx2] = 0
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
            if cell == 2 and powerup_show:draw.circle(   screen, 'white', (COUNT_C*jc, COUNT_R*ic), 10)
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
    if powerup:
        if not G0.dead and not eaten_ghost[0]:            blink_target = (runaway_x, runaway_y)
        elif not G0.dead and eaten_ghost[0]:
            if 340 < blink_x < 560 and 340 < blink_y < 500:                blink_target = (400, 100)
            else:                blink_target = (player_x, player_y)
        else:            blink_target = return_target
        if not G1.dead and not eaten_ghost[1]:            ink_target = (runaway_x, player_y)
        elif not G1.dead and eaten_ghost[1]:
            if 340 < ink_x < 560 and 340 < ink_y < 500:                ink_target = (400, 100)
            else:                ink_target = (player_x, player_y)
        else:            ink_target = return_target
        if not G2.dead:            pink_target = (player_x, runaway_y)
        elif not G2.dead and eaten_ghost[2]:
            if 340 < pink_x < 560 and 340 < pink_y < 500:                pink_target = (400, 100)
            else:                pink_target = (player_x, player_y)
        else:            pink_target = return_target
        if not G3.dead and not eaten_ghost[3]:            clyd_target = (450, 450)
        elif not G3.dead and eaten_ghost[3]:
            if 340 < clyd_x < 560 and 340 < clyd_y < 500:                clyd_target = (400, 100)
            else:                clyd_target = (player_x, player_y)
        else:            clyd_target = return_target
    else:
        if not G0.dead:
            if 340 < blink_x < 560 and 340 < blink_y < 500:                blink_target = (400, 100)
            else:                blink_target = (player_x, player_y)
        else:            blink_target = return_target
        if not G1.dead:
            if 340 < ink_x < 560 and 340 < ink_y < 500:                ink_target = (400, 100)
            else:                ink_target = (player_x, player_y)
        else:            ink_target = return_target
        if not G2.dead:
            if 340 < pink_x < 560 and 340 < pink_y < 500:                pink_target = (400, 100)
            else:                pink_target = (player_x, player_y)
        else:            pink_target = return_target
        if not G3.dead:
            if 340 < clyd_x < 560 and 340 < clyd_y < 500:                clyd_target = (400, 100)
            else:                clyd_target = (player_x, player_y)
        else:            clyd_target = return_target
    return [blink_target, ink_target, pink_target, clyd_target]

run = True
while run:
    
    timer.tick(fps)

    counter += 1
    counter %= 20
    
    powerup_show = (7 < counter)

    if powerup and power_counter < 600:
        power_counter += 1
    elif powerup and power_counter >= 600:
        power_counter = 0
        powerup = False
        eaten_ghost = [False, False, False, False]
    if startup_counter < 180 and not game_over and not game_won:
        moving = False
        startup_counter += 1
    else:
        moving = True

    screen.fill('black')
    
    draw_board()

    center_x = player_x + 23 # due to 45 pixel image
    center_y = player_y + 23 # due to 45 pixel image

    ghost_speeds = [ powerup and 1 or 2]*4
    for i in range(4):
        if eaten_ghost[i]:ghost_speeds[i] = 2
        
    if G0_dead:        ghost_speeds[0] = 4
    if G1_dead:        ghost_speeds[1] = 4
    if G2_dead:        ghost_speeds[2] = 4
    if G3_dead:        ghost_speeds[3] = 4

    game_won = True
    for i in range(len(level)):
        if 1 in level[i] or 2 in level[i]:game_won = False

    player_circle = draw.circle(screen, 'black', (center_x, center_y), 20, 2)

    draw_player()
    
    G0  = Ghost(G0_x, G0_y, targets[0], ghost_speeds[0], G0_img, G0_player_dir, G0_dead,G0_box, 0)
    G1    = Ghost(G1_x, G1_y, targets[1], ghost_speeds[1], G1_img, G1_player_dir, G1_dead,G1_box, 1)
    G2   = Ghost(G2_x, G2_y, targets[2], ghost_speeds[2], G2_img, G2_player_dir, G2_dead,G2_box, 2)
    G3   = Ghost(G3_x, G3_y, targets[3], ghost_speeds[3], G3_img, G3_player_dir, G3_dead,G3_box, 3)
    draw_misc()
    targets = get_targets(G0_x, G0_y, G1_x, G1_y, G2_x, G2_y, G3_x, G3_y)

    can_move = check_passable(center_x, center_y)

    if moving:
        player_x, player_y = move_player(player_x, player_y)
        if not G0_dead and not G0.in_box:            G0_x, G0_y, G0_player_dir = G0.move_G0()
        else:            G0_x, G0_y, G0_player_dir = G0.move_G3()
        if not G2_dead and not G2.in_box:            G2_x, G2_y, G2_player_dir = G2.move_G2()
        else:            G2_x, G2_y, G2_player_dir = G2.move_G3()
        if not G1_dead and not G1.in_box:            G1_x, G1_y, G1_player_dir = G1.move_G1()
        else:            G1_x, G1_y, G1_player_dir = G1.move_G3()
        G3_x, G3_y, G3_player_dir = G3.move_G3()
    score, powerup, power_counter, eaten_ghost = check_collisions(score, powerup, power_counter, eaten_ghost)
    # add to if not powerup to check if eaten ghosts
    if not powerup:
        if any (player_circle.colliderect(x) and not y for x,y in ((G0.rect, G0.dead),(G1.rect, G1.dead),(G2.rect, G2.dead),(G3.rect, G3.dead)) ):
            if lives > 0:
                lives -= 1
                startup_counter = powerup = power_counter = 0
                
                player_x = 450
                player_y = 663
                
                player_dir = 0
                player_dir_command = 0
                
                G0_x = 440 
                G1_x = 440 + 45
                G2_x = 440
                G3_x = 440 - 45
                G0_y = 388
                G1_y = G2_y = G3_y = 438
                G0_player_dir = G1_player_dir = G2_player_dir = G3_player_dir = 0
                
                eaten_ghost = [0]*4
                G0_dead = G1_dead = G3_dead = G2_dead = 0
            else:
                game_over = 1
                moving = startup_counter = 0
    if powerup and player_circle.colliderect(G0.rect) and eaten_ghost[0] and not G0.dead:
        if lives > 0:
            powerup = False
            power_counter = 0
            lives -= 1
            startup_counter = 0
            player_x = 450
            player_y = 663
            player_dir = 0
            player_dir_command = 0
            
            G0_x = 440 
            G1_x = 440 + 45
            G2_x = 440
            G3_x = 440 - 45
            G0_y = 388
            G1_y = G2_y = G3_y = 438
            G0_player_dir = G1_player_dir = G2_player_dir = G3_player_dir = 0

            eaten_ghost = [0]*4
            G0_dead =G1_dead =G3_dead =G2_dead = False
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if powerup and player_circle.colliderect(G1.rect) and eaten_ghost[1] and not G1.dead:
        if lives > 0:
            powerup = False
            power_counter = 0
            lives -= 1
            startup_counter = 0
            player_x = 450
            player_y = 663
            player_dir = 0
            player_dir_command = 0
            
            G0_x = 440 
            G1_x = 440 + 45
            G2_x = 440
            G3_x = 440 - 45
            G0_y = 388
            G1_y = G2_y = G3_y = 438
            G0_player_dir = G1_player_dir = G2_player_dir = G3_player_dir = 0
            
            eaten_ghost = [False, False, False, False]
            G0_dead =G1_dead =G3_dead = G2_dead = False
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if powerup and player_circle.colliderect(G2.rect) and eaten_ghost[2] and not G2.dead:
        if lives > 0:
            powerup = False
            power_counter = 0
            lives -= 1
            startup_counter = 0
            player_x = 450
            player_y = 663
            player_dir = 0
            player_dir_command = 0

            G0_x = 440 
            G1_x = 440 + 45
            G2_x = 440
            G3_x = 440 - 45
            G0_y = 388
            G1_y = G2_y = G3_y = 438
            G0_player_dir = G1_player_dir = G2_player_dir = G3_player_dir = 0

            eaten_ghost = [False, False, False, False]
            G0_dead =G1_dead =G3_dead =G2_dead = False
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if powerup and player_circle.colliderect(G3.rect) and eaten_ghost[3] and not G3.dead:
        if lives > 0:
            powerup = False
            power_counter = 0
            lives -= 1
            startup_counter = 0
            player_x = 450
            player_y = 663
            player_dir = 0
            player_dir_command = 0
            
            G0_x = 440 
            G1_x = 440 + 45
            G2_x = 440
            G3_x = 440 - 45
            G0_y = 388
            G1_y = G2_y = G3_y = 438
            G0_player_dir = G1_player_dir = G2_player_dir = G3_player_dir = 0

            eaten_ghost = [False, False, False, False]
            G0_dead =G1_dead =G3_dead =G2_dead = False
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if powerup and player_circle.colliderect(G0.rect) and not G0.dead and not eaten_ghost[0]:
        G0_dead = True
        eaten_ghost[0] = True
        score += (2 ** eaten_ghost.count(True)) * 100
    if powerup and player_circle.colliderect(G1.rect) and not G1.dead and not eaten_ghost[1]:
        G1_dead = True
        eaten_ghost[1] = True
        score += (2 ** eaten_ghost.count(True)) * 100
    if powerup and player_circle.colliderect(G2.rect) and not G2.dead and not eaten_ghost[2]:
        G2_dead = True
        eaten_ghost[2] = True
        score += (2 ** eaten_ghost.count(True)) * 100
    if powerup and player_circle.colliderect(G3.rect) and not G3.dead and not eaten_ghost[3]:
        G3_dead = True
        eaten_ghost[3] = True
        score += (2 ** eaten_ghost.count(True)) * 100

    for e in event.get():
        run = (e.type != QUIT) 

        if e.type == KEYDOWN:
            player_dir_command={x:i for i,x in enumerate([K_RIGHT,K_LEFT,K_UP,K_DOWN])}.get(e.key, player_dir_command) # key defines player_dir

            if e.key == K_SPACE and (game_over or game_won):
                powerup = False
                power_counter = 0
                lives -= 1
                startup_counter = 0
                player_x = 450
                player_y = 663
                player_dir = 0
                player_dir_command = 0

                G0_x = 440 
                G1_x = 440 + 45
                G2_x = 440
                G3_x = 440 - 45
                G0_y = 388
                G1_y = G2_y = G3_y = 438
                G0_player_dir = G1_player_dir = G2_player_dir = G3_player_dir = 0
                
                eaten_ghost = [0]*4
                G0_dead =G1_dead =G3_dead =G2_dead = False
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

    if G0.in_box and G0_dead:   G0_dead = False
    if G1.in_box and G1_dead:       G1_dead = False
    if G2.in_box and G2_dead:     G2_dead = False
    if G3.in_box and G3_dead:     G3_dead = False

    display.flip()

quit()

# sound effects, restart and winning messages