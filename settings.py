import pygame

# 画面設定
WIDTH = 800
HEIGHT = 600
FPS = 60
TITLE = "Space Shooter"

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
GREY = (100, 100, 100)
DARK_GREY = (50, 50, 50)

# プレイヤー設定
PLAYER_SPEED = 5

# 敵の設定
ENEMY_SPEED_MIN = 3
ENEMY_SPEED_MAX = 8

# ステージ進行のスコア基準（長くしました）
SCORE_STAGE2 = 1500   # 1500点で山が見え始める
SCORE_STAGE3 = 3500   # 3500点で基地に入り始める
