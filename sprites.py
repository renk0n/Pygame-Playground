import pygame
import random
from settings import *

# ==========================================
# プレイヤー
# ==========================================


class Player(pygame.sprite.Sprite):
    def __init__(self, all_sprites, bullets):
        super().__init__()
        self.image = pygame.Surface((50, 30))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centery = HEIGHT // 2
        self.rect.left = 50
        self.speedx = 0
        self.speedy = 0
        self.all_sprites = all_sprites
        self.bullets = bullets

    def update(self):
        self.speedx = 0
        self.speedy = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.speedx = -PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.speedx = PLAYER_SPEED
        if keys[pygame.K_UP]:
            self.speedy = -PLAYER_SPEED
        if keys[pygame.K_DOWN]:
            self.speedy = PLAYER_SPEED

        if self.speedx != 0 and self.speedy != 0:
            self.speedx *= 0.7071
            self.speedy *= 0.7071

        self.rect.x += self.speedx
        self.rect.y += self.speedy

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0

    def shoot(self):
        bullet = Bullet(self.rect.right, self.rect.centery)
        self.all_sprites.add(bullet)
        self.bullets.add(bullet)

# ==========================================
# 敵
# ==========================================


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        # 敵は常に画面右外から出現させる
        self.rect.x = random.randrange(WIDTH + 10, WIDTH + 100)
        self.rect.y = random.randrange(50, HEIGHT - 50)
        self.speedx = random.randrange(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)

    def update(self):
        self.rect.x -= self.speedx
        # 画面左に消えたら削除してメモリ節約（再利用しない）
        if self.rect.right < 0:
            self.kill()

# ==========================================
# 弾
# ==========================================


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.centery = y
        self.speedx = 10

    def update(self):
        self.rect.x += self.speedx
        if self.rect.left > WIDTH:
            self.kill()

# ==========================================
# 背景の星
# ==========================================


class Star(pygame.sprite.Sprite):
    def __init__(self, from_right=False):
        super().__init__()
        self.size = random.randrange(1, 4)
        self.image = pygame.Surface((self.size, self.size))
        brightness = random.randrange(100, 255)
        self.image.fill((brightness, brightness, brightness))
        self.rect = self.image.get_rect()

        if from_right:
            # ゲーム中は右端から生まれる
            self.rect.x = WIDTH + random.randrange(0, 50)
        else:
            # ゲーム開始時は画面全体に散らばる
            self.rect.x = random.randrange(WIDTH)

        self.rect.y = random.randrange(HEIGHT)
        self.speedx = -(self.size * 1.5)

    def update(self):
        self.rect.x += self.speedx
        if self.rect.right < 0:
            self.kill()  # 画面外に出たら消す

# ==========================================
# Stage 2: 山
# ==========================================


class Mountain(pygame.sprite.Sprite):
    def __init__(self, is_top, from_right=True):
        super().__init__()
        width = random.randrange(80, 150)
        height = random.randrange(50, 120)
        self.image = pygame.Surface((width, height))
        self.image.set_colorkey(BLACK)

        points = [(0, height), (width // 2, 0), (width, height)]
        if is_top:
            points = [(0, 0), (width // 2, height), (width, 0)]

        pygame.draw.polygon(self.image, BROWN, points)

        self.rect = self.image.get_rect()

        if from_right:
            self.rect.x = WIDTH + random.randrange(0, 50)
        else:
            self.rect.x = random.randrange(0, WIDTH)

        if is_top:
            self.rect.top = 0
        else:
            self.rect.bottom = HEIGHT

        self.speedx = -3  # 背景スクロール速度

    def update(self):
        self.rect.x += self.speedx
        if self.rect.right < 0:
            self.kill()

# ==========================================
# Stage 3: 壁
# ==========================================


class Wall(pygame.sprite.Sprite):
    def __init__(self, is_top, from_right=True):
        super().__init__()
        width = 100
        height = 80
        self.image = pygame.Surface((width, height))
        self.image.fill(GREY)
        pygame.draw.rect(self.image, WHITE, (0, 0, width, height), 2)
        pygame.draw.line(self.image, DARK_GREY, (20, 0), (20, height), 2)

        self.rect = self.image.get_rect()

        if from_right:
            self.rect.x = WIDTH
        else:
            self.rect.x = random.randrange(0, WIDTH)

        if is_top:
            self.rect.top = 0
        else:
            self.rect.bottom = HEIGHT

        self.speedx = -3

    def update(self):
        self.rect.x += self.speedx
        if self.rect.right < 0:
            self.kill()
