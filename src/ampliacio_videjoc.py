import pygame
import random
import sys
import os

# Config rutas imgs
MENU_IMAGE_PATH = "assets/background/space.jpg"
BACKGROUND_IMAGE_PATH = "assets/background/space.jpg"
PLAYER_FULL_HEALTH_PATH = "assets/ship/MainShip_FullHealth.png"
PLAYER_SLIGHT_DAMAGE_PATH = "assets/ship/MainShip_SlightDamage.png"
PLAYER_DAMAGED_PATH = "assets/ship/MainShip_Damaged.png"
PLAYER_VERY_DAMAGED_PATH = "assets/ship/MainShip_VeryDamaged.png"
BULLET_IMAGE_PATH = "assets/weapons/main_ship_rockets.png"
SOUNDTRACK_PATH = "audio/chiphead64-endgame.mp3"

# Config inicial
WIDTH, HEIGHT = 800, 600
FPS = 60 # Afecta velocidad juego tambien
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 128, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Star Shooter - Python Project")
clock = pygame.time.Clock()

# Vars globales
score = 0
high_score = 0
difficulty_level = 1
lives = 3
font = pygame.font.SysFont("Arial", 24)

def load_image(path, default_size=None):
    try:
        img = pygame.image.load(path).convert_alpha()
        if default_size:
            img = pygame.transform.scale(img, default_size)
        return img
    except Exception as e:
        print(f"Error cargando imagen: {path}", e)
        surface = pygame.Surface(default_size or (50, 50), pygame.SRCALPHA)
        pygame.draw.rect(surface, (255, 0, 0), surface.get_rect(), 2)
        return surface

# Cargar imgs
menu_background = load_image(MENU_IMAGE_PATH, (WIDTH, HEIGHT))
game_background = load_image(BACKGROUND_IMAGE_PATH, (WIDTH, HEIGHT))

ship_images = { # nave visual x vida          nº vida x imagen
    4: load_image(PLAYER_FULL_HEALTH_PATH, (50, 50)),
    3: load_image(PLAYER_SLIGHT_DAMAGE_PATH, (50, 50)),
    2: load_image(PLAYER_DAMAGED_PATH, (50, 50)),
    1: load_image(PLAYER_VERY_DAMAGED_PATH, (50, 50))
}

bullet_img = load_image(BULLET_IMAGE_PATH, (50, 75))

def load_soundtrack():
    try:
        pygame.mixer.music.load(SOUNDTRACK_PATH)
        return True
    except Exception as e:
        print(f"Error cargando musica: {SOUNDTRACK_PATH}", e)
        return False

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.images = ship_images
        self.current_health = 3
        self.image = self.images[3]
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 20
        self.speed = 7

    def update(self):
        if self.current_health in self.images:
            self.image = self.images[self.current_health]
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(self.image, RED, (20, 20), 20)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-150, -40)
        self.speedy = random.randint(2 + difficulty_level, 5 + difficulty_level)

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            global score, high_score
            score += 1
            if score > high_score:
                high_score = score
            self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -5

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()


def draw_text(surface, text, size, x, y, color=WHITE):
    font = pygame.font.SysFont("Arial", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

def show_menu():
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False
        
        screen.blit(menu_background, (0, 0))
        draw_text(screen, "STAR SHOOTER", 64, WIDTH//2 - 200, HEIGHT//2 - 100)
        draw_text(screen, f"High Score: {high_score}", 36, WIDTH//2 - 100, HEIGHT//2 - 30)
        draw_text(screen, "Pulsa cualquier tecla para comenzar", 22, WIDTH//2 - 180, HEIGHT//2 + 50)
        pygame.display.flip()

def show_game_over(final_score):
    global high_score
    if final_score > high_score:
        high_score = final_score
    
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False
        
        screen.blit(game_background, (0, 0))
        draw_text(screen, "¡GAME OVER!", 64, WIDTH//2 - 180, HEIGHT//2 - 130, RED)
        draw_text(screen, f"Puntuación final: {final_score}", 36, WIDTH//2 - 150, HEIGHT//2 - 50)
        draw_text(screen, f"High Score: {high_score}", 36, WIDTH//2 - 100, HEIGHT//2)
        draw_text(screen, "Pulsa cualquier tecla para reiniciar", 22, WIDTH//2 - 180, HEIGHT//2 + 50)
        pygame.display.flip()

        

def game_loop():
    global score, difficulty_level, lives, high_score
    score = 0
    difficulty_level = 1
    lives = 4
    
    soundtrack_loaded = load_soundtrack()
    if soundtrack_loaded:
        pygame.mixer.music.play(-1)
    
    all_sprites = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    
    player = Player()
    player.current_health = lives
    all_sprites.add(player)
    
    ADD_ASTEROID = pygame.USEREVENT + 1
    pygame.time.set_timer(ADD_ASTEROID, 1000)
    
    last_difficulty_update = pygame.time.get_ticks()
    
    running = True
    while running:
        clock.tick(FPS)
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == ADD_ASTEROID:
                a = Asteroid()
                all_sprites.add(a)
                asteroids.add(a)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # print("¡Bala disparada!") # Debug
                    bullet = Bullet(player.rect.centerx, player.rect.top)
                    all_sprites.add(bullet)
                    bullets.add(bullet)
        
        if current_time - last_difficulty_update > 15000:
            difficulty_level += 1
            last_difficulty_update = current_time
            asteroid_interval = max(500, 1000 - difficulty_level * 100)
            pygame.time.set_timer(ADD_ASTEROID, asteroid_interval)
        
        all_sprites.update()
        
        hits = pygame.sprite.groupcollide(asteroids, bullets, True, True)
        for hit in hits:
            score += 1
            if score > high_score:
                high_score = score
        
        if pygame.sprite.spritecollide(player, asteroids, True):
            lives -= 1
            player.current_health = lives
            if lives <= 0:
                if soundtrack_loaded:
                    pygame.mixer.music.stop()
                running = False
        
        screen.blit(game_background, (0, 0))
        all_sprites.draw(screen)
        # for bullet in bullets:
            # pygame.draw.rect(screen, (255, 0, 0), bullet.rect, 1)  DEBUG
        
        draw_text(screen, f"Puntuación: {score}", 20, 10, 10)
        draw_text(screen, f"High Score: {high_score}", 20, 10, 40)
        draw_text(screen, f"Nivel: {difficulty_level}", 20, 10, 70)
        draw_text(screen, f"Vidas: {lives}", 20, 10, 100)
        
        pygame.display.flip()
    
    return score

# Bucle principal
while True:
    show_menu()
    final_score = game_loop()
    show_game_over(final_score)
