import pygame
import sys
from math import floor, ceil

UPDATES_PER_SEC = 60
SIZE = WIDTH, HEIGHT = 1280, 720
SCREEN = None
CLOCK = pygame.time.Clock()

GROUND_HEIGHT = 100

GRAVITY = 1.0
FORCE = -1.75

class MovingImages():
    def __init__(self, speed, images, rects):
        self.speed = speed
        self.images = images
        self.rects = rects
        for i, rect in enumerate(self.rects):
            rect.move_ip(i * rect.width, 0)

    def update(self):
        for i, rect in enumerate(self.rects):
            self.rects[i].move_ip(-self.speed, 0)
            if rect.x + rect.width <= 0:
                self.rects[i] = pygame.Rect(max([rc.x + rc.width for rc in self.rects]) - 18, rect.y, rect.width, rect.height)
        SCREEN.blits([el for el in zip(self.images, self.rects)])

BACKGROUND_IMAGES = [pygame.image.load("assets/grey.png")] * (ceil(WIDTH/300) + 1)
GROUND_IMAGES = [pygame.image.load("assets/gr.png")] * (ceil(WIDTH/300) + 1)

BACKGROUND_RECTS = [img.get_rect() for img in BACKGROUND_IMAGES]
GROUND_RECTS = [img.get_rect() for img in GROUND_IMAGES]

for rect in GROUND_RECTS:
    rect.y = HEIGHT - GROUND_HEIGHT

BACKGROUND = MovingImages(4, BACKGROUND_IMAGES, BACKGROUND_RECTS)
GROUND = MovingImages(10, GROUND_IMAGES, GROUND_RECTS)
GROUND_C = pygame.Rect(0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT)

def init_game():
    global SCREEN
    pygame.init()

    SCREEN = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("NEAT Jetpack")


class Player:
    rectangle = pygame.Rect(200, 0, 48, 96)

    acceleration = GRAVITY

    def __init__(self):
        pass

    def draw(self):
        pygame.draw.rect(SCREEN, (255, 255, 255), self.rectangle)

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


def draw_background():
    BG_COLOR = (0, 191, 255)
    BACKGROUND.update()


def draw_ground():
    G_COLOR = (105, 105, 105)
    GROUND.update()


def draw_objects(objects):
    for obj in objects:
        obj.draw()


def object_logic(objects):
    for obj in objects:
        obj.logic()


def process_player_input(player):
    if pygame.mouse.get_pressed()[0]:
        player.acceleration += FORCE


if __name__ in "__main__":
    player = Player()
    objects = [player]
    init_game()
    while True:
        CLOCK.tick(UPDATES_PER_SEC)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        draw_background()
        process_player_input(player)
        object_logic(objects)
        draw_objects(objects)
        draw_ground()
        # print(CLOCK.get_fps())
        pygame.display.flip()

# TODO: Dibuixar sprites del fondo i del terra (Galajat)
# TODO: Dibuixar sprites del personatge i objectes (Galajat)
# TODO: Fer el desplaçament del fondo (Galajat)
# TODO: Començar a mirar tema NEAT (Joe)
