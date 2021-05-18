import pygame
import sys
from math import floor

UPDATES_PER_SEC = 60
SIZE = WIDTH, HEIGHT = 1280, 720
SCREEN = None
CLOCK = pygame.time.Clock()

GROUND_HEIGHT = 100

BACKGROUND = pygame.Rect(0, 0, WIDTH, HEIGHT)
GROUND = pygame.Rect(0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT)

GRAVITY = 1.0
FORCE = -1.75


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
        if rect_copy.colliderect(GROUND):
            # Si colisione, moure al jugador sol lo suficient, per no enfonsarse
            vert_dist = GROUND.y - (self.rectangle.y + self.rectangle.height)
            self.rectangle.move_ip(0, vert_dist)
            self.acceleration = 0
        elif rect_copy.y <= 0:
            vert_dist = -self.rectangle.y
            self.rectangle.move_ip(0, vert_dist)
            self.acceleration = GRAVITY
        else:
            if not self.rectangle.colliderect(GROUND):
                self.rectangle.move_ip(0, floor(self.acceleration))
                self.acceleration += GRAVITY
            else:
                self.acceleration = 0

    def logic(self):
        self.affected_by_acceleration()


def draw_background():
    pygame.draw.rect(SCREEN, (0, 191, 255), BACKGROUND)


def draw_ground():
    pygame.draw.rect(SCREEN, (105, 105, 105), GROUND)


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
        pygame.display.flip()

# TODO: Dibuixar sprites del fondo i del terra (Galajat)
# TODO: Dibuixar sprites del personatge i objectes (Galajat)
# TODO: Fer el desplaçament del fondo (Galajat)
# TODO: Començar a mirar tema NEAT (Joe)
