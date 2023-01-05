from pygame import *
#from settings import *

WIDTH=1280
HEIGHT=720
FPS=60
TILESIZE=64

class Game:
    def __init__(self) -> None:
        init()
        self.screen=display.set_mode((WIDTH,HEIGHT))
        self.clock=time.Clock()


    def run(self):
        while 1:
            for ev in event.get():
                if ev.type==QUIT:
                    quit()
                    exit()

game=Game()
game.run()
