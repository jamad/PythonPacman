
from pygame import *
from PIL import Image, ImageDraw

# --- constants ---
BLUE  = (  0,   0, 255)
RED   = (255,   0,   0)
GREY  = (128, 128, 128)

# - generate PIL image with transparent background -
size = 32
my_img = Image.new("RGBA", (size, size))
my_draw = ImageDraw.Draw(my_img)
my_rect = (0, 0, size-1, size-1)
my_draw.arc(my_rect, 0, 90, fill=RED)      #arc
my_draw.pieslice((0, 0, size-1, size-1), 320, 0, fill=GREY)#

# - convert into PyGame image -
data = my_img.tobytes()
my_img = image.fromstring(data, my_img.size, my_img.mode)

# --- main ----
init()
screen = display.set_mode((160,160))
image_rect = my_img.get_rect(center=screen.get_rect().center)# image rect to draw

# - mainloop -
clock = time.Clock()

running = True
while running:
    clock.tick(60)

    for e in event.get():
        if e.type == QUIT:running = False
        if e.type == KEYDOWN and e.key == K_ESCAPE:running = False

        if e.type==KEYDOWN and e.key==K_UP:image_rect.y-=1 #position change

    screen.fill(BLUE)
    screen.blit(my_img, image_rect) # <- display image
    display.flip()
# - end -
quit()