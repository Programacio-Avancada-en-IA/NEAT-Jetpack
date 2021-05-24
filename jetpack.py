import pygame
import sys
from math import floor, ceil, sqrt
import random
import neat

UPDATES_PER_SEC = 60
SIZE = WIDTH, HEIGHT = 1280, 720
SCREEN = None
BACKGROUND = None
FAROLES = None
GROUND = None
GROUND_C = None
RUNNING = True
PASSED = False
CLOCK = pygame.time.Clock()
objects = []

GAME_SPEED = 8

GROUND_HEIGHT = 100

PLAYER_WIDTH = 64
PLAYER_HEIGHT = 128

GRAVITY = 1.0
FORCE = -1.75

LASER_IMAGES = [pygame.image.load("assets/vlaser.png"), pygame.image.load("assets/dulaser.png"),
                pygame.image.load("assets/hlaser.png"), pygame.image.load("assets/ddlaser.png"),
                pygame.image.load("assets/vlaser.png")]


# An image that moves when updated, used for the background, ground and lights
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


# A sprite with different frames, used to animate the character running
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
		return self.images[self.image_index]


# A single electric ball that together with lasers and another ball form a CoilPair
class Coil:
	rect = None
	size = 64
	image = pygame.image.load("assets/coil.png")
	center_image = pygame.image.load("assets/coil_center.png")

	def __init__(self, location):
		self.x, self.y = location
		self.image = self.image.convert_alpha()
		self.image = pygame.transform.scale(self.image, (self.size, self.size))
		self.center_image = self.center_image.convert_alpha()
		self.center_image = pygame.transform.scale(self.center_image, (self.size, self.size))
		self.rect = pygame.Rect(round(self.x), round(self.y), self.size, self.size)

	def draw(self):
		# pygame.draw.rect(SCREEN, (0, 0, 255), self.rect, width=3)
		SCREEN.blit(self.image, self.rect)

	def draw_center(self):
		SCREEN.blit(self.center_image, self.rect)

	def logic(self):
		self.rect.move_ip(-GAME_SPEED, 0)

	def collides(self, player):
		if self.collides_rect(player):
			if self.collides_mask(player):
				return True
		return False

	def collides_rect(self, player):
		return self.rect.colliderect(player.rectangle)

	def collides_mask(self, player):
		player_mask = pygame.mask.from_surface(player.current_sprite)
		player_head_mask = pygame.mask.from_surface(player.head_sprite)
		self.mask = pygame.mask.from_surface(self.image)
		offset = (round(self.rect.x - player.x), round(self.rect.y - player.rectangle.y))
		if player_mask.overlap(self.mask, offset) or player_head_mask.overlap(self.mask, offset):
			return True
		return False


# A laser object that appears between 2 coils
class Laser:
	rect = None
	image = None
	mask = None
	LASER_SHORT = 16
	LASER_LONG = 64
	hor_size = LASER_SHORT
	ver_size = LASER_LONG
	rect_size = round((hor_size // sqrt(2)) + (ver_size // sqrt(2)))

	def __init__(self, location, direction):
		self.x, self.y = location
		self.image = LASER_IMAGES[direction]
		if direction == 0 or direction == 4:
			self.image = pygame.transform.scale(self.image, (self.hor_size, self.ver_size))
			self.rect = pygame.Rect(round(self.x), round(self.y), self.hor_size, self.ver_size)
		elif direction == 1 or direction == 3:
			self.image = pygame.transform.scale(self.image, (Laser.rect_size, Laser.rect_size))
			self.rect = pygame.Rect(round(self.x), round(self.y), Laser.rect_size, Laser.rect_size)
		elif direction == 2:
			self.image = pygame.transform.scale(self.image, (self.LASER_LONG, self.LASER_SHORT))
			self.rect = pygame.Rect(round(self.x), round(self.y), self.ver_size, self.hor_size)
		self.mask = pygame.mask.from_surface(self.image)

	def collides(self, player):
		if self.collides_rect(player):
			if self.collides_mask(player):
				return True
		return False

	def collides_rect(self, player):
		return self.rect.colliderect(player.rectangle)

	def collides_mask(self, player):
		player_mask = pygame.mask.from_surface(player.current_sprite)
		player_head_mask = pygame.mask.from_surface(player.head_sprite)
		self.mask = pygame.mask.from_surface(self.image)
		offset = (round(self.rect.x - player.x), round(self.rect.y - player.rectangle.y))
		if player_mask.overlap(self.mask, offset) or player_head_mask.overlap(self.mask, offset):
			return True
		return False

	def draw(self):
		# pygame.draw.rect(SCREEN, (255, 0, 0), self.rect, width=3)
		SCREEN.blit(self.image, self.rect)

	def logic(self):
		self.rect.move_ip(-GAME_SPEED, 0)


# A pair of coils connected by lasers, the main obstacles of the game
class CoilPair:
	objects = []

	# Location per crear el coil 1
	# Direccio de les 5 possibles
	# Mida del laser, si mes gran o petit
	def __init__(self, coil_1_location, direction, size):
		self.coil_1 = Coil(coil_1_location)
		# Up
		half_coil_size = self.coil_1.size // 2
		self.lasers = []
		if direction == 0:
			starting_point = self.coil_1.y + half_coil_size
			elem_x = self.coil_1.x + half_coil_size - (Laser.hor_size // 2)
			last_y = 0
			for i in range(size):
				self.lasers.append(Laser((elem_x, starting_point - (i + 1) * Laser.ver_size), direction))
				last_y = starting_point - (i + 1) * Laser.ver_size
			self.coil_2 = Coil((self.coil_1.x, last_y - Laser.ver_size + half_coil_size))
		elif direction == 1:
			laser_offset = (Laser.LASER_SHORT // sqrt(2))
			starting_x = self.coil_1.x + half_coil_size - (laser_offset // 2)
			starting_y = self.coil_1.y + half_coil_size + (laser_offset // 2) - (Laser.rect_size)
			last_x = last_y = 0
			for i in range(size):
				self.lasers.append(Laser((starting_x + i * (Laser.rect_size - laser_offset),
				                          starting_y - i * (Laser.rect_size - laser_offset)), 1))
				last_x = starting_x + i * (Laser.rect_size - laser_offset)
				last_y = starting_y - i * (Laser.rect_size - laser_offset)
			self.coil_2 = Coil((last_x + Laser.rect_size - (laser_offset // 2) - half_coil_size,
			                    last_y + (laser_offset // 2) - half_coil_size))
		elif direction == 2:
			elem_y = self.coil_1.y + half_coil_size - (Laser.LASER_SHORT // 2)
			starting_point = self.coil_1.x + half_coil_size
			last_x = 0
			for i in range(size):
				self.lasers.append(Laser((starting_point + i * Laser.LASER_LONG, elem_y), direction))
				last_x = starting_point + i * Laser.LASER_LONG
			self.coil_2 = Coil((last_x + Laser.LASER_LONG - half_coil_size, self.coil_1.y))
		elif direction == 3:
			laser_offset = (Laser.LASER_SHORT // sqrt(2))
			starting_x = self.coil_1.x + half_coil_size - (laser_offset // 2)
			starting_y = self.coil_1.y + half_coil_size - (laser_offset // 2)
			last_x = last_y = 0
			for i in range(size):
				self.lasers.append(Laser((starting_x + i * (Laser.rect_size - laser_offset),
				                          starting_y + i * (Laser.rect_size - laser_offset)), 3))
				last_x = starting_x + i * (Laser.rect_size - laser_offset)
				last_y = starting_y + i * (Laser.rect_size - laser_offset)
			self.coil_2 = Coil((last_x + Laser.rect_size - (laser_offset // 2) - half_coil_size,
			                    last_y + Laser.rect_size - (laser_offset // 2) - half_coil_size))
		elif direction == 4:
			starting_point = self.coil_1.y + half_coil_size
			elem_x = self.coil_1.x + half_coil_size - (Laser.hor_size // 2)
			last_y = 0
			for i in range(size):
				self.lasers.append(Laser((elem_x, starting_point + i * Laser.ver_size), direction))
				last_y = starting_point + i * Laser.ver_size
			self.coil_2 = Coil((self.coil_1.x, last_y + Laser.ver_size - half_coil_size))
		self.objects.append(self.coil_1)
		self.objects.append(self.coil_2)
		self.objects.extend(self.lasers)

	def logic(self):
		self.coil_1.logic()
		self.coil_2.logic()
		for laser in self.lasers:
			laser.logic()

	def draw(self):
		self.coil_1.draw()
		self.coil_2.draw()
		for laser in self.lasers:
			laser.draw()
		self.coil_1.draw_center()
		self.coil_2.draw_center()

	def collides(self, player):
		for obj in self.objects:
			if obj.collides(player):
				return True
		return False


class CoilPairGenerator:

	def __init__(self):
		self.last_obstacle = 0
		self.last_ground = 0

	def generate_pair(self):
		global objects
		direction = random.randint(0, 4)  # Random orientation between 5 possibles
		size = random.randint(3, 6)  # Random size between 2 and 6 lasers
		# Possible heights
		height = 100
		if direction == 0:
			height = random.randint(Laser.LASER_LONG * size, HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT - 30 - Coil.size)
		elif direction == 1:
			height = random.randint(Laser.rect_size * size, HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT - 30 - Coil.size)
		elif direction == 2:
			height = random.randint(0, HEIGHT - GROUND_HEIGHT - Coil.size)
		elif direction == 3:
			height = random.randint(PLAYER_HEIGHT + 30, HEIGHT - GROUND_HEIGHT - Laser.rect_size * size)
		elif direction == 4:
			height = random.randint(PLAYER_HEIGHT + 30, PLAYER_HEIGHT + 30 + Laser.LASER_LONG * size)
		self.last_ground += 1

		if self.last_ground > 3:
			if direction == 0:
				try:
					height = random.randint(150 + Laser.LASER_LONG * size,
					                        HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT - 30 - Coil.size)
				except ValueError:
					height = HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT - 30 - Coil.size
			elif direction == 1:
				try:
					height = random.randint(150 + Laser.rect_size * size,
					                        HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT - 30 - Coil.size)
				except ValueError:
					height = HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT - 30 - Coil.size
			elif direction == 2:
				try:
					height = random.randint(150, HEIGHT - GROUND_HEIGHT - Coil.size)
				except ValueError:
					height = HEIGHT - GROUND_HEIGHT - Coil.size - 50
			elif direction == 3:
				try:
					height = random.randint(150 + PLAYER_HEIGHT + 30, HEIGHT - GROUND_HEIGHT - Laser.rect_size * size)
				except ValueError:
					height = HEIGHT - GROUND_HEIGHT - Laser.rect_size * size
			elif direction == 4:
				try:
					height = random.randint(150 + PLAYER_HEIGHT + 30, PLAYER_HEIGHT + 30 + Laser.LASER_LONG * size)
				except ValueError:
					height = PLAYER_HEIGHT + 30 + Laser.LASER_LONG * size
			self.last_ground = 0
		pair = CoilPair((2000, height), direction, size)
		objects.append(pair)

	def logic(self):
		global PASSED
		self.last_obstacle += GAME_SPEED
		if self.last_obstacle >= 800:
			self.last_obstacle = 0
			self.generate_pair()
			PASSED = True

	# Does not draw anything
	def draw(self):
		pass

	def collides(self, player):
		return False


def init_game():
	global SCREEN, BACKGROUND, GROUND, FAROLES, GROUND_C
	pygame.init()

	SCREEN = pygame.display.set_mode(SIZE)
	pygame.display.set_caption("NEAT Jetpack")

	bg_image = pygame.image.load("assets/background.png").convert_alpha()
	BACKGROUND_IMAGES = [pygame.transform.scale(bg_image, (WIDTH, HEIGHT))] * (
			ceil(WIDTH / bg_image.get_rect().width)
			+ 1)
	gr_image = pygame.image.load("assets/ground.png").convert_alpha()
	GROUND_IMAGES = [pygame.transform.scale(gr_image, (WIDTH, GROUND_HEIGHT))] * (
			ceil(WIDTH / gr_image.get_rect().width)
			+ 1)

	fa_image = pygame.image.load("assets/farola.png")
	fa_image.set_colorkey((255, 255, 255))
	fa_image = fa_image.convert_alpha()
	new_width = floor(fa_image.get_rect().width * 0.8)
	new_height = floor(fa_image.get_rect().height * 0.8)
	FA_IMAGES = [pygame.transform.scale(fa_image, (new_width, new_height))] * (
			ceil(WIDTH / fa_image.get_rect().width)
			+ 1)

	BACKGROUND_RECTS = [img.get_rect() for img in BACKGROUND_IMAGES]
	GROUND_RECTS = [img.get_rect() for img in GROUND_IMAGES]
	FA_RECTS = [img.get_rect() for img in FA_IMAGES]

	for rect in GROUND_RECTS:
		rect.y = HEIGHT - GROUND_HEIGHT

	for rect in FA_RECTS:
		rect.y = HEIGHT - GROUND_HEIGHT - rect.height

	BACKGROUND = MovingImages(3, BACKGROUND_IMAGES, BACKGROUND_RECTS)
	GROUND = MovingImages(GAME_SPEED, GROUND_IMAGES, GROUND_RECTS)
	FAROLES = MovingImages(3, FA_IMAGES, FA_RECTS, offset=200)
	GROUND_C = pygame.Rect(0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT)

	for i, laser_image in enumerate(LASER_IMAGES):
		LASER_IMAGES[i] = laser_image.convert_alpha()


class Player:
	x = 180
	rectangle = pygame.Rect(x, 0, PLAYER_WIDTH, PLAYER_HEIGHT)

	current_sprite = None
	air_sprite = None
	prop_sprite = None
	running_sp = None
	head_sprite = None
	# 0: running
	# 1: falling
	# 2: propulsing
	state = 0

	acceleration = GRAVITY

	def __init__(self):
		self.air_sprite = pygame.image.load("assets/on_air.png").convert_alpha()
		self.air_sprite = pygame.transform.scale(self.air_sprite, (PLAYER_WIDTH, PLAYER_HEIGHT))
		self.prop_sprite = pygame.image.load("assets/prop.png").convert_alpha()
		self.prop_sprite = pygame.transform.scale(self.prop_sprite, (PLAYER_WIDTH, PLAYER_HEIGHT))
		self.running_sp = AnimatedSprite(
			[pygame.image.load("assets/running/" + str(i) + ".png").convert_alpha()
			 for i in range(1, 9)], 3)
		for i, sp in enumerate(self.running_sp.images):
			self.running_sp.images[i] = pygame.transform.scale(sp, (PLAYER_WIDTH, PLAYER_HEIGHT))
		head = random.randint(1, 5)
		self.head_sprite = pygame.image.load("assets/pibes/" + str(head) + ".png").convert_alpha()

	def draw(self):
		if self.state == 0:
			self.running_sp.update()
			self.current_sprite = self.running_sp.draw(self.rectangle)
		elif self.state == 1:
			self.current_sprite = self.air_sprite
			SCREEN.blit(self.air_sprite, self.rectangle)
		elif self.state == 2:
			self.current_sprite = self.prop_sprite
			SCREEN.blit(self.prop_sprite, self.rectangle)
		# pygame.draw.rect(SCREEN, (0, 255, 0), self.rectangle, width=3)
		SCREEN.blit(self.head_sprite, self.rectangle)

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
		if self.rectangle.y >= (HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT - 1):
			# Running on the ground
			self.state = 0
		elif not pygame.mouse.get_pressed()[0] and not self.state == 0:
			# Player not running and not propulsing
			self.state = 1

	def process_input(self):
		if pygame.mouse.get_pressed()[0]:
			self.acceleration += FORCE
			self.state = 2

	def activated(self):
		self.acceleration += FORCE
		self.state = 2

	def check_for_interactions(self, objects):
		for obj in objects:
			if obj.collides(self):
				return True
		return False


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


def object_logic(addons=None):
	if addons is None:
		addons = []
	global objects
	for obj in objects + addons:
		obj.logic()
	for obj in objects:
		if type(obj) == CoilPair:
			if obj.coil_2.rect.x + Coil.size < 0:
				objects = objects[1:]
				break
	print(len(objects))


def main(genomes, config):
	global objects, RUNNING, PASSED
	init_game()

	nets = []
	ge = []
	players = []

	for _, g in genomes:
		net = neat.nn.FeedForwardNetwork.create(g, config)
		nets.append(net)
		players.append(Player())
		g.fitness = 0
		ge.append(g)

	generator = CoilPairGenerator()
	objects = []
	generator.generate_pair()
	while RUNNING:
		CLOCK.tick(UPDATES_PER_SEC)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				# print(sum(fps)/len(fps))
				RUNNING = False
				sys.exit()

		laser_ind = 0
		if len(players) > 0:
			if len(objects) > 1 and players[0].rectangle.x > objects[0].coil_2.rect.x + Coil.size:
				laser_ind = 1
		else:
			RUNNING = False
			break
		print(laser_ind, len(objects))
		draw_background()
		for ind, plr in enumerate(players):
			plr.logic()
			ge[ind].fitness += 0.1

			player_height = HEIGHT - GROUND_HEIGHT - plr.rectangle.y + PLAYER_HEIGHT
			player_top = plr.rectangle.y
			hor_coil1 = objects[laser_ind].coil_1.rect.x - Player.x
			hor_coil2 = objects[laser_ind].coil_2.rect.x - Player.x
			ver_coil1 = objects[laser_ind].coil_1.rect.y - plr.rectangle.y
			ver_coil2 = objects[laser_ind].coil_2.rect.y - plr.rectangle.y
			output = nets[ind].activate((player_height, player_top, hor_coil1, hor_coil2, ver_coil1, ver_coil2))

			if output[0] > 0.5:
				plr.activated()

			if plr.check_for_interactions(objects):
				ge[ind].fitness -= 1
				players.pop(ind)
				nets.pop(ind)
				ge.pop(ind)
			plr.draw()
		object_logic([generator])
		if PASSED:
			for g in ge:
				g.fitness += 5
			PASSED = False
		draw_objects(objects)
		draw_ground()
		# fps.append(CLOCK.get_fps())
		pygame.display.flip()
	# inp = input("")


def run(config_path):
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
	                            neat.DefaultStagnation, config_path)

	# Population
	p = neat.Population(config)

	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)

	winner = p.run(main, 50)


if __name__ in "__main__":
	config_path = "config-feedforward.txt"
	run(config_path)
