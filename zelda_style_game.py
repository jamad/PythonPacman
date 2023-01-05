# https://www.youtube.com/watch?v=cwWi05Icpw0  

from pygame import *
from zelda_style_game_settings import *
from zelda_style_game_tiles import *
from zelda_style_game_player import *
from zelda_style_game_level import *
from zelda_style_game_debug import my_debug # for debug info

class Game:
    def __init__(self) -> None:
        init()
        self.screen=display.set_mode((WIDTH,HEIGHT))
        self.clock=time.Clock()
        display.set_caption('ZELDA') # challenge 1

        self.level=Level() # level creation

    def run(self):
        while 1:
            for ev in event.get():
                if ev.type==QUIT:
                    quit()
                    exit()

            self.screen.fill('black')

            self.level.run()

            my_debug('hello :) ')
            display.update()
            self.clock.tick(FPS)

game=Game()
game.run()
