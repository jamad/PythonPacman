#screen.blit(transform.rotate(img_player, 90*player_dir), pos) # this logic needs RDLU instead of RLUD
from pygame import *
import copy
from math import pi, cos, sin

init()
FPS=120
HG =12 # half grid ( minimum : 4 ,  maximum  maybe 16)
G_SIZE=HG*2 # grid size is double of half grid
GRID_COUNT_X=30
GRID_COUNT_Y=33
HEIGHT_HUD_UPPER=HG*2
HEIGHT_HUD_LOWER=HG*2

### global variables
g_player_speed=HG/4 # speed can be float number (for example, 0.25)

g_player_dir=-4
g_player_wish_dir=-1

g_screen=display.set_mode([G_SIZE*60 ,HEIGHT_HUD_UPPER+GRID_COUNT_Y*G_SIZE+HEIGHT_HUD_LOWER])
g_clock=time.Clock() # originally variable timer 

ALL_FONTS=font.get_fonts()

def keyboard_control():
     global g_player_dir,g_player_wish_dir,g_mainloop# need mainloop to exit by ESC etc
     for e in event.get():
          if e.type==QUIT:
               g_mainloop=False # x button to close exe
          elif e.type==KEYDOWN:
               if e.key == K_ESCAPE:g_mainloop = False #Esc key
               else:g_player_wish_dir = DIR_DICT.get(e.key, g_player_dir)# change player direction

def debugdraw():
    for i,f in enumerate(ALL_FONTS):
        g_myfont=font.SysFont(f,G_SIZE//4*3)

        _mystr2=f'{i}/{len(ALL_FONTS)} {f.upper()}'
        _mytext2=g_myfont.render(_mystr2, 1, (255,255,0))             
        _myrect2=Rect(G_SIZE*(i//30)*10,    G_SIZE*(i%30),   G_SIZE*10  ,G_SIZE*10)
        g_screen.blit(_mytext2,_myrect2)

start_ticks=time.get_ticks()# game initial time to register
g_mainloop=True
while g_mainloop:# main loop continues until quit button

     # game time
     g_clock.tick(FPS)
     
     keyboard_control() # user key input handling

     ###################### draw screen
     g_screen.fill('black')

     if 1:debugdraw()# DEBUG DRAW
     
     display.flip()

quit()