# Build Pac-Man from Scratch in Python with PyGame!!
import copy
from board import boards

#import pygame
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

img_size=(45, 45)
player_images = [transform.scale(image.load(f'assets/player_images/{i}.png'),img_size) for i in (1,2,3,2)]# 4 images
blinky_img = transform.scale(image.load(f'assets/ghost_images/red.png'),img_size)
pinky_img = transform.scale(image.load(f'assets/ghost_images/pink.png'),img_size)
inky_img = transform.scale(image.load(f'assets/ghost_images/blue.png'),img_size)
clyde_img = transform.scale(image.load(f'assets/ghost_images/orange.png'),img_size)
spooked_img = transform.scale(image.load(f'assets/ghost_images/powerup.png'),img_size)
dead_img = transform.scale(image.load(f'assets/ghost_images/dead.png'),img_size)

player_x = 450 - 20
player_y = 663
direction = direction_command = 0 #direction : RLUD
turns_allowed = [0]*4 # R, L, U, D  open flag for movement

blinky_x = 56
blinky_y = 58
blinky_direction = 0

inky_x = 440
inky_y = 388
inky_direction = 2

pinky_x = 440
pinky_y = 438
pinky_direction = 2

clyde_x = 440
clyde_y = 438
clyde_direction = 2

counter = 0  # what it is for?
powerup_show = False



player_speed = 2
score = 0
powerup = False
power_counter = 0
eaten_ghost = [False, False, False, False]
targets = [(player_x, player_y), (player_x, player_y), (player_x, player_y), (player_x, player_y)]
blinky_dead = False
inky_dead = False
clyde_dead = False
pinky_dead = False
blinky_box = False
inky_box = False
clyde_box = False
pinky_box = False
moving = False
ghost_speeds = [2, 2, 2, 2]
startup_counter = 0
lives = 3
game_over = False
game_won = False

class Ghost:
    def __init__(self, x_coord, y_coord, target, speed, img, direct, dead, box, id):
        self.x_pos = x_coord
        self.y_pos = y_coord
        self.center_x = self.x_pos + 22
        self.center_y = self.y_pos + 22
        self.target = target
        self.speed = speed
        self.img = img
        self.direction = direct
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
        # R, L, U, D
        
        RADIUS = 15  # what's this? 
        self.turns = [False, False, False, False]
        if 0 < self.center_x // 30 < 29:
            if level[(self.center_y - RADIUS) // COUNT_R][self.center_x // COUNT_C] == 9:                self.turns[2] = True
            if level[self.center_y // COUNT_R][(self.center_x - RADIUS) // COUNT_C] < 3 or (level[self.center_y // COUNT_R][(self.center_x - RADIUS) // COUNT_C] == 9 and (self.in_box or self.dead)):self.turns[1] = True
            if level[self.center_y // COUNT_R][(self.center_x + RADIUS) // COUNT_C] < 3 or (level[self.center_y // COUNT_R][(self.center_x + RADIUS) // COUNT_C] == 9 and (self.in_box or self.dead)):self.turns[0] = True
            if level[(self.center_y + RADIUS) // COUNT_R][self.center_x // COUNT_C] < 3 or (level[(self.center_y + RADIUS) // COUNT_R][self.center_x // COUNT_C] == 9 and (self.in_box or self.dead)):self.turns[3] = True
            if level[(self.center_y - RADIUS) // COUNT_R][self.center_x // COUNT_C] < 3 or (level[(self.center_y - RADIUS) // COUNT_R][self.center_x // COUNT_C] == 9 and (self.in_box or self.dead)):self.turns[2] = True

            if self.direction == 2 or self.direction == 3:
                if 12 <= self.center_x % COUNT_C <= 18:
                    if level[(self.center_y + RADIUS) // COUNT_R][self.center_x // COUNT_C] < 3 or (level[(self.center_y + RADIUS) // COUNT_R][self.center_x // COUNT_C] == 9 and (self.in_box or self.dead)):self.turns[3] = True
                    if level[(self.center_y - RADIUS) // COUNT_R][self.center_x // COUNT_C] < 3 or (level[(self.center_y - RADIUS) // COUNT_R][self.center_x // COUNT_C] == 9 and (self.in_box or self.dead)):self.turns[2] = True
                if 12 <= self.center_y % COUNT_R <= 18:
                    if level[self.center_y // COUNT_R][(self.center_x - COUNT_C) // COUNT_C] < 3 or (level[self.center_y // COUNT_R][(self.center_x - COUNT_C) // COUNT_C] == 9 and (self.in_box or self.dead)):self.turns[1] = True
                    if level[self.center_y // COUNT_R][(self.center_x + COUNT_C) // COUNT_C] < 3 or (level[self.center_y // COUNT_R][(self.center_x + COUNT_C) // COUNT_C] == 9 and (self.in_box or self.dead)):self.turns[0] = True

            if self.direction == 0 or self.direction == 1:
                if 12 <= self.center_x % COUNT_C <= 18:
                    if level[(self.center_y + RADIUS) // COUNT_R][self.center_x // COUNT_C] < 3 or (level[(self.center_y + RADIUS) // COUNT_R][self.center_x // COUNT_C] == 9 and (self.in_box or self.dead)):self.turns[3] = True
                    if level[(self.center_y - RADIUS) // COUNT_R][self.center_x // COUNT_C] < 3 or (level[(self.center_y - RADIUS) // COUNT_R][self.center_x // COUNT_C] == 9 and (self.in_box or self.dead)):self.turns[2] = True
                if 12 <= self.center_y % COUNT_R <= 18:
                    if level[self.center_y // COUNT_R][(self.center_x - RADIUS) // COUNT_C] < 3 or (level[self.center_y // COUNT_R][(self.center_x - RADIUS) // COUNT_C] == 9 and (self.in_box or self.dead)):self.turns[1] = True
                    if level[self.center_y // COUNT_R][(self.center_x + RADIUS) // COUNT_C] < 3 or (level[self.center_y // COUNT_R][(self.center_x + RADIUS) // COUNT_C] == 9 and (self.in_box or self.dead)):self.turns[0] = True
        else: self.turns[0] = self.turns[1] = 1
        self.in_box = (350 < self.x_pos < 550 and 370 < self.y_pos < 480)
        return self.turns, self.in_box

    def move_clyde(self):
        # r, l, u, d
        # clyde is going to turn whenever advantageous for pursuit
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:                    self.x_pos += self.speed
        elif self.direction == 1:
            if self.target[1] > self.y_pos and self.turns[3]:                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:                    self.x_pos -= self.speed
        elif self.direction == 2:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.direction = 1
                self.x_pos -= self.speed
            elif self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:self.y_pos += self.speed
        self.x_pos = (self.x_pos < -30 and 900) or ( self.x_pos > 900 and self.x_pos - 30) or self.x_pos            
        return self.x_pos, self.y_pos, self.direction

    def move_blinky(self):
        # r, l, u, d
        # blinky is going to turn whenever colliding with walls, otherwise continue straight
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                self.x_pos += self.speed
        elif self.direction == 1:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                self.x_pos -= self.speed
        elif self.direction == 2:
            if self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[2]:
                self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[3]:
                self.y_pos += self.speed
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos - 30
        return self.x_pos, self.y_pos, self.direction

    def move_inky(self):
        # r, l, u, d
        # inky turns up or down at any point to pursue, but left and right only on collision
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos += self.speed
        elif self.direction == 1:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos -= self.speed
        elif self.direction == 2:
            if self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]:
                self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                self.y_pos += self.speed
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos - 30
        return self.x_pos, self.y_pos, self.direction

    def move_pinky(self):
        # r, l, u, d
        # inky is going to turn left or right whenever advantageous, but only up or down on collision
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                self.x_pos += self.speed
        elif self.direction == 1:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                self.x_pos -= self.speed
        elif self.direction == 2:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.direction = 1
                self.x_pos -= self.speed
            elif self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos += self.speed
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos - 30
        return self.x_pos, self.y_pos, self.direction

def draw_misc():
    score_text = font.render(f'Score: {score}', True, 'white')
    screen.blit(score_text, (10, 920))
    
    if powerup:        draw.circle(screen, 'blue', (140, 930), 15)

    for i in range(lives):        screen.blit(transform.scale(player_images[0], (30, 30)), (650 + i * 40, 915))
    
    if game_over:
        draw.rect(screen, 'white', [50, 200, 800, 300],0, 10)
        draw.rect(screen, 'dark gray', [70, 220, 760, 260], 0, 10)
        gameover_text = font.render('Game over! Space bar to restart!', True, 'red')
        screen.blit(gameover_text, (100, 300))
    
    if game_won:
        draw.rect(screen, 'white', [50, 200, 800, 300],0, 10)
        draw.rect(screen, 'dark gray', [70, 220, 760, 260], 0, 10)
        gameover_text = font.render('Victory! Space bar to restart!', True, 'green')
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
    # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
    pos=(player_x, player_y)
    img_player=player_images[counter // 5]
    if direction == 0:        screen.blit(img_player, pos)
    elif direction == 1:        screen.blit(transform.flip(img_player, True, False), pos)
    elif direction == 2:        screen.blit(transform.rotate(img_player, 90), pos)
    elif direction == 3:        screen.blit(transform.rotate(img_player, -90), pos)


# check collisions based on center x and center y of player +/- RADIUS number
def check_passable(col, row):  # originally check_position
    if 29 <= col // 30 : return [1,1,0,0] # only horizontal warp is passable

    cell_R=level[row // COUNT_R][(col + RADIUS) // COUNT_C]
    cell_L=level[row // COUNT_R][(col - RADIUS) // COUNT_C]
    cell_U=level[(row - RADIUS) // COUNT_R][col // COUNT_C]
    cell_D=level[(row + RADIUS) // COUNT_R][col // COUNT_C]
    dir_H= direction in(0,1)
    dir_V= direction in(2,3)

    tR = (direction in(0,1)and cell_R < 3) or ( dir_V and( 12 <= row % COUNT_R <= 18)and(level[row // COUNT_R][col // COUNT_C + 1] < 3)) 
    tL = (direction in(0,1)and cell_L < 3) or ( dir_V and( 12 <= row % COUNT_R <= 18)and(level[row // COUNT_R][col // COUNT_C - 1] < 3))     
    tU = (direction in(2,3)and cell_U < 3) or ( dir_H and( 12 <= col % COUNT_C <= 18)and(level[row // COUNT_R - 1][col // COUNT_C] < 3)) 
    tD = (direction in(2,3)and cell_D < 3) or ( dir_H and( 12 <= col % COUNT_C <= 18)and(level[row // COUNT_R + 1][col // COUNT_C] < 3)) 

    return [tR,tL,tU,tD]

def move_player(play_x, play_y):
    # r, l, u, d
    if turns_allowed[direction]:
        if direction == 0:        play_x += player_speed
        elif direction == 1 :        play_x -= player_speed
        elif direction == 2 :        play_y -= player_speed
        elif direction == 3 :        play_y += player_speed
    return play_x, play_y

def get_targets(blink_x, blink_y, ink_x, ink_y, pink_x, pink_y, clyd_x, clyd_y):
    if player_x < 450:        runaway_x = 900
    else:        runaway_x = 0
    if player_y < 450:        runaway_y = 900
    else:        runaway_y = 0
    return_target = (380, 400)
    if powerup:
        if not blinky.dead and not eaten_ghost[0]:            blink_target = (runaway_x, runaway_y)
        elif not blinky.dead and eaten_ghost[0]:
            if 340 < blink_x < 560 and 340 < blink_y < 500:                blink_target = (400, 100)
            else:                blink_target = (player_x, player_y)
        else:            blink_target = return_target
        if not inky.dead and not eaten_ghost[1]:            ink_target = (runaway_x, player_y)
        elif not inky.dead and eaten_ghost[1]:
            if 340 < ink_x < 560 and 340 < ink_y < 500:                ink_target = (400, 100)
            else:                ink_target = (player_x, player_y)
        else:            ink_target = return_target
        if not pinky.dead:            pink_target = (player_x, runaway_y)
        elif not pinky.dead and eaten_ghost[2]:
            if 340 < pink_x < 560 and 340 < pink_y < 500:                pink_target = (400, 100)
            else:                pink_target = (player_x, player_y)
        else:            pink_target = return_target
        if not clyde.dead and not eaten_ghost[3]:            clyd_target = (450, 450)
        elif not clyde.dead and eaten_ghost[3]:
            if 340 < clyd_x < 560 and 340 < clyd_y < 500:                clyd_target = (400, 100)
            else:                clyd_target = (player_x, player_y)
        else:            clyd_target = return_target
    else:
        if not blinky.dead:
            if 340 < blink_x < 560 and 340 < blink_y < 500:                blink_target = (400, 100)
            else:                blink_target = (player_x, player_y)
        else:            blink_target = return_target
        if not inky.dead:
            if 340 < ink_x < 560 and 340 < ink_y < 500:                ink_target = (400, 100)
            else:                ink_target = (player_x, player_y)
        else:            ink_target = return_target
        if not pinky.dead:
            if 340 < pink_x < 560 and 340 < pink_y < 500:                pink_target = (400, 100)
            else:                pink_target = (player_x, player_y)
        else:            pink_target = return_target
        if not clyde.dead:
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
    if eaten_ghost[0]:        ghost_speeds[0] = 2
    if eaten_ghost[1]:        ghost_speeds[1] = 2
    if eaten_ghost[2]:        ghost_speeds[2] = 2
    if eaten_ghost[3]:        ghost_speeds[3] = 2
    if blinky_dead:        ghost_speeds[0] = 4
    if inky_dead:        ghost_speeds[1] = 4
    if pinky_dead:        ghost_speeds[2] = 4
    if clyde_dead:        ghost_speeds[3] = 4

    game_won = True
    for i in range(len(level)):
        if 1 in level[i] or 2 in level[i]:game_won = False

    player_circle = draw.circle(screen, 'black', (center_x, center_y), 20, 2)

    draw_player()
    
    blinky = Ghost(blinky_x, blinky_y, targets[0], ghost_speeds[0], blinky_img, blinky_direction, blinky_dead,blinky_box, 0)
    inky = Ghost(inky_x, inky_y, targets[1], ghost_speeds[1], inky_img, inky_direction, inky_dead,inky_box, 1)
    pinky = Ghost(pinky_x, pinky_y, targets[2], ghost_speeds[2], pinky_img, pinky_direction, pinky_dead,pinky_box, 2)
    clyde = Ghost(clyde_x, clyde_y, targets[3], ghost_speeds[3], clyde_img, clyde_direction, clyde_dead,clyde_box, 3)
    draw_misc()
    targets = get_targets(blinky_x, blinky_y, inky_x, inky_y, pinky_x, pinky_y, clyde_x, clyde_y)

    turns_allowed = check_passable(center_x, center_y)
    if moving:
        player_x, player_y = move_player(player_x, player_y)
        if not blinky_dead and not blinky.in_box:            blinky_x, blinky_y, blinky_direction = blinky.move_blinky()
        else:            blinky_x, blinky_y, blinky_direction = blinky.move_clyde()
        if not pinky_dead and not pinky.in_box:            pinky_x, pinky_y, pinky_direction = pinky.move_pinky()
        else:            pinky_x, pinky_y, pinky_direction = pinky.move_clyde()
        if not inky_dead and not inky.in_box:            inky_x, inky_y, inky_direction = inky.move_inky()
        else:            inky_x, inky_y, inky_direction = inky.move_clyde()
        clyde_x, clyde_y, clyde_direction = clyde.move_clyde()
    score, powerup, power_counter, eaten_ghost = check_collisions(score, powerup, power_counter, eaten_ghost)
    # add to if not powerup to check if eaten ghosts
    if not powerup:
        if any (player_circle.colliderect(x) and not y for x,y in ((blinky.rect, blinky.dead),(inky.rect, inky.dead),(pinky.rect, pinky.dead),(clyde.rect, clyde.dead)) ):
            if lives > 0:
                lives -= 1
                startup_counter = powerup = power_counter = 0
                
                player_x = 450
                player_y = 663
                
                direction = 0
                direction_command = 0
                
                blinky_x = 56
                blinky_y = 58
                blinky_direction = 0
                
                inky_x = pinky_x = clyde_x = 440
                inky_direction = pinky_direction = clyde_direction = 2
                
                inky_y = 388
                pinky_y = 438
                clyde_y = 438
                
                eaten_ghost = [0]*4
                blinky_dead = inky_dead = clyde_dead = pinky_dead = 0
            else:
                game_over = 1
                moving = startup_counter = 0
    if powerup and player_circle.colliderect(blinky.rect) and eaten_ghost[0] and not blinky.dead:
        if lives > 0:
            powerup = False
            power_counter = 0
            lives -= 1
            startup_counter = 0
            player_x = 450
            player_y = 663
            direction = 0
            direction_command = 0
            blinky_x = 56
            blinky_y = 58
            blinky_direction = 0
            inky_x = 440
            inky_y = 388
            inky_direction = 2
            pinky_x = 440
            pinky_y = 438
            pinky_direction = 2
            clyde_x = 440
            clyde_y = 438
            clyde_direction = 2
            eaten_ghost = [0]*4
            blinky_dead =inky_dead =clyde_dead =pinky_dead = False
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if powerup and player_circle.colliderect(inky.rect) and eaten_ghost[1] and not inky.dead:
        if lives > 0:
            powerup = False
            power_counter = 0
            lives -= 1
            startup_counter = 0
            player_x = 450
            player_y = 663
            direction = 0
            direction_command = 0
            blinky_x = 56
            blinky_y = 58
            blinky_direction = 0
            inky_x = 440
            inky_y = 388
            inky_direction = 2
            pinky_x = 440
            pinky_y = 438
            pinky_direction = 2
            clyde_x = 440
            clyde_y = 438
            clyde_direction = 2
            eaten_ghost = [False, False, False, False]
            blinky_dead = False
            inky_dead = False
            clyde_dead = False
            pinky_dead = False
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if powerup and player_circle.colliderect(pinky.rect) and eaten_ghost[2] and not pinky.dead:
        if lives > 0:
            powerup = False
            power_counter = 0
            lives -= 1
            startup_counter = 0
            player_x = 450
            player_y = 663
            direction = 0
            direction_command = 0
            blinky_x = 56
            blinky_y = 58
            blinky_direction = 0
            inky_x = 440
            inky_y = 388
            inky_direction = 2
            pinky_x = 440
            pinky_y = 438
            pinky_direction = 2
            clyde_x = 440
            clyde_y = 438
            clyde_direction = 2
            eaten_ghost = [False, False, False, False]
            blinky_dead = False
            inky_dead = False
            clyde_dead = False
            pinky_dead = False
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if powerup and player_circle.colliderect(clyde.rect) and eaten_ghost[3] and not clyde.dead:
        if lives > 0:
            powerup = False
            power_counter = 0
            lives -= 1
            startup_counter = 0
            player_x = 450
            player_y = 663
            direction = 0
            direction_command = 0
            blinky_x = 56
            blinky_y = 58
            blinky_direction = 0
            inky_x = 440
            inky_y = 388
            inky_direction = 2
            pinky_x = 440
            pinky_y = 438
            pinky_direction = 2
            clyde_x = 440
            clyde_y = 438
            clyde_direction = 2
            eaten_ghost = [False, False, False, False]
            blinky_dead = False
            inky_dead = False
            clyde_dead = False
            pinky_dead = False
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if powerup and player_circle.colliderect(blinky.rect) and not blinky.dead and not eaten_ghost[0]:
        blinky_dead = True
        eaten_ghost[0] = True
        score += (2 ** eaten_ghost.count(True)) * 100
    if powerup and player_circle.colliderect(inky.rect) and not inky.dead and not eaten_ghost[1]:
        inky_dead = True
        eaten_ghost[1] = True
        score += (2 ** eaten_ghost.count(True)) * 100
    if powerup and player_circle.colliderect(pinky.rect) and not pinky.dead and not eaten_ghost[2]:
        pinky_dead = True
        eaten_ghost[2] = True
        score += (2 ** eaten_ghost.count(True)) * 100
    if powerup and player_circle.colliderect(clyde.rect) and not clyde.dead and not eaten_ghost[3]:
        clyde_dead = True
        eaten_ghost[3] = True
        score += (2 ** eaten_ghost.count(True)) * 100

    for e in event.get():
        run = (e.type != QUIT) 

        if e.type == KEYDOWN:
            direction_command={x:i for i,x in enumerate([K_RIGHT,K_LEFT,K_UP,K_DOWN])}.get(e.key, direction_command) # key defines direction

            if e.key == K_SPACE and (game_over or game_won):
                powerup = False
                power_counter = 0
                lives -= 1
                startup_counter = 0
                player_x = 450
                player_y = 663
                direction = 0
                direction_command = 0
                blinky_x = 56
                blinky_y = 58
                blinky_direction = 0
                inky_x = 440
                inky_y = 388
                inky_direction = 2
                pinky_x = 440
                pinky_y = 438
                pinky_direction = 2
                clyde_x = 440
                clyde_y = 438
                clyde_direction = 2
                eaten_ghost = [False, False, False, False]
                blinky_dead = False
                inky_dead = False
                clyde_dead = False
                pinky_dead = False
                score = 0
                lives = 3
                level = copy.deepcopy(boards)
                game_over = False
                game_won = False

        # direction : RLUD
        if e.type == KEYUP:
            if e.key == K_RIGHT and direction_command == 0:                direction_command = direction
            if e.key == K_LEFT and direction_command == 1:                direction_command = direction
            if e.key == K_UP and direction_command == 2:                direction_command = direction
            if e.key == K_DOWN and direction_command == 3:                direction_command = direction

    if direction_command == 0 and turns_allowed[0]:        direction = 0
    if direction_command == 1 and turns_allowed[1]:        direction = 1
    if direction_command == 2 and turns_allowed[2]:        direction = 2
    if direction_command == 3 and turns_allowed[3]:        direction = 3

    if player_x > 900:        player_x = -47
    elif player_x < -50:        player_x = 897

    if blinky.in_box and blinky_dead:        blinky_dead = False
    if inky.in_box and inky_dead:        inky_dead = False
    if pinky.in_box and pinky_dead:        pinky_dead = False
    if clyde.in_box and clyde_dead:        clyde_dead = False

    display.flip()
quit()

# sound effects, restart and winning messages