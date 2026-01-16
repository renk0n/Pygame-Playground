# sprites.py
import pygame
import random
from settings import *

# ==========================================
# プレイヤー（自機）クラス：横向き、8方向移動
# ==========================================


class Player(pygame.sprite.Sprite):
    def __init__(self, all_sprites, bullets):
        super().__init__()
        # 横向きの自機（とりあえず横長の緑）
        self.image = pygame.Surface((50, 30))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        # 初期位置：画面左の中央寄り
        self.rect.centery = HEIGHT // 2
        self.rect.left = 50
        self.speedx = 0
        self.speedy = 0
        self.all_sprites = all_sprites
        self.bullets = bullets

    def update(self):
        # 8方向移動の入力受付
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

        # 斜め移動の速度補正（任意だが、あると自然）
        if self.speedx != 0 and self.speedy != 0:
            self.speedx *= 0.7071  # 1/√2
            self.speedy *= 0.7071

        # 移動反映
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        # 画面外に出ないように制限（上下左右）
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0

    def shoot(self):
        # 弾を右に向かって発射
        bullet = Bullet(self.rect.right, self.rect.centery)
        self.all_sprites.add(bullet)
        self.bullets.add(bullet)

# ==========================================
# 敵クラス：右から左へ流れてくる
# ==========================================


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        # 画面の右外側に出現
        self.rect.x = random.randrange(WIDTH + 10, WIDTH + 100)
        self.rect.y = random.randrange(0, HEIGHT - self.rect.height)
        # 左に向かう速度設定
        self.speedx = random.randrange(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)

    def update(self):
        # 左へ移動
        self.rect.x -= self.speedx
        # 画面左端へ消えたら、右外側に戻す（再利用）
        if self.rect.right < 0:
            self.rect.x = random.randrange(WIDTH + 10, WIDTH + 100)
            self.rect.y = random.randrange(0, HEIGHT - self.rect.height)
            self.speedx = random.randrange(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)

# ==========================================
# 弾クラス：右へ飛ぶ
# ==========================================


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # 横長の弾
        self.image = pygame.Surface((20, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.centery = y
        self.speedx = 10  # 右に向かって進む速度

    def update(self):
        self.rect.x += self.speedx
        # 画面右端を超えたら消す
        if self.rect.left > WIDTH:
            self.kill()
