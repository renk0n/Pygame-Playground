import pygame
import random
import math
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
# 普通の敵 (クラス定義のみ保持)
# ==========================================


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH + 10, WIDTH + 100)
        self.rect.y = random.randrange(50, HEIGHT - 50)
        self.speedx = random.randrange(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)

    def update(self):
        self.rect.x -= self.speedx
        if self.rect.right < 0:
            self.kill()

# ==========================================
# ★編隊を組む敵 (玉)
# ==========================================


class FormationEnemy(pygame.sprite.Sprite):
    def __init__(self, offset_x, start_y, y_direction):
        super().__init__()
        self.radius = 15
        self.image = pygame.Surface(
            (self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 255, 255),
                           (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect()

        # スタート位置
        self.rect.x = WIDTH + offset_x
        self.rect.y = start_y

        self.speed = 6
        self.state = 0
        self.turn_timer = 0
        self.y_direction = y_direction

    def update(self):
        # State 0: 左へ進む
        if self.state == 0:
            self.rect.x -= self.speed
            # 画面中央より少し奥で折り返し
            if self.rect.centerx < (WIDTH // 2) - 100:
                self.state = 1
                self.turn_timer = pygame.time.get_ticks()

        # State 1: 斜めへ折り返す
        elif self.state == 1:
            self.rect.x += self.speed
            self.rect.y += (self.speed * 0.6) * self.y_direction

            if pygame.time.get_ticks() - self.turn_timer > 500:
                self.state = 2

        # State 2: そのまま右へ抜ける
        elif self.state == 2:
            self.rect.x += self.speed

        # --- 修正箇所: 画面外判定のロジック変更 ---
        # 「右へ帰っていく時(state 2)」だけ、画面右外に出たら消す
        # そうしないと、登場時(state 0)に画面右外にいる後続の敵が消されてしまう
        if self.state == 2 and self.rect.left > WIDTH:
            self.kill()

        # 上下の画面外判定はいつでも有効
        elif self.rect.top > HEIGHT or self.rect.bottom < 0:
            self.kill()

        # (左端の判定は入れていませんが、この敵は左へ抜け切ることはないので不要です)

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
            self.rect.x = WIDTH + random.randrange(0, 50)
        else:
            self.rect.x = random.randrange(WIDTH)

        self.rect.y = random.randrange(HEIGHT)
        self.speedx = -(self.size * 1.5)

    def update(self):
        self.rect.x += self.speedx
        if self.rect.right < 0:
            self.kill()

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

        self.speedx = -3

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
