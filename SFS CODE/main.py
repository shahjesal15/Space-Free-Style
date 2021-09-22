# SHMUP GAME
import pygame
import random
import os
import shelve

# ASSETS FOLDERS
game_folder = os.path.dirname(__file__)
assets_folder = os.path.join(game_folder, "assets")

# DEFINE CONSTANTS
HEIGHT = 700
WIDTH = 500
FPS = 90
FONT_NAME = pygame.font.match_font("arial")
BAR_LENGTH = 100
BAR_HEIGHT = 10
SPAWN_BOSS = True
SHIP_WON = False

# DEFINE COLORS
BLACK = (0, 0, 0)
WHITE  = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255,255,0)

# INIT WINDOW
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Space Free Style")
clock = pygame.time.Clock()

# ALL SPRITES
all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerUps = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()

# LOADING ASSETS
background = pygame.image.load(os.path.join(assets_folder, "background/0.jpg")).convert()
background_rect = background.get_rect()

logo = pygame.image.load(os.path.join(assets_folder, "Texts/0.png")).convert()
logo_rect  = logo.get_rect()
logo.set_colorkey(BLACK)

pop_laser = pygame.image.load(os.path.join(assets_folder,"power ups/buzzLazer.png")).convert()
pop_laser = pygame.transform.scale(pop_laser, (24,24))
enemy_laser = pygame.image.load(os.path.join(assets_folder,"Lasers/Mob0.png")).convert()
enemy_laser = pygame.transform.scale(enemy_laser, (10,20))
enemy = pygame.image.load(os.path.join(assets_folder, "Enemy/0.png")).convert()

meteors = [pygame.image.load(os.path.join(assets_folder, "meteors/0.png")).convert(),
pygame.image.load(os.path.join(assets_folder, "meteors/1.png")).convert(),
pygame.image.load(os.path.join(assets_folder, "meteors/2.png")).convert(),
pygame.image.load(os.path.join(assets_folder, "meteors/3.png")).convert(),
pygame.image.load(os.path.join(assets_folder, "meteors/4.png")).convert(),
pygame.image.load(os.path.join(assets_folder, "meteors/5.png")).convert(),
pygame.image.load(os.path.join(assets_folder, "meteors/6.png")).convert(),
pygame.image.load(os.path.join(assets_folder, "meteors/7.png")).convert(),
pygame.image.load(os.path.join(assets_folder, "meteors/8.png")).convert(),
pygame.image.load(os.path.join(assets_folder, "meteors/9.png")).convert()]

explosions = {
	'large': [pygame.image.load(os.path.join(assets_folder, 'explosions/{}.png'.format(x))) for x in range(0,9)],
	'small': [pygame.image.load(os.path.join(assets_folder, 'explosions/{}.png'.format(x))) for x in range(0,9)],
	'player': [pygame.image.load(os.path.join(assets_folder, 'Sonic Explosions/{}.png'.format(x))) for x in range(0,9)]	
}

powerUp = {
	'shield' : [pygame.image.load(os.path.join(assets_folder, 'power ups/shield.png')), lambda: increase_shield()],
	'lives' : [pygame.image.load(os.path.join(assets_folder, 'power ups/life.png')), lambda: increase_health()],
	'buzz' : [pygame.image.load(os.path.join(assets_folder, 'power ups/buzz.png')), lambda: increase_shoot()]
}

for index, large in enumerate(explosions['large']):
	large = pygame.transform.scale(large, (75, 75))
	large.set_colorkey(BLACK)
	explosions['large'][index] = large.convert()

for index, small in enumerate(explosions['small']):
	small = pygame.transform.scale(small, (32, 32))
	small.set_colorkey(BLACK)
	explosions['small'][index] = small.convert()

for index, player in enumerate(explosions['player']):
	player = pygame.transform.scale(player, (50, 50))
	player.set_colorkey(BLACK)
	explosions['player'][index] = player.convert()

laser_shoot = pygame.mixer.	Sound(os.path.join(assets_folder, "Sounds/Laser.wav"))
player_dead_sound = pygame.mixer.Sound(os.path.join(assets_folder, "Sounds/death.ogg"))

explosions_sound = [pygame.mixer.Sound(os.path.join(assets_folder, "Sounds/Explosion1.wav")),
pygame.mixer.Sound(os.path.join(assets_folder, "Sounds/Explosion2.wav")),
pygame.mixer.Sound(os.path.join(assets_folder, "Sounds/Explosion3.wav")),
pygame.mixer.Sound(os.path.join(assets_folder, "Sounds/Explosion4.wav"))]
powerup_sound = pygame.mixer.Sound(os.path.join(assets_folder, "Sounds/Powerup.wav"))
boss_sound = pygame.mixer.Sound(os.path.join(assets_folder, "Sounds/boss.wav"))

pop_sounds = [pygame.mixer.Sound(os.path.join(assets_folder, "Sounds/pop1.wav")),
	pygame.mixer.Sound(os.path.join(assets_folder, "Sounds/pop2.wav"))
]

pygame.mixer.music.load(os.path.join(assets_folder,"Sounds/looper.ogg"))
pygame.mixer.music.set_volume(0.4)

# USERDATA LOADER
class Userdata:
	def __init__(self): 
		global spaceship, laser
		self.data = {
			"level":None,
			"highest-score":None,
			"player_shield":0,
			"player_lives":0,
			"boss_lives":0,
			"boss_shield":0
		}
		with shelve.open(os.path.join(assets_folder, "User/userdata")) as file:
			if 'level' in file:
				self.data['level'] = file['level']
				self.data['highest-score'] = file['highest-score']
			else:
				self.data['level'] = 0
				self.data['highest-score'] = 0

		spaceship = pygame.image.load(os.path.join(assets_folder, "player/{}.png".format(self.data['level']))).convert()
		laser = pygame.image.load(os.path.join(assets_folder, "Lasers/{}.png".format(self.data['level']))).convert()
		self.load_Game()

	def finish(self):
		with shelve.open(os.path.join(assets_folder, "User/userdata")) as file:
			file['level'] = self.data['level']
			file['highest-score'] = self.data['highest-score']
	
	def updateUserData(self, score, level=None):
		self.data['highest-score'] = score if self.data['highest-score'] < score else self.data['highest-score']
		if not level is None:
			self.data['level'] = level

	def load_Game(self):
		with shelve.open(os.path.join(assets_folder, "Keys/data_keys")) as file:
			if not self.data['level'] == 0:
				self.data['player_lives'], self.data['player_shield'], self.data['damage'] = file[str(self.data['level'])]
			else:
				self.data['player_lives'], self.data['player_shield'], self.data['damage'] = 2, 100, 2
			if self.data['level'] < 10:
				self.data['boss_lives'], self.data['boss_shield'], temp = file[str(self.data['level']+1)]
			 

# PLAYER
class Player(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.image = spaceship
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.radius = 18
		self.rect.centerx = WIDTH / 2
		self.rect.bottom = HEIGHT + 25
		self.speedx = 0
		self.shield = userdata.data['player_shield']
		self.shoot_delay = 250
		self.last_shot = pygame.time.get_ticks()
		self.lives = userdata.data['player_lives']
		self.hidden = False
		self.hide_timer = pygame.time.get_ticks()
		self.respawned = False
		self.respawned_timer = pygame.time.get_ticks()
		self.kills = 15

	def update(self):
		if self.rect.bottom > HEIGHT - 30:
			self.rect.y -= 1

		if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
			self.hidden = False
			self.rect.centerx = WIDTH / 2
			self.rect.bottom = HEIGHT - 25
			self.respawned = True
			self.respawned = pygame.time.get_ticks()

		if pygame.time.get_ticks() - self.respawned > 2000:
			self.respawned = False

		self.speedx = 0
		keystate = pygame.key.get_pressed()
		if (keystate[pygame.K_LEFT] or keystate[pygame.K_a]) and self.rect.x > 0:
			self.speedx = -5
		if (keystate[pygame.K_RIGHT] or keystate[pygame.K_d]) and self.rect.x < WIDTH - 80:
			self.speedx = 5
		if keystate[pygame.K_SPACE]:
			self.shoot()
		self.rect.x += self.speedx

	def shoot(self):
		now = pygame.time.get_ticks()
		if now - self.last_shot > self.shoot_delay:
			self.last_shot = now
			bullet = Bullets(self.rect.x - 8, self.rect.top, laser)
			all_sprites.add(bullet)
			bullets.add(bullet)
			laser_shoot.play()

	def hide(self):
		# HIDE THE PLAYER TEMPORARILY
		self.hidden = True
		self.hide_timer = pygame.time.get_ticks()
		self.rect.centerx = WIDTH / 2 
		self.rect.bottom = HEIGHT + 200
		self.respawned_timer = pygame.time.get_ticks()

# BOSS
class Boss(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(os.path.join(assets_folder, "player/{}.png".format(userdata.data['level']+1))).convert()
		self.laser = pygame.image.load(os.path.join(assets_folder, "Lasers/{}.png".format(userdata.data['level']+1))).convert()
		self.laser.set_colorkey(BLACK)
		self.image.set_colorkey(BLACK)
		self.image = pygame.transform.rotate(self.image, 180)
		self.laser = pygame.transform.rotate(self.laser, 180)
		self.rect = self.image.get_rect()
		self.rect.x = WIDTH / 2
		self.rect.y = -70  
		self.shield = userdata.data['boss_shield']
		self.lives = userdata.data['boss_lives']
		self.speedx = 2
		self.speedy = 1
		self.movedelay = 90
		self.shoot_delay = 400
		self.last_moved = pygame.time.get_ticks()
		self.last_shot = pygame.time.get_ticks()

	def update(self):
		now = pygame.time.get_ticks()
		if now - self.last_moved > self.movedelay:
			self.move()
		if now - self.last_shot > self.shoot_delay:
			self.shoot()
			self.last_shot = now

	def move(self):
		self.rect.x += self.speedx
		if self.rect.y < 60:
			self.rect.y += self.speedy
		if self.rect.left > WIDTH - 60:
			self.speedx = -2
		if self.rect.right < 60:
			self.speedx = 2

	def shoot(self):
		bullet = Bullets(self.rect.centerx, self.rect.bottom, self.laser)
		bullet.speedy = 7
		all_sprites.add(bullet)
		enemy_bullets.add(bullet)

# MOB
class Mob(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.image_orig = random.choice(meteors)
		self.image_orig.set_colorkey(BLACK)
		self.image = self.image_orig.copy()
		self.rect = self.image.get_rect()
		self.radius = int(self.rect.width * .85 / 2)
		#pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
		self.rect.x = random.randrange(WIDTH - self.rect.width)
		self.rect.y = random.randrange(-100, -40)
		self.speedy = random.randrange(1, 2)
		self.speedx = random.randrange(-1, 1)
		self.rot = 0
		self.rot_speed = random.randrange(-8, 8)
		self.last_update = pygame.time.get_ticks()		

	def rotate(self):
		now = pygame.time.get_ticks()
		if now - self.last_update > 50:
			self.last_update = now
			self.rot = (self.rot + self.rot_speed) % 360
			new_image = pygame.transform.rotate(self.image_orig, self.rot)
			old_center = self.rect.center
			self.image = new_image
			self.rect = self.image.get_rect()
			self.rect.center = old_center

	def update(self):
		self.rotate()
		self.rect.y += self.speedy
		self.rect.x += self.speedx
		if self.rect.top > HEIGHT + 10 or self.rect.right > WIDTH + 20 or self.rect.left < -25:
			self.rect.x = random.randrange(WIDTH - self.rect.width)
			self.rect.y = random.randrange(-100, -40)
			self.speedy = random.randrange(1, 8)

# BULLETS
class Bullets(pygame.sprite.Sprite):
	def __init__(self, x, y, image):
		pygame.sprite.Sprite.__init__(self)
		self.image = image
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.rect.y = y
		self.rect.x = x
		self.speedy = -10

	def update(self):
		self.rect.y += self.speedy
		# BULLET OFF THE BOARD
		if self.rect.bottom < 0:
			self.kill()

# POWERUPS
class PowerUp(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = random.choice(['lives', 'shield', 'buzz'])
		self.powerup = powerUp[self.image][1]
		self.image = powerUp[self.image][0]
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.rect.bottom = y
		self.rect.centerx = x
		self.speedy = 2

	def update(self):
		self.rect.y += self.speedy
		# BULLET OFF THE BOARD
		if self.rect.bottom < 0:
			self.kill()

# BUZZ KILL
class BuzzKill(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pop_laser
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.rect.bottom = y
		self.rect.centerx = x
		self.speedy = -3

	def update(self):
		self.rect.y += self.speedy
		# BULLET OFF THE BOARD
		if self.rect.bottom < 0:
			self.kill()

# KILLER BOTS
class KillerT(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.image = enemy
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.radius = int(self.rect.width * .85 / 2)
		#pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
		self.rect.x = random.randrange(WIDTH - self.rect.width)
		self.rect.y = random.randrange(-100, -40)
		self.speedy = random.randrange(1, 3)
		self.speedx = random.randrange(-1, 1)
		self.last_shot = pygame.time.get_ticks()
		self.shoot_delay = 800	

	def update(self):
		self.rect.y += self.speedy
		self.rect.x += self.speedx
		
		if pygame.time.get_ticks() - self.last_shot > self.shoot_delay:
			self.shoot()

		if self.rect.top > HEIGHT + 10 or self.rect.right > WIDTH + 20 or self.rect.left < -25:
			self.rect.x = random.randrange(WIDTH - self.rect.width)
			self.rect.y = random.randrange(-100, -40)
			self.speedy = random.randrange(2, 4)

	def shoot(self):
		self.last_shot = pygame.time.get_ticks()
		bullet = Bullets(self.rect.centerx, self.rect.bottom, enemy_laser)
		bullet.speedy = 4
		all_sprites.add(bullet)
		enemy_bullets.add(bullet)

# EXPLOSIONS
class Explosions(pygame.sprite.Sprite):
	def __init__(self, center, size):
		pygame.sprite.Sprite.__init__(self)
		self.size = size
		self.image = explosions[self.size][0]
		self.rect = self.image.get_rect()
		self.rect.center = center
		self.frame = 0
		self.last_update = pygame.time.get_ticks()
		self.frame_rate = 75

	def update(self):
		now = pygame.time.get_ticks()
		if now - self.last_update > self.frame_rate:
			self.last_update = now
			self.frame += 1
			if self.frame == len(explosions[self.size]):
				self.kill()
			else:
				center = self.rect.center
				self.image = explosions[self.size][self.frame]
				self.rect = self.image.get_rect()
				self.rect.center = center

# INTERFACE SCREEN
def interfaceScreen():
	running = True
	change = False
	pygame.init()
	spaceship_rect = spaceship.get_rect()
	color = BLACK
	delay = pygame.time.get_ticks()
	spaceship.set_colorkey(BLACK)
	while running:
		clock.tick(FPS)
		now = pygame.time.get_ticks()
		scroll_background()
		screen.blit(logo, (WIDTH / 2 - logo_rect.width /2 + 5, HEIGHT / 6))
		screen.blit(spaceship, (WIDTH / 2 - spaceship_rect.width / 2, HEIGHT - 350))
		draw_text(screen, "Highest Score : "+str(userdata.data['highest-score']), 20,WIDTH / 2 + 4, HEIGHT - 180)
		draw_text(screen, "Any key to continue...", 18, WIDTH / 2 + 2, HEIGHT - 120,color = color)
		draw_text(screen,"Developed by : Jesal Shah", 12, 90, HEIGHT - 20)
		draw_text(screen,"Art Credits : OpenGameArt.org", 12, WIDTH - 100, HEIGHT - 20)
		if now - delay > 400:
			if color == BLACK:
				color = WHITE
			else:
				color = BLACK
			delay = now
		for event in pygame.event.get():
			if event.type == pygame.KEYUP:
				splashScreen(WIDTH / 2 - spaceship_rect.width / 2 + 5, HEIGHT - 250)
				running = False
			if event.type == pygame.QUIT:
				pygame.quit()
		pygame.display.flip()

# SPLASH SCREEN
def splashScreen(x, y):
	update = pygame.time.get_ticks()
	spaceship.set_colorkey(BLACK)
	while True:
		clock.tick(FPS)
		scroll_background()
		screen.blit(spaceship,(x, y))
		if pygame.time.get_ticks() - update > 10:
			y -= 15	
			if y <= 0:
				break
			update = pygame.time.get_ticks()
		pygame.display.flip()

# WON A SPACESHIP
def spaceShipWon():
	running = True
	won = pygame.image.load(os.path.join(assets_folder, "player/{}.png".format(userdata.data['level']+1))).convert()
	won.set_colorkey(BLACK)
	won_rect = won.get_rect()
	delay = pygame.time.get_ticks()
	color = BLACK
	while running:
		clock.tick(FPS)
		now = pygame.time.get_ticks()
		scroll_background()
		screen.blit(logo, (WIDTH / 2 - logo_rect.width / 2, HEIGHT / 6))
		screen.blit(won, (WIDTH / 2 - won_rect.width / 2, HEIGHT - 350))
		draw_text(screen, "New Space Ship Unlocked !",18, WIDTH / 2, HEIGHT - 150)
		draw_text(screen, "Any key to continue...", 18, WIDTH / 2 + 2, HEIGHT - 100,color = color)
		if now - delay > 400:
			if color == BLACK:
				color = WHITE
			else:
				color = BLACK
			delay = now
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
			if event.type == pygame.KEYUP:
				running = False
		pygame.display.flip()

# DRAWING PAUSE OR GAMEOVER SCREEN
def gameOverScreen():
	global score, spaceship, userdata, SHIP_WON
	running = True
	spaceship_rect = spaceship.get_rect()
	spaceship.set_colorkey(BLACK)
	delay = pygame.time.get_ticks()
	color = BLACK
	if SHIP_WON is True:
			spaceShipWon()
			SHIP_WON = False
	while running:
		clock.tick(FPS)
		now = pygame.time.get_ticks()
		scroll_background()
		draw_text(screen, "Game Over", 20, WIDTH / 2, HEIGHT / 4)
		screen.blit(logo, (WIDTH / 2 - logo_rect.width / 2, HEIGHT / 3))
		screen.blit(spaceship, (WIDTH / 2 - spaceship_rect.width / 2, HEIGHT - 250))
		draw_text(screen, "Score : "+str(score),18, WIDTH / 2, HEIGHT - 150)
		draw_text(screen, "Any key to continue...", 18, WIDTH / 2 + 2, HEIGHT - 100,color = color)
		if now - delay > 400:
			if color == BLACK:
				color = WHITE
			else:
				color = BLACK
			delay = now
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
			if event.type == pygame.KEYUP:
				SPAWN_BOSS = True
				userdata.updateUserData(score)
				userdata.finish()
				userdata.__init__()
				player.__init__()
				boss.__init__()
				score = 0
				splashScreen(WIDTH / 2 - spaceship_rect.width / 2, HEIGHT - 250)
				interfaceScreen()
				running = False

		pygame.display.flip()


# SPWAN A MOB
def spawnMob():
	m = random.choice([Mob(),KillerT()])
	all_sprites.add(m)
	mobs.add(m)

# DRAWING TEXT
def draw_text(surface, text, size, x, y, color=WHITE):
	font = pygame.font.Font(FONT_NAME, size)
	text_surface = font.render(text, True, color)
	text_rect = text_surface.get_rect()
	text_rect.midtop = (x, y)
	surface.blit(text_surface, text_rect)	

# DRAWING SHIELD BAR
def draw_shield_bar(surface, x, y, percentage, shield=100):
	if percentage < 0:
		percentage = 0
	fill = (percentage / shield) * BAR_LENGTH
	outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
	fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
	pygame.draw.rect(surface, GREEN, fill_rect)
	pygame.draw.rect(surface, WHITE, outline_rect, 2)

# MAKING EXPLOSION
def making_explosion(hit):
	random.choice(explosions_sound).play()
	if hit.radius > 25:
		all_sprites.add(Explosions(hit.rect.center, 'large'))
	else:
		all_sprites.add(Explosions(hit.rect.center, 'small'))

# DRAWING LIVES
def draw_lives(surface, x, y, lives, image):
	for i in range(lives):
		image_rect = image.get_rect()
		image_rect.x = x + 30 * i
		image_rect.y = y
		surface.blit(image, image_rect)

# ALLOCATING POWERUPS
def increase_shield():
	global player 
	player.shield += 30
	if player.shield > userdata.data['player_shield']:
		player.shield = userdata.data['player_shield']

def increase_health():
	global player
	player.lives += 1
	if player.lives > 3:
		player.lives = 3

def increase_shoot():
	global player
	player.kills = 20
	for i in range(0,15):
		y, x = random.randrange(350,550), random.randrange(10,470)
		bullet = BuzzKill(x ,y)
		all_sprites.add(bullet)
		bullets.add(bullet)
	random.choice(pop_sounds).play()

# LOADING USERDATA
spaceship = None
laser = None
userdata = Userdata()
spaceship_lives = pygame.transform.scale(spaceship, (25, 19))
spaceship_lives.set_colorkey(BLACK)

# SCROLL BACKGROUND ASSETS
update_scroll = pygame.time.get_ticks()
follow_background = background.copy()
follow_background_rect = follow_background.get_rect()
follow_background_rect.bottom = background_rect.top
now = pygame.time.get_ticks()

def scroll_background():
	global now
	screen.fill(BLACK)
	if pygame.time.get_ticks() - now > 50:
		background_rect.move_ip(0, 2)
		follow_background_rect.move_ip(0, 2)
		now = pygame.time.get_ticks()
	if background_rect.top == HEIGHT:
		background_rect.bottom = follow_background_rect.top
	if follow_background_rect.top == HEIGHT:
		follow_background_rect.bottom = background_rect.top   
	screen.blit(background, background_rect)
	screen.blit(follow_background, follow_background_rect)

# GAME LOOP
running = True

# PLAYER
player = Player()
boss = Boss()
all_sprites.add(player)

# SPAWING MOBS
for m in range(5):
	spawnMob()

# LOADING UTILITIES
pygame.mixer.music.play(loops=-1)
death_explosion = None

# SCORES
score = 0

# GAME LOOP
def mainLoop():
	global running, score, SPAWN_BOSS, SHIP_WON, spaceship
	while running:
	# FPS
		clock.tick(FPS)
		# PROCESS AND INPUTS
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

		# UPDATE
		all_sprites.update()
		scroll_background()
		# DRAW AND RENDER
		all_sprites.draw(screen)
		draw_text(screen,"Score : " + str(score), 18, WIDTH / 2, 10)
		draw_shield_bar(screen, 10, 10, player.shield,shield=userdata.data['player_shield'])
		if boss.alive():
			draw_shield_bar(screen, boss.rect.x - 10,  boss.rect.y - 5, boss.shield,shield=userdata.data['boss_shield'])
			#adraw_lives(screen, boss.rect.x - 25, boss.rect.y - 10, boss.lives)
		draw_lives(screen, WIDTH - 100, 10, player.lives, spaceship_lives)
	

		# CHECK TO SEE IF MOBS DELETED BY BULLETS SAME FOR BULLETS
		hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
		for hit in hits:
			score += hit.radius
			player.kills -= 1
			making_explosion(hit)
			mobs.remove(hit)
			all_sprites.remove(hit)
			# POWERUPS
			if player.kills <= 0:
				power = PowerUp(hit.rect.x, hit.rect.y)
				all_sprites.add(power)
				powerUps.add(power)
				player.kills = 15

			spawnMob()
		
		hits = pygame.sprite.spritecollide(player, powerUps, True)
		for hit in hits:
			hit.powerup()	
			powerup_sound.play()
			powerUps.remove(hit)
			all_sprites.remove(hit)

		# CHECK TO SEE IF MOBS COLLIDED
		if not player.respawned:
			hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)

			for hit in hits:
				player.shield -= hit.radius * 2
				making_explosion(hit)
				spawnMob()
				mobs.remove(hit)
				all_sprites.remove(hit)
				if player.shield <= 0:
					player_dead_sound.play()
					death_explosion = Explosions(player.rect.center, 'player')
					all_sprites.add(death_explosion)
					player.hide()
					player.lives -= 1
					player.shield = userdata.data['player_shield']

		# ENEMY BULLET HITS PLAYER BULLET
		hits = pygame.sprite.groupcollide(enemy_bullets, bullets, True, True)

		# ENEMY BULLETS HIT
		if not player.respawned:
			hits = pygame.sprite.spritecollide(player, enemy_bullets, True)

		for hit in hits:
			player.shield -= 4
			if player.shield <= 0:
				player_dead_sound.play()
				death_explosion = Explosions(player.rect.center, 'player')
				all_sprites.add(death_explosion)
				player.hide()
				player.lives -= 1
				player.shield = 100

		# SPAWNING BOSS
		if SPAWN_BOSS is True: 
			if score >= (userdata.data['level']+1)*500 and userdata.data['level'] < 10:
				all_sprites.add(boss)
				boss_sound.play()
				SPAWN_BOSS = False

		if boss.alive():
			hits = pygame.sprite.spritecollide(boss, bullets, True)
			for hit in hits:
				boss.shield -= userdata.data['damage'] + 3	
				if boss.shield <= 0:
					boss.lives -= 1
					boss.shield = userdata.data['boss_shield']
				if boss.lives == 0:
					boss.kill()
					all_sprites.remove(boss)
					death_explosion = Explosions(boss.rect.center, 'large')
					userdata.updateUserData(score,level=userdata.data['level']+1)
					userdata.finish()
					all_sprites.add(death_explosion)
					SHIP_WON = True

		# END GAME	
		if player.lives == 0 and not death_explosion.alive():
			gameOverScreen()

		# AFTER DRAWING EVERYTHING
		pygame.display.flip()

interfaceScreen()
mainLoop()

userdata.updateUserData(score)
userdata.finish()

pygame.quit()