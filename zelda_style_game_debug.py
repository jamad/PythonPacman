from pygame import *

init()

myfont=font.Font(None,30)

def my_debug(info, y=10, x=10):
    display_surface=display.get_surface()
    debug_surf=myfont.render(str(info), True,'white')
    debug_rect=debug_surf.get_rect(topleft=(x,y))
    draw.rect(display_surface, 'black',debug_rect)
    display_surface.blit(debug_surf, debug_rect)

