import pygame
import random
import math
import os
from settings import *
import sys

# ...他のimport文...

# ここから書き換え
if getattr(sys, 'frozen', False):
    # exe化されたときは、exeファイルがある場所を基準にする
    game_folder = os.path.dirname(sys.executable)
else:
    # 普通に実行するときは、ファイルの場所を基準にする
    game_folder = os.path.dirname(__file__)

img_folder = os.path.join(game_folder, 'images')
# 書き換えここまで
# ==========================================
# 画像読み込み用ヘルパー関数
# ==========================================


def load_image(filename, width, height, color_key=BLACK, flip_x=False):
    """
    imagesフォルダから画像を読み込み、リサイズして返す。
    flip_x=True なら左右反転させる。
    """
    try:
        file_path = os.path.join(img_folder, filename)
        image = pygame.image.load(file_path).convert()
        image = pygame.transform.scale(image, (width, height))

        # 左右反転フラグがあれば反転
        if flip_x:
            image = pygame.transform.flip(image, True, False)

        if color_key is not None:
            image.set_colorkey(color_key)
        return image
    except (FileNotFoundError, pygame.error):
        # 画像がない場合は四角形を返す
        image = pygame.Surface((width, height))
        return image

# ==========================================
# プレイヤー
# ==========================================


class Player(pygame.sprite.Sprite):
    def __init__(self, all_sprites, bullets):
        super().__init__()
        # サイズ: 65x40
        self.width = 65
        self.height = 40
        self.image = load_image("player.png", self.width, self.height)

        try:
            pygame.image.load(os.path.join(img_folder, "player.png"))
        except:
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
        # 弾の発射位置を調整（自機の右端から出るように）
        bullet = Bullet(self.rect.right, self.rect.centery)
        self.all_sprites.add(bullet)
        self.bullets.add(bullet)

# ==========================================
# 普通の敵 (赤)
# ==========================================


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # サイズ: 45x45
        self.image = load_image("enemy.png", 45, 45)
        try:
            pygame.image.load(os.path.join(img_folder, "enemy.png"))
        except:
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
        # サイズ: 45
        size = 45
        self.image = load_image("enemy_ball.png", size, size)
        try:
            pygame.image.load(os.path.join(img_folder, "enemy_ball.png"))
        except:
            pygame.draw.circle(self.image, (0, 255, 255),
                               (size//2, size//2), size//2)
            self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.x = WIDTH + offset_x
        self.rect.y = start_y

        self.speed = 6
        self.state = 0
        self.turn_timer = 0
        self.y_direction = y_direction

    def update(self):
        if self.state == 0:
            self.rect.x -= self.speed
            if self.rect.centerx < (WIDTH // 2) - 100:
                self.state = 1
                self.turn_timer = pygame.time.get_ticks()
        elif self.state == 1:
            self.rect.x += self.speed
            self.rect.y += (self.speed * 0.6) * self.y_direction
            if pygame.time.get_ticks() - self.turn_timer > 500:
                self.state = 2
        elif self.state == 2:
            self.rect.x += self.speed

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
        # サイズ: 45x45
        size = 45
        # 左向きに反転
        self.image = load_image("enemy_track.png", size, size, flip_x=True)

        try:
            pygame.image.load(os.path.join(img_folder, "enemy_track.png"))
        except:
            points = [(0, size // 2), (size, 0), (size, size)]
            pygame.draw.polygon(self.image, (255, 0, 255), points)
            self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.x = WIDTH + offset_x
        self.rect.y = start_y
        self.dash_speed = 6
        self.creep_speed = 3

    def update(self):
        dy = self.player.rect.centery - self.rect.centery
        threshold = 5

        if dy < -threshold:
            self.rect.x -= self.creep_speed * 0.7
            self.rect.y -= self.creep_speed * 0.7
        elif dy > threshold:
            self.rect.x -= self.creep_speed * 0.7
            self.rect.y += self.creep_speed * 0.7
        else:
            self.rect.x -= self.dash_speed

        if self.rect.right < 0:
            self.kill()
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()

# ==========================================
# 固定砲台 (天井)
# ==========================================


class CeilingTurret(pygame.sprite.Sprite):
    def __init__(self, x, y, player, all_sprites, hazards):
        super().__init__()
        # サイズ: 45x45
        self.image = load_image("turret.png", 45, 45)
        try:
            pygame.image.load(os.path.join(img_folder, "turret.png"))
        except:
            self.image.fill(RED)
            pygame.draw.rect(self.image, (200, 0, 0), (10, 15, 10, 15))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.player = player
        self.all_sprites = all_sprites
        self.hazards = hazards

        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 1500
        self.speedx = -3

    def update(self):
        self.rect.x += self.speedx

        if -50 < self.rect.centerx < WIDTH + 50:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shoot_delay:
                self.shoot()
                self.last_shot = now

        if self.rect.right < 0:
            self.kill()

    def shoot(self):
        laser = EnemyLaser(self.rect.centerx, self.rect.bottom, self.player)
        self.all_sprites.add(laser)
        self.hazards.add(laser)

# ==========================================
# 敵の弾 (レーザー) - ★向きに合わせて回転
# ==========================================


class EnemyLaser(pygame.sprite.Sprite):
    def __init__(self, x, y, player):
        super().__init__()
        # サイズ: 30x30。回転の基準となる元の画像を保持。
        self.original_image = load_image("laser.png", 30, 30)
        # 画像がない場合のバックアップ（黄色い四角）
        try:
            pygame.image.load(os.path.join(img_folder, "laser.png"))
        except:
            self.original_image.fill(YELLOW)

        # 初期状態のimageを設定
        self.image = self.original_image.copy()

        # 速度と角度の計算
        speed = 4
        dx = player.rect.centerx - x
        dy = player.rect.centery - y
        # 角度（ラジアン）を計算
        angle = math.atan2(dy, dx)

        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        # --- 画像の回転処理 ---
        # ラジアンを度数法に変換。
        # pygame.transform.rotate は反時計回り。
        # 画像が元々「右向き」だと仮定し、進行方向に向けるためマイナスの角度で回転。
        angle_degrees = math.degrees(angle)
        self.image = pygame.transform.rotate(
            self.original_image, -angle_degrees)

        # 回転すると画像の矩形サイズが変わるので、中心位置を元の発生源に合わせ直す
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

        if (self.rect.right < 0 or self.rect.left > WIDTH or
                self.rect.bottom < 0 or self.rect.top > HEIGHT):
            self.kill()

# ==========================================
# プレイヤーの弾 - ★サイズ3倍
# ==========================================


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # ★サイズ変更: 60x30
        self.image = load_image("bullet.png", 60, 30)
        try:
            pygame.image.load(os.path.join(img_folder, "bullet.png"))
        except:
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
# Stage 2: 平らな地面
# ==========================================


class FlatGround(pygame.sprite.Sprite):
    def __init__(self, x, is_top):
        super().__init__()
        self.width = 50
        self.height = 40
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(BROWN)
        pygame.draw.rect(self.image, (100, 50, 0),
                         (0, 0, self.width, self.height), 1)

        if is_top:
            pygame.draw.line(self.image, GREEN, (0, self.height - 2),
                             (self.width, self.height - 2), 3)
        else:
            pygame.draw.line(self.image, GREEN, (0, 0), (self.width, 0), 3)

        self.rect = self.image.get_rect()
        self.rect.x = x

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
# Stage 2: 山
# ==========================================


class Mountain(pygame.sprite.Sprite):
    def __init__(self, is_top, from_right=True):
        super().__init__()
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

        ground_height = 40
        if is_top:
            self.rect.top = ground_height - 10
        else:
            self.rect.bottom = HEIGHT - ground_height + 10

        self.speedx = -3

    def update(self):
        self.rect.x += self.speedx
        if self.rect.right < 0:
            self.kill()

# ==========================================
# Stage 3: 壁
# ==========================================


class Wall(pygame.sprite.Sprite):
    def __init__(self, is_top, from_right=True, height=80):
        super().__init__()
        width = 100
        self.image = pygame.Surface((width, height))
        self.image.fill(GREY)
        pygame.draw.rect(self.image, WHITE, (0, 0, width, height), 2)
        pygame.draw.line(self.image, DARK_GREY, (20, 0), (20, height), 2)
        pygame.draw.line(self.image, DARK_GREY, (80, 0), (80, height), 2)

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

# ==========================================
# ホッピングする敵
# ==========================================


class HoppingEnemy(pygame.sprite.Sprite):
    def __init__(self, x, player, all_sprites, hazards):
        super().__init__()
        # サイズ: 45x45
        self.image = load_image("hopper.png", 45, 45)
        try:
            pygame.image.load(os.path.join(img_folder, "hopper.png"))
        except:
            self.image.fill((0, 255, 255))

        self.rect = self.image.get_rect()

        self.ground_y = HEIGHT - 40
        self.rect.x = x
        self.rect.bottom = self.ground_y

        self.player = player
        self.all_sprites = all_sprites
        self.hazards = hazards

        self.vy = 0
        self.gravity = 0.8
        self.jump_power = -12

        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = random.randrange(1500, 2500)

        self.scroll_speed = -3
        self.move_speed = 3.5
        self.vx = self.scroll_speed

    def update(self):
        self.vy += self.gravity
        self.rect.y += self.vy

        self.rect.x += self.vx

        if self.rect.bottom >= self.ground_y:
            self.rect.bottom = self.ground_y
            self.vy = self.jump_power

            dist_x = self.player.rect.centerx - self.rect.centerx
            if abs(dist_x) < 40:
                current_rel_speed = self.vx - self.scroll_speed
                if current_rel_speed > 0:
                    self.vx = self.scroll_speed - self.move_speed
                else:
                    self.vx = self.scroll_speed + self.move_speed
            else:
                if dist_x > 0:
                    self.vx = self.scroll_speed + self.move_speed
                else:
                    self.vx = self.scroll_speed - self.move_speed

        if self.rect.right < -100 or self.rect.left > WIDTH + 100:
            if self.rect.right < -100:
                self.kill()

        if 0 < self.rect.centerx < WIDTH:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shoot_delay:
                self.shoot()
                self.last_shot = now
                self.shoot_delay = random.randrange(1500, 2500)

    def shoot(self):
        laser = EnemyLaser(self.rect.centerx, self.rect.top, self.player)
        self.all_sprites.add(laser)
        self.hazards.add(laser)

# ==========================================
# 波線で進む飛行機 (オレンジ)
# ==========================================


class WaveEnemy(pygame.sprite.Sprite):
    def __init__(self, offset_x, base_y):
        super().__init__()
        # サイズ: 60x45, 左向き
        self.image = load_image("enemy_wave.png", 60, 45, flip_x=True)
        try:
            pygame.image.load(os.path.join(img_folder, "enemy_wave.png"))
        except:
            points = [(0, 15), (40, 0), (40, 30)]
            pygame.draw.polygon(self.image, (255, 165, 0), points)
            self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.x = WIDTH + offset_x

        self.base_y = base_y
        self.rect.centery = base_y

        self.speed = 5
        self.theta = 0
        self.amplitude = 80
        self.frequency = 0.05

    def update(self):
        self.rect.x -= self.speed

        self.theta += self.frequency
        self.rect.centery = self.base_y + math.sin(self.theta) * self.amplitude

        if self.rect.right < 0:
            self.kill()

# ==========================================
# タワーから出てくる敵 (90度回転)
# ==========================================


class TowerEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # サイズ: 20x32
        self.image = load_image("enemy_small.png", 20, 32)
        # 画像を90度左に回転
        self.image = pygame.transform.rotate(self.image, 90)

        try:
            pygame.image.load(os.path.join(img_folder, "enemy_small.png"))
        except:
            self.image.fill((255, 50, 50))

        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.centery = y
        self.speedx = -5

    def update(self):
        self.rect.x += self.speedx
        if self.rect.right < 0:
            self.kill()

# ==========================================
# 敵が出てくる鉄塔
# ==========================================


class EnemyTower(pygame.sprite.Sprite):
    def __init__(self, x, is_top, all_sprites, mobs):
        super().__init__()
        self.image = load_image("tower.png", 40, 60)
        try:
            pygame.image.load(os.path.join(img_folder, "tower.png"))
        except:
            self.image.fill(GREY)
            pygame.draw.rect(self.image, (50, 50, 50), (5, 5, 30, 20))
            pygame.draw.line(self.image, DARK_GREY, (0, 0), (40, 60), 2)
            pygame.draw.line(self.image, DARK_GREY, (40, 0), (0, 60), 2)

        self.rect = self.image.get_rect()
        self.rect.x = x

        if is_top:
            self.rect.top = 80
            self.spawn_y = self.rect.bottom - 10
        else:
            self.rect.bottom = HEIGHT - 80
            self.spawn_y = self.rect.top + 15

        self.hp = 5
        self.all_sprites = all_sprites
        self.mobs = mobs
        self.scroll_speed = -3

        self.is_spawning = False
        self.spawn_count = 0
        self.spawn_timer = 0
        self.cooldown_timer = 0
        self.cooldown_delay = 2000

    def update(self):
        self.rect.x += self.scroll_speed

        if 0 < self.rect.right < WIDTH:
            now = pygame.time.get_ticks()
            if not self.is_spawning:
                if now - self.cooldown_timer > self.cooldown_delay:
                    self.is_spawning = True
                    self.spawn_enemy()
                    self.spawn_count = 1
                    self.spawn_timer = now
            else:
                if now - self.spawn_timer > 400:
                    self.spawn_enemy()
                    self.spawn_timer = now
                    self.spawn_count += 1
                    if self.spawn_count >= 4:
                        self.is_spawning = False
                        self.cooldown_timer = now

        if self.rect.right < 0:
            self.kill()

    def spawn_enemy(self):
        enemy = TowerEnemy(self.rect.centerx, self.spawn_y)
        self.all_sprites.add(enemy)
        self.mobs.add(enemy)

# ==========================================
# ステージボス: ビッグ・コア
# ==========================================


class Boss(pygame.sprite.Sprite):
    def __init__(self, all_sprites, hazards, player):
        super().__init__()
        # サイズ: 220x120
        self.image = load_image("boss.png", 220, 120)
        try:
            pygame.image.load(os.path.join(img_folder, "boss.png"))
        except:
            self.image = pygame.Surface((60, 100))
            self.image.fill(GREY)
            pygame.draw.circle(self.image, (0, 0, 255), (30, 50), 15)
            pygame.draw.circle(self.image, (255, 255, 255), (30, 50), 5)
            pygame.draw.rect(self.image, DARK_GREY, (0, 0, 60, 20))
            pygame.draw.rect(self.image, DARK_GREY, (0, 80, 60, 20))

        self.rect = self.image.get_rect()
        self.rect.x = WIDTH + 50
        self.rect.centery = HEIGHT // 2

        self.all_sprites = all_sprites
        self.hazards = hazards
        self.player = player

        self.hp = 80
        self.max_hp = 80
        self.state = 'entry'
        self.speedy = 2
        self.last_shot = 0
        self.shoot_delay = 1200

    def update(self):
        if self.state == 'entry':
            self.rect.x -= 2
            if self.rect.right < WIDTH - 50:
                self.rect.right = WIDTH - 50
                self.state = 'battle'

        elif self.state == 'battle':
            self.rect.y += self.speedy
            if self.rect.top < 40 or self.rect.bottom > HEIGHT - 40:
                self.speedy *= -1

            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shoot_delay:
                self.shoot()
                self.last_shot = now

        if self.hp < self.max_hp * 0.3:
            try:
                pygame.image.load(os.path.join(img_folder, "boss.png"))
            except:
                pygame.draw.circle(self.image, (255, 0, 0), (30, 50), 15)

    def shoot(self):
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        base_angle = math.atan2(dy, dx)
        offsets = [-0.3, 0, 0.3]
        for offset in offsets:
            angle = base_angle + offset
            vx = math.cos(angle) * 5
            vy = math.sin(angle) * 5
            bullet = EnemyLaser(self.rect.left, self.rect.centery, self.player)
            bullet.vx = vx
            bullet.vy = vy
            self.all_sprites.add(bullet)
            self.hazards.add(bullet)
