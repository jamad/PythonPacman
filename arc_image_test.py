
from pygame import *
from PIL import Image, ImageDraw

# --- constants ---
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE  = (  0,   0, 255)
GREEN = (  0, 255,   0)
RED   = (255,   0,   0)
GREY  = (128, 128, 128)

# - generate PIL image with transparent background -
pil_size = 300
pil_image = Image.new("RGBA", (pil_size, pil_size))
pil_draw = ImageDraw.Draw(pil_image)
pil_draw.arc((0, 0, pil_size-1, pil_size-1), 0, 270, fill=RED)
pil_draw.pieslice((0, 0, pil_size-1, pil_size-1), 330, 0, fill=GREY)

# - convert into PyGame image -
mode = pil_image.mode
size = pil_image.size
data = pil_image.tobytes()
my_img = image.fromstring(data, size, mode)


# --- main ----
init()
screen = display.set_mode((320,320))
image_rect = my_img.get_rect(center=screen.get_rect().center)

# - mainloop -

clock = time.Clock()

running = True
while running:
    clock.tick(10)

    for e in event.get():
        if e.type == QUIT:running = False
        if e.type == KEYDOWN and e.key == K_ESCAPE:running = False

    screen.fill(BLACK)
    screen.blit(my_img, image_rect) # <- display image
    display.flip()
# - end -
quit()