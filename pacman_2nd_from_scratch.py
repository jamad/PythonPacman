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

while QUIT not in (e.type for e in event.get()):# main loop continues until quit button
    timer.tick(FPS)
    screen.fill('black')
    
    # draw screen

    display.flip()

quit()




    
