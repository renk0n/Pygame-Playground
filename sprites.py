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
# 編隊を組む敵 (青い玉)
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

        self.rect.x = WIDTH + offset_x
        self.rect.y = start_y

        self.speed = 6
        self.state = 0
        self.turn_timer = 0
        self.y_direction = y_direction

    def update(self):
        # State 0: 左へ
        if self.state == 0:
            self.rect.x -= self.speed
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

        # 画面外判定
        if self.state == 2 and self.rect.left > WIDTH:
            self.kill()
        elif self.rect.top > HEIGHT or self.rect.bottom < 0:
            self.kill()

# ==========================================
# 追尾する敵 (紫の三角)
# ==========================================


class TrackingEnemy(pygame.sprite.Sprite):
    def __init__(self, start_y, player, offset_x=0):
        super().__init__()
        self.player = player

        size = 30
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        points = [(0, size // 2), (size, 0), (size, size)]
        pygame.draw.polygon(self.image, (255, 0, 255), points)

        self.rect = self.image.get_rect()
        self.rect.x = WIDTH + offset_x
        self.rect.y = start_y

        # 速度設定
        self.dash_speed = 6   # 直進時の速さ
        self.creep_speed = 3  # 斜め移動時の速さ（ゆっくり）

    def update(self):
        dy = self.player.rect.centery - self.rect.centery
        threshold = 5

        # 斜め移動（位置合わせ）はゆっくり
        # 直線移動（攻撃）は速く

        if dy < -threshold:
            # 斜め左上 (45度) - ゆっくり
            self.rect.x -= self.creep_speed * 0.7
            self.rect.y -= self.creep_speed * 0.7
        elif dy > threshold:
            # 斜め左下 (45度) - ゆっくり
            self.rect.x -= self.creep_speed * 0.7
            self.rect.y += self.creep_speed * 0.7
        else:
            # 直進 - 速い！
            self.rect.x -= self.dash_speed

        if self.rect.right < 0:
            self.kill()
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
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
# Stage 2: 山 (平坦に変更)
# ==========================================


class Mountain(pygame.sprite.Sprite):
    def __init__(self, is_top, from_right=True):
        super().__init__()
        # ★変更点: 幅を広く、高さを低くして平坦な印象に
        width = random.randrange(150, 250)
        height = random.randrange(30, 70)

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
