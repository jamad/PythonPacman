from pygame import *
from zelda_style_game_settings import *
from zelda_style_game_tiles import * # rocks
from zelda_style_game_player import *
from zelda_style_game_debug import my_debug # for debug info

class Level:
    def __init__(self) -> None:

        #self.display_surface = display.get_surface() # get display surface

        #self.visible_sprites=sprite.Group()
        self.visible_sprites=YSortCameraGroup()

        self.col_sprites=sprite.Group()

        self.player=None # placeholder 
        self.create_map() # sprite setup below


    def create_map(self):
        for index_r,row in enumerate(WORLD_MAP):
            #print(index,row)
            for index_c,col in enumerate(row):
                y=index_r * TILESIZE
                x=index_c * TILESIZE
                if col=='x':
                    pos=(x,y)
                    Tile(pos, [self.visible_sprites,self.col_sprites])
                if col=='p':
                    pos=(x,y)
                    
                    self.player = Player(pos, [self.visible_sprites], self.col_sprites)
                
    def run(self):
        #self.visible_sprites.draw(self.display_surface) # draw all sprites in sprite group
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()

        my_debug(self.player.direction)#

class YSortCameraGroup(sprite.Group):
    def __init__(self):
        super().__init__()

        self.display_surface = display.get_surface() # get display surface
        
        #define camera offset here
        self.offset=math.Vector2()

    def custom_draw(self, player):
        
        half_w,half_h=(x//2 for x in self.display_surface.get_size())

        self.offset.x = -player.rect.centerx + half_w
        self.offset.y = -player.rect.centery + half_h

        for my_sprite in sorted( self.sprites(), key=lambda spr:spr.rect.centery):
            
            #myrect= (my_sprite.rect.x, my_sprite.rect.y + offset, my_sprite.rect.w, my_sprite.rect.h)
            myrect=my_sprite.rect.topleft + self.offset  # 2d vector addition

            self.display_surface.blit(my_sprite.image, myrect)
