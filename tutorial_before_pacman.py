# https://w3cschoool.com/tutorial/pygame-tutorial

from pygame import init,sprite,Surface,time,display,K_LEFT, K_RIGHT, K_UP, K_DOWN, event,QUIT,key
import sys


class Sprite(sprite.Sprite):
    def __init__(self, pos):
        sprite.Sprite.__init__(self)
        self.image = Surface([20, 20])
        self.image.fill((255, 0, 255))
        self.rect = self.image.get_rect()
        self.rect.center = pos

def main():
    init()
    clock = time.Clock()
    fps = 50
    bg = [0, 0, 0]
    size =[300, 300]
    screen = display.set_mode(size)
    player = Sprite([40, 50])
    # Define keys for player movement
    player.move = [K_LEFT, K_RIGHT, K_UP, K_DOWN]
    player.vx = 5
    player.vy = 5

    wall = Sprite([100, 60])

    wall_group = sprite.Group()
    wall_group.add(wall)

    player_group = sprite.Group()
    player_group.add(player)

    while True:
        for e in event.get():
            if e.type == QUIT:
                return False
        k = key.get_pressed()
        for i in range(2):
            if k[player.move[i]]:
                player.rect.x += player.vx * [-1, 1][i]

        for i in range(2):
            if k[player.move[2:4][i]]:
                player.rect.y += player.vy * [-1, 1][i]
        screen.fill(bg)
        # first parameter takes a single sprite
        # second parameter takes sprite groups
        # third parameter is a kill command if true
        hit = sprite.spritecollide(player, wall_group, True)
        if hit:
        # if collision is detected call a function to destroy
            # rect
            player.image.fill((255, 255, 255))
        player_group.draw(screen)
        wall_group.draw(screen)
        display.update()
        clock.tick(fps)
    quit()
    sys.exit

if __name__ == '__main__':main()