import pygame
import sys
from math import floor

UPDATES_PER_SEC = 60
SIZE = WIDTH, HEIGHT = 1280, 720
SCREEN = None
CLOCK = pygame.time.Clock()

GROUND_HEIGHT = 100

GRAVITY = 1.0
FORCE = -1.75

class MovingImage():
    def __init__(self, speed, image, rect):
        self.speed = speed
        self.image = pygame.transform.scale(image, (rect.width, rect.height))
        self.rectangle = rect

    def update(self):
        self.rectangle.move_ip(-self.speed, 0)
        if self.rectangle.x <= -self.rectangle.width:
            self.rectangle.move_ip(-self.rectangle.x, 0)
        SCREEN.blit(self.image, self.rectangle)

BACKGROUND_REC1 = pygame.Rect(0, 0, WIDTH, HEIGHT)
BACKGROUND_REC2 = pygame.Rect(WIDTH, 0, WIDTH, HEIGHT)
BACKGROUND_IMAGE = pygame.image.load("assets/background.png")
GROUND_REC1 = pygame.Rect(0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT)
GROUND_REC2 = pygame.Rect(WIDTH, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT)
GROUND_IMAGE = pygame.image.load("assets/ground.png")

BACKGROUND1 = MovingImage(4, BACKGROUND_IMAGE, BACKGROUND_REC1)
GROUND1 = MovingImage(10, GROUND_IMAGE, GROUND_REC1)
BACKGROUND2 = MovingImage(4, BACKGROUND_IMAGE, BACKGROUND_REC2)
GROUND2 = MovingImage(10, GROUND_IMAGE, GROUND_REC2)

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

    def collides_with_ground(self, copy):
        return copy.colliderect(GROUND1.rectangle) or copy.colliderect(GROUND2.rectangle)

    def affected_by_acceleration(self):
        # Crear rectangle copia
        # Moure copia
        rect_copy = self.rectangle.move(0, floor(self.acceleration))
        # Mirar si colisione
        if self.collides_with_ground(rect_copy):
            # Si colisione, moure al jugador sol lo suficient, per no enfonsarse
            vert_dist = GROUND1.rectangle.y - (self.rectangle.y + self.rectangle.height)
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
    BACKGROUND1.update()
    BACKGROUND2.update()


def draw_ground():
    G_COLOR = (105, 105, 105)
    GROUND1.update()
    GROUND2.update()


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
        print(CLOCK.get_fps())
        pygame.display.flip()

# TODO: Dibuixar sprites del fondo i del terra (Galajat)
# TODO: Dibuixar sprites del personatge i objectes (Galajat)
# TODO: Fer el desplaçament del fondo (Galajat)
# TODO: Començar a mirar tema NEAT (Joe)
