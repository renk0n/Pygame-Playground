import pygame
import sys
from settings import *
from sprites import Player, Enemy


def main():
    # Pygameの初期化
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    # スプライトグループの作成
    all_sprites = pygame.sprite.Group()
    mobs = pygame.sprite.Group()

    # プレイヤーの生成
    player = Player()
    all_sprites.add(player)

    # 敵の生成（とりあえず8体）
    for i in range(8):
        m = Enemy()
        all_sprites.add(m)
        mobs.add(m)

    # ゲームループ
    running = True
    while running:
        # 1. イベント処理
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2. 更新
        all_sprites.update()

        # 3. 描画
        screen.fill(BLACK)
        all_sprites.draw(screen)

        # 画面を更新
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
