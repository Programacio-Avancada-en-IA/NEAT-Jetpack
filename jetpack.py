import pygame
import sys
from math import floor, ceil

UPDATES_PER_SEC = 60
SIZE = WIDTH, HEIGHT = 1280, 720
SCREEN = None
BACKGROUND = None
FAROLES = None
GROUND = None
GROUND_C = None
CLOCK = pygame.time.Clock()

GROUND_HEIGHT = 100

GRAVITY = 1.0
FORCE = -1.75


class MovingImages:
    def __init__(self, speed, images, rects, offset=0):
        self.speed = speed
        self.images = images
        self.rects = rects
        for i, rect in enumerate(self.rects):
            rect.move_ip(i * (rect.width + offset), 0)
        self.offset = offset

    def update(self):
        for i, rect in enumerate(self.rects):
            self.rects[i].move_ip(-self.speed, 0)
            if rect.x + rect.width <= 0:
                self.rects[i] = pygame.Rect(max([rc.x + rc.width for rc in self.rects]) - 18 + self.offset, rect.y,
                                            rect.width, rect.height)
        SCREEN.blits([el for el in zip(self.images, self.rects)])

class AnimatedSprite:
    def __init__(self, images, speed):
        self.images = images
        self.speed = speed
        self.frame_counter = 0
        self.image_index = 0

    def update(self):
        self.frame_counter += 1
        if self.frame_counter % self.speed == 0:
            self.frame_counter = 0
            self.image_index = (self.image_index + 1) % len(self.images)

    def draw(self, rect):
        SCREEN.blit(self.images[self.image_index], rect)


def init_game():
    global SCREEN, BACKGROUND, GROUND, FAROLES, GROUND_C
    pygame.init()

    SCREEN = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("NEAT Jetpack")

    bg_image = pygame.image.load("assets/background.png").convert_alpha()
    BACKGROUND_IMAGES = [pygame.transform.scale(bg_image, (WIDTH, HEIGHT))] * (ceil(WIDTH/bg_image.get_rect().width)
                                                                               + 1)
    gr_image = pygame.image.load("assets/ground.png").convert_alpha()
    GROUND_IMAGES = [pygame.transform.scale(gr_image, (WIDTH, GROUND_HEIGHT))] * (ceil(WIDTH/gr_image.get_rect().width)
                                                                                  + 1)

    fa_image = pygame.image.load("assets/farola.png")
    fa_image.set_colorkey((255, 255, 255))
    fa_image = fa_image.convert_alpha()
    new_width = floor(fa_image.get_rect().width * 0.8)
    new_height = floor(fa_image.get_rect().height * 0.8)
    FA_IMAGES = [pygame.transform.scale(fa_image, (new_width, new_height))] * (ceil(WIDTH/fa_image.get_rect().width)
                                                                               + 1)

    BACKGROUND_RECTS = [img.get_rect() for img in BACKGROUND_IMAGES]
    GROUND_RECTS = [img.get_rect() for img in GROUND_IMAGES]
    FA_RECTS = [img.get_rect() for img in FA_IMAGES]

    for rect in GROUND_RECTS:
        rect.y = HEIGHT - GROUND_HEIGHT

    for rect in FA_RECTS:
        rect.y = HEIGHT - GROUND_HEIGHT - rect.height

    BACKGROUND = MovingImages(3, BACKGROUND_IMAGES, BACKGROUND_RECTS)
    GROUND = MovingImages(8, GROUND_IMAGES, GROUND_RECTS)
    FAROLES = MovingImages(3, FA_IMAGES, FA_RECTS, offset=200)
    GROUND_C = pygame.Rect(0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT)


class Player:
    rectangle = pygame.Rect(200, 0, 48, 96)

    air_sprite = None
    prop_sprite = None
    running_sp = None
    # 0: running
    # 1: falling
    # 2: propulsing
    state = 0

    acceleration = GRAVITY

    def __init__(self):
        self.air_sprite = pygame.image.load("assets/on_air.png").convert_alpha()
        self.prop_sprite = pygame.image.load("assets/prop.png").convert_alpha()
        self.running_sp = AnimatedSprite(
            [pygame.image.load("assets/running/"+ str(i) + ".png").convert_alpha()
            for i in range(1,9)],3)

    def draw(self):
        if self.state == 0:
            self.running_sp.update()
            self.running_sp.draw(self.rectangle)
        elif self.state == 1:
            SCREEN.blit(self.air_sprite, self.rectangle)
        elif self.state == 2:
            SCREEN.blit(self.prop_sprite, self.rectangle)


    def affected_by_acceleration(self):
        # Crear rectangle copia
        # Moure copia
        rect_copy = self.rectangle.move(0, floor(self.acceleration))
        # Mirar si colisione
        if rect_copy.colliderect(GROUND_C):
            # Si colisione, moure al jugador sol lo suficient, per no enfonsarse
            vert_dist = GROUND_C.y - (self.rectangle.y + self.rectangle.height)
            self.rectangle.move_ip(0, vert_dist)
            self.acceleration = 0
        elif rect_copy.y <= 0:
            vert_dist = -self.rectangle.y
            self.rectangle.move_ip(0, vert_dist)
            self.acceleration = GRAVITY
        else:
            self.rectangle.move_ip(0, floor(self.acceleration))
            self.acceleration += GRAVITY

    def logic(self):
        self.affected_by_acceleration()
        if self.acceleration == 0:
            # Running on the ground
            self.state = 0
        elif not pygame.mouse.get_pressed()[0] and not self.state == 0:
            # Player not running and not propulsing
            self.state = 1

    def process_input(self):
        if pygame.mouse.get_pressed()[0]:
            player.acceleration += FORCE
            self.state = 2


def draw_background():
    BG_COLOR = (0, 191, 255)
    BACKGROUND.update()
    FAROLES.update()


def draw_ground():
    G_COLOR = (105, 105, 105)
    GROUND.update()


def draw_objects(objects):
    for obj in objects:
        obj.draw()


def object_logic(objects):
    for obj in objects:
        obj.logic()


if __name__ in "__main__":
    init_game()
    fps = []
    player = Player()
    objects = []
    RUNNING = True
    while RUNNING:
        CLOCK.tick(UPDATES_PER_SEC)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # print(sum(fps)/len(fps))
                RUNNING = False
        draw_background()
        player.process_input()
        object_logic(objects + [player])
        draw_objects(objects)
        player.draw()
        draw_ground()
        #fps.append(CLOCK.get_fps())
        pygame.display.flip()
    sys.exit()

# TODO: Dibuixar sprites del fondo i del terra (Galajat)
# TODO: Dibuixar sprites del personatge i objectes (Galajat)
# TODO: Fer el desplaçament del fondo (Galajat)
# TODO: Començar a mirar tema NEAT (Joe)
