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
# 普通の敵
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
        size = 30
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        points = [(0, size // 2), (size, 0), (size, size)]
        pygame.draw.polygon(self.image, (255, 0, 255), points)
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
    def __init__(self, x, player, all_sprites, hazards):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        pygame.draw.rect(self.image, (200, 0, 0), (10, 15, 10, 15))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.top = 40

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
# 敵の弾 (レーザー)
# ==========================================


class EnemyLaser(pygame.sprite.Sprite):
    def __init__(self, x, y, player):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        speed = 4

        dx = player.rect.centerx - x
        dy = player.rect.centery - y
        angle = math.atan2(dy, dx)

        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

        if (self.rect.right < 0 or self.rect.left > WIDTH or
                self.rect.bottom < 0 or self.rect.top > HEIGHT):
            self.kill()

# ==========================================
# プレイヤーの弾
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
            pygame.draw.line(self.image, GREEN, (0, self.height-2),
                             (self.width, self.height-2), 3)
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

# ==========================================
# ホッピングする敵 (AI強化版)
# ==========================================


class HoppingEnemy(pygame.sprite.Sprite):
    def __init__(self, x, player, all_sprites, hazards):
        super().__init__()
        self.image = pygame.Surface((30, 30))
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

        self.scroll_speed = -3   # 背景スクロール速度
        self.move_speed = 3.5    # 敵自身の移動速度
        self.vx = self.scroll_speed  # 初期速度

    def update(self):
        self.vy += self.gravity
        self.rect.y += self.vy

        self.rect.x += self.vx

        # 着地判定
        if self.rect.bottom >= self.ground_y:
            self.rect.bottom = self.ground_y
            self.vy = self.jump_power

            # AI: プレイヤーの位置に応じて動きを変える
            dist_x = self.player.rect.centerx - self.rect.centerx
            if abs(dist_x) < 40:
                # またぐ動き
                current_rel_speed = self.vx - self.scroll_speed
                if current_rel_speed > 0:
                    self.vx = self.scroll_speed - self.move_speed
                else:
                    self.vx = self.scroll_speed + self.move_speed
            else:
                # 接近
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
# ★波線で進む飛行機
# ==========================================


class WaveEnemy(pygame.sprite.Sprite):
    def __init__(self, offset_x, start_y):
        super().__init__()
        # オレンジ色の三角形
        self.image = pygame.Surface((40, 30), pygame.SRCALPHA)
        points = [(0, 15), (40, 0), (40, 30)]  # 左向きの三角
        pygame.draw.polygon(self.image, (255, 165, 0), points)  # Orange

        self.rect = self.image.get_rect()
        self.rect.x = WIDTH + offset_x

        self.base_y = start_y  # 基準となるY座標
        self.rect.centery = start_y

        self.speed = 5
        self.theta = 0  # 角度
        self.amplitude = 80  # 振幅 (波の大きさ)
        self.frequency = 0.05  # 周波数 (波の細かさ)

    def update(self):
        self.rect.x -= self.speed

        # サイン波でY座標を計算
        self.theta += self.frequency
        self.rect.centery = self.base_y + math.sin(self.theta) * self.amplitude

        if self.rect.right < 0:
            self.kill()
# (既存のimportsの下、ファイルの末尾に追加)

# ==========================================
# ★タワーから出てくる敵
# ==========================================


class TowerEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # 小さな赤い四角
        self.image = pygame.Surface((20, 20))
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
# ★敵が出てくる鉄塔 (修正版)
# ==========================================


class EnemyTower(pygame.sprite.Sprite):
    def __init__(self, x, is_top, all_sprites, mobs):
        super().__init__()
        self.image = pygame.Surface((40, 60))
        self.image.fill(GREY)
        # ハッチ（出口）を描画
        pygame.draw.rect(self.image, (50, 50, 50), (5, 5, 30, 20))
        # 鉄骨のような模様
        pygame.draw.line(self.image, DARK_GREY, (0, 0), (40, 60), 2)
        pygame.draw.line(self.image, DARK_GREY, (40, 0), (0, 60), 2)

        self.rect = self.image.get_rect()
        self.rect.x = x

        # ステージ3の壁(高さ80)に合わせて配置
        if is_top:
            self.rect.top = 80
            self.spawn_y = self.rect.bottom - 10
        else:
            self.rect.bottom = HEIGHT - 80
            self.spawn_y = self.rect.top + 15

        self.hp = 5  # 耐久力
        self.all_sprites = all_sprites
        self.mobs = mobs

        self.scroll_speed = -3

        # 生成ロジック用変数
        self.is_spawning = False
        self.spawn_count = 0
        self.spawn_timer = 0

        # ★変更点1: 初期値を0にして、画面に入ったら即発射可能にする
        self.cooldown_timer = 0
        # ★変更点2: 次のウェーブまでの時間を短縮 (3秒 -> 2秒)
        self.cooldown_delay = 2000

    def update(self):
        self.rect.x += self.scroll_speed

        # 画面内に完全に入ったら動作開始
        if 0 < self.rect.right < WIDTH:
            now = pygame.time.get_ticks()

            # 待機状態 -> 生成開始
            if not self.is_spawning:
                if now - self.cooldown_timer > self.cooldown_delay:
                    self.is_spawning = True
                    # ★変更点3: 生成開始と同時に1体目を即座に出す
                    self.spawn_enemy()
                    self.spawn_count = 1
                    self.spawn_timer = now

            # 生成中 (残り3体)
            else:
                if now - self.spawn_timer > 150:  # 0.15秒間隔で連射
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
# (既存のimportsの下、ファイルの末尾に追加)

# ==========================================
# ★ステージボス: ビッグ・コア
# ==========================================


class Boss(pygame.sprite.Sprite):
    def __init__(self, all_sprites, hazards, player):
        super().__init__()
        # 巨大なボディ (青とグレー)
        self.image = pygame.Surface((60, 100))
        self.image.fill(GREY)
        # コア部分 (弱点)
        pygame.draw.circle(self.image, (0, 0, 255), (30, 50), 15)  # 青いコア
        pygame.draw.circle(self.image, (255, 255, 255), (30, 50), 5)  # 光沢
        # 上下のウィング
        pygame.draw.rect(self.image, DARK_GREY, (0, 0, 60, 20))
        pygame.draw.rect(self.image, DARK_GREY, (0, 80, 60, 20))

        self.rect = self.image.get_rect()
        self.rect.x = WIDTH + 50  # 画面外からスタート
        self.rect.centery = HEIGHT // 2

        self.all_sprites = all_sprites
        self.hazards = hazards
        self.player = player

        self.hp = 80  # 耐久力 (かなり硬い)
        self.max_hp = 80

        # 状態管理 ('entry': 入場中, 'battle': 戦闘中)
        self.state = 'entry'

        self.speedy = 2
        self.last_shot = 0
        self.shoot_delay = 1200  # 1.2秒ごとに攻撃

    def update(self):
        # ■ 入場フェーズ
        if self.state == 'entry':
            self.rect.x -= 2
            # 画面の右側定位置に来たら止まる
            if self.rect.right < WIDTH - 50:
                self.rect.right = WIDTH - 50
                self.state = 'battle'

        # ■ 戦闘フェーズ
        elif self.state == 'battle':
            # 上下移動
            self.rect.y += self.speedy
            if self.rect.top < 40 or self.rect.bottom > HEIGHT - 40:
                self.speedy *= -1  # 端に当たったら反転

            # 攻撃
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shoot_delay:
                self.shoot()
                self.last_shot = now

        # HPバーの描画 (ボスの頭上に表示)
        # ※実際の描画は本来drawで行うが、簡易的にimageを毎フレーム更新するか、
        # あるいはmain側で描画するのが綺麗だが、ここでは簡易化のため省略し、
        # 色の変化でダメージを表現する
        if self.hp < self.max_hp * 0.3:  # ピンチになると赤くなる
            pygame.draw.circle(self.image, (255, 0, 0), (30, 50), 15)
        else:
            pygame.draw.circle(self.image, (0, 0, 255), (30, 50), 15)

    def shoot(self):
        # プレイヤーへ向けた3方向弾
        # プレイヤーへの角度を計算
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        base_angle = math.atan2(dy, dx)

        offsets = [-0.3, 0, 0.3]  # 3方向の角度ずれ

        for offset in offsets:
            angle = base_angle + offset
            vx = math.cos(angle) * 5
            vy = math.sin(angle) * 5
            bullet = EnemyLaser(self.rect.left, self.rect.centery, self.player)
            # 速度を上書き
            bullet.vx = vx
            bullet.vy = vy
            self.all_sprites.add(bullet)
            self.hazards.add(bullet)
