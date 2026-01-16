import pygame
import random
from settings import *

# ==========================================
# プレイヤー（自機）クラス
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
# 敵クラス
# ==========================================


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH + 10, WIDTH + 100)
        self.rect.y = random.randrange(0, HEIGHT - self.rect.height)
        self.speedx = random.randrange(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)

    def update(self):
        self.rect.x -= self.speedx
        if self.rect.right < 0:
            self.rect.x = random.randrange(WIDTH + 10, WIDTH + 100)
            self.rect.y = random.randrange(0, HEIGHT - self.rect.height)
            self.speedx = random.randrange(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)

# ==========================================
# 弾クラス
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
# ★背景の星クラス（新規追加）
# ==========================================


class Star(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # 星の大きさ（1〜3ピクセル）
        self.size = random.randrange(1, 4)
        self.image = pygame.Surface((self.size, self.size))

        # 明るさをランダムに（真っ白〜少し暗いグレー）
        brightness = random.randrange(100, 255)
        self.image.fill((brightness, brightness, brightness))

        self.rect = self.image.get_rect()
        # 初期位置は画面内のどこか
        self.rect.x = random.randrange(WIDTH)
        self.rect.y = random.randrange(HEIGHT)

        # 移動速度（大きい星ほど速く動かす＝遠近感）
        self.speedx = -(self.size * 1.5)

    def update(self):
        self.rect.x += self.speedx
        # 画面左端に消えたら右端に戻す
        if self.rect.right < 0:
            self.rect.left = WIDTH
            self.rect.y = random.randrange(HEIGHT)
