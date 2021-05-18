import pygame
import sys
from math import floor

UPDATES_PER_SEC = 30
SIZE = WIDTH, HEIGHT = 1280, 720
SCREEN = None
CLOCK = pygame.time.Clock()

BACKGROUND = pygame.Rect(0, 0, WIDTH, HEIGHT)
GROUND = pygame.Rect(0, HEIGHT - 180, WIDTH, 180)

GRAVITY = 1.0
FORCE = -2.5

def init_game():
    global SCREEN
    pygame.init()

    SCREEN = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("NEAT Jetpack")

class Player:
    rectangle = pygame.Rect(WIDTH//2, 0, 64, 128)

    acceleration = GRAVITY

    def __init__(self):
        pass

    def draw(self):
        pygame.draw.rect(SCREEN, (100, 100, 100), self.rectangle)

    def affected_by_acceleration(self):
        # Crear rectangle copia
        # Moure copia
        rect_copy = self.rectangle.move(0, floor(self.acceleration))
        # Mirar si colisione
        if rect_copy.colliderect(GROUND):
            # Si colisione, moure al jugador sol lo suficient, per no enfonsarse
            vert_dist = GROUND.y - (self.rectangle.y + 128)
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
    pygame.draw.rect(SCREEN, (255, 0, 150), BACKGROUND)

def draw_ground():
    pygame.draw.rect(SCREEN, (0, 255, 150), GROUND)

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
