import pygame
import random
import sys

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Survival")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 28)

# --- Cargar recursos ---
player_img = pygame.image.load("assets/player.png")
enemy_img = pygame.image.load("assets/enemy.png")
bullet_img = pygame.image.load("assets/bullet.png")
explosion_img = pygame.image.load("assets/explosion.png")

shoot_sound = pygame.mixer.Sound("assets/shoot.wav")
explosion_sound = pygame.mixer.Sound("assets/explosion.wav")

pygame.mixer.music.load("assets/music.ogg")
pygame.mixer.music.play(-1)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# --- Fondo animado ---
stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT)] for _ in range(80)]

def draw_stars():
    for star in stars:
        pygame.draw.circle(screen, WHITE, star, 2)
        star[1] += 2
        if star[1] > HEIGHT:
            star[0] = random.randint(0, WIDTH)
            star[1] = 0


# --- Clases ---

class Player:
    def __init__(self):
        self.image = player_img
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT-60))
        self.speed = 7
        self.lives = 3

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def draw(self):
        screen.blit(self.image, self.rect)


class Bullet:
    def __init__(self, x, y):
        self.image = bullet_img
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10

    def update(self):
        self.rect.y -= self.speed

    def draw(self):
        screen.blit(self.image, self.rect)


class Enemy:
    def __init__(self):
        self.image = enemy_img
        self.rect = self.image.get_rect(
            center=(random.randint(40, WIDTH-40), -40))
        self.speed = random.randint(2, 5)

    def update(self):
        self.rect.y += self.speed

    def draw(self):
        screen.blit(self.image, self.rect)


class Explosion:
    def __init__(self, x, y):
        self.image = explosion_img
        self.rect = self.image.get_rect(center=(x, y))
        self.timer = 20

    def update(self):
        self.timer -= 1

    def draw(self):
        screen.blit(self.image, self.rect)


# --- Funciones ---

def draw_text(text, x, y):
    img = font.render(text, True, WHITE)
    screen.blit(img, (x, y))


def menu():
    while True:
        screen.fill(BLACK)
        draw_stars()

        draw_text("SPACE SURVIVAL", WIDTH//2 - 120, HEIGHT//2 - 60)
        draw_text("ENTER para jugar", WIDTH//2 - 110, HEIGHT//2)
        draw_text("ESC para salir", WIDTH//2 - 90, HEIGHT//2 + 40)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
                if event.key == pygame.K_ESCAPE:
                    sys.exit()


def game_over(score):
    pygame.mixer.music.stop()

    while True:
        screen.fill(BLACK)
        draw_text("GAME OVER", WIDTH//2 - 90, HEIGHT//2 - 60)
        draw_text(f"Puntaje: {score}", WIDTH//2 - 80, HEIGHT//2)
        draw_text("ENTER para reiniciar", WIDTH//2 - 130, HEIGHT//2 + 40)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    pygame.mixer.music.play(-1)
                    return


def game():
    player = Player()
    bullets = []
    enemies = []
    explosions = []
    score = 0
    spawn_timer = 0

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullets.append(Bullet(player.rect.centerx, player.rect.top))
                    shoot_sound.play()

        keys = pygame.key.get_pressed()
        player.move(keys)

        # Balas
        for bullet in bullets[:]:
            bullet.update()
            if bullet.rect.bottom < 0:
                bullets.remove(bullet)

        # Generar enemigos
        spawn_timer += 1
        if spawn_timer > 30:
            enemies.append(Enemy())
            spawn_timer = 0

        # Enemigos
        for enemy in enemies[:]:
            enemy.update()

            if enemy.rect.top > HEIGHT:
                enemies.remove(enemy)
                player.lives -= 1

            # Colisión con jugador
            if enemy.rect.colliderect(player.rect):
                explosion_sound.play()
                explosions.append(Explosion(player.rect.centerx, player.rect.centery))
                return score

            # Colisión con balas
            for bullet in bullets[:]:
                if enemy.rect.colliderect(bullet.rect):
                    explosion_sound.play()
                    explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery))
                    enemies.remove(enemy)
                    bullets.remove(bullet)
                    score += 10
                    break

        # Explosiones
        for exp in explosions[:]:
            exp.update()
            if exp.timer <= 0:
                explosions.remove(exp)

        if player.lives <= 0:
            return score

        # Dibujar
        screen.fill(BLACK)
        draw_stars()

        player.draw()

        for bullet in bullets:
            bullet.draw()

        for enemy in enemies:
            enemy.draw()

        for exp in explosions:
            exp.draw()

        draw_text(f"Puntaje: {score}", 10, 10)
        draw_text(f"Vidas: {player.lives}", WIDTH - 120, 10)

        pygame.display.flip()


# --- Bucle principal ---

while True:
    menu()
    score = game()
    game_over(score)
