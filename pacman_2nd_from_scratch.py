from pygame import *

init()

WIDTH=900
HEIGHT=950
GRID_W=0
GRID_H=0
FPS=60

screen=display.set_mode([WIDTH,HEIGHT])
timer=time.Clock()
myfont=font.Font('freesansbold.ttf',20)


def main_loop():
    for ev in event.get():
        if ev.type==QUIT:return 0
    return 1

while main_loop():
    timer.tick(FPS)
    screen.fill('black')
    
    # draw screen

    display.flip()

quit()




    
