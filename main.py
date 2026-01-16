import pygame
import sys
from settings import *
from sprites import Player, Enemy, Bullet

# 文字を描画するための便利な関数


def draw_text(screen, text, size, x, y, color=WHITE):
    # フォントの種類（あればarial、なければデフォルト）
    font_name = pygame.font.match_font('arial')
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    screen.blit(text_surface, text_rect)

# スタート画面（オープニング）を表示する関数


def show_start_screen(screen):
    screen.fill(BLACK)

    # 1. Konamiロゴ風
    draw_text(screen, "Konami", 30, WIDTH // 2, HEIGHT // 6, WHITE)

    # 2. タイトルロゴ "GRADIUS" 風
    # 本物はロゴ画像ですが、ここでは文字と枠で再現します
    # 赤っぽい影
    draw_text(screen, "GRADIUS", 80, WIDTH //
              2 + 4, HEIGHT // 4 + 4, (200, 0, 0))
    # 青っぽい本体
    draw_text(screen, "GRADIUS", 80, WIDTH // 2, HEIGHT // 4, (0, 100, 255))

    # 3. コピーライト
    draw_text(screen, "(c) KONAMI 1986", 20, WIDTH // 2, HEIGHT // 2, WHITE)

    # 4. ハイスコア
    draw_text(screen, "HI  0050000", 25, WIDTH //
              2, HEIGHT // 2 + 40, (255, 100, 100))

    # 5. メニュー
    draw_text(screen, "1 PLAYER", 30, WIDTH // 2, HEIGHT * 3 / 4, WHITE)
    draw_text(screen, "2 PLAYERS", 30, WIDTH // 2, HEIGHT *
              3 / 4 + 40, (150, 150, 150))  # 選択不可っぽく灰色に

    # カーソル（自機っぽい三角形）を 1 PLAYER の横に描く
    # 三角形の座標: (x1, y1), (x2, y2), (x3, y3)
    cursor_x = WIDTH // 2 - 100
    cursor_y = HEIGHT * 3 / 4 + 10
    pygame.draw.polygon(screen, WHITE, [
        (cursor_x, cursor_y),
        (cursor_x, cursor_y + 20),
        (cursor_x + 20, cursor_y + 10)
    ])

    pygame.display.flip()

    # キー入力待ち
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                # 何かキーを離したらゲーム開始（誤作動防止でKEYUP推奨）
                # 今回はSPACEキーかENTERキーで開始にします
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    waiting = False


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    # ゲームループ全体のフラグ
    game_running = True

    while game_running:
        # ★ここでスタート画面を表示して待機★
        show_start_screen(screen)

        # --- ゲーム本編の準備 ---
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()

        player = Player(all_sprites, bullets)
        all_sprites.add(player)

        def new_mob():
            m = Enemy()
            all_sprites.add(m)
            mobs.add(m)

        for i in range(8):
            new_mob()

        # --- ゲームプレイ中のループ ---
        run_level = True
        while run_level:
            clock.tick(FPS)

            # イベント処理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run_level = False
                    game_running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        player.shoot()

            # 更新
            all_sprites.update()

            # 当たり判定：弾 -> 敵
            hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
            for hit in hits:
                new_mob()

            # 当たり判定：敵 -> プレイヤー
            hits = pygame.sprite.spritecollide(player, mobs, False)
            if hits:
                # 死んだらループを抜けてタイトルに戻る
                run_level = False

            # 描画
            screen.fill(BLACK)
            all_sprites.draw(screen)

            # 画面上部にスコアなどを描くならここ
            # draw_text(screen, "SCORE: 0", 18, WIDTH / 2, 10, WHITE)

            pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
