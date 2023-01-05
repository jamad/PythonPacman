from pygame import *
from zelda_style_game_settings import *
from zelda_style_game_tiles import * # rocks


class Level:
    def __init__(self) -> None:

        self.display_surface = display.get_surface() # get display surface
        self.visible_sprites=sprite.Group()
        self.col_sprites=sprite.Group()

        self.create_map() # sprite setup below

    def create_map(self):
        for index_r,row in enumerate(WORLD_MAP):
            #print(index,row)
            for index_c,col in enumerate(row):
                y=index_r * TILESIZE
                x=index_c * TILESIZE
                if col=='x':
                    pos=(x,y)
                    Tile(pos, [self.visible_sprites])
                
                    

    def run(self):
        self.visible_sprites.draw(self.display_surface) # draw all sprites in sprite group
        
