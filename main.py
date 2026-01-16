import pygame
import sys
from settings import *
from sprites import Player, Enemy, Bullet


def draw_text(screen, text, size, x, y, color=WHITE):
    font_name = pygame.font.match_font('arial')
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    screen.blit(text_surface, text_rect)

# スタート画面関数（戻り値で選んだモードを返すように変更）


def show_start_screen(screen):
    # メニューの選択状態（0: 1P, 1: 2P）
    selected_index = 0

    waiting = True
    while waiting:
        screen.fill(BLACK)

        # --- タイトル描画 ---
        draw_text(screen, "Konami", 30, WIDTH // 2, HEIGHT // 6, WHITE)
        draw_text(screen, "GRADIUS", 80, WIDTH //
                  2 + 4, HEIGHT // 4 + 4, (200, 0, 0))
        draw_text(screen, "GRADIUS", 80, WIDTH //
                  2, HEIGHT // 4, (0, 100, 255))
        draw_text(screen, "(c) KONAMI 1986", 20,
                  WIDTH // 2, HEIGHT // 2, WHITE)
        draw_text(screen, "HI  0050000", 25, WIDTH //
                  2, HEIGHT // 2 + 40, (255, 100, 100))

        # --- メニュー項目描画 ---
        # 選ばれている方は白、選ばれていない方は灰色にする演出
        color_1p = WHITE if selected_index == 0 else (100, 100, 100)
        color_2p = WHITE if selected_index == 1 else (100, 100, 100)

        draw_text(screen, "1 PLAYER", 30, WIDTH // 2, HEIGHT * 3 / 4, color_1p)
        draw_text(screen, "2 PLAYERS", 30, WIDTH //
                  2, HEIGHT * 3 / 4 + 40, color_2p)

        # --- 矢印（カーソル）の描画 ---
        # 基準となるY座標（1 PLAYERの横）
        base_y = HEIGHT * 3 / 4 + 10
        # 2 PLAYERなら 40px 下にずらす
        cursor_y = base_y + (40 * selected_index)

        cursor_x = WIDTH // 2 - 100

        # 三角形を描く
        pygame.draw.polygon(screen, WHITE, [
            (cursor_x, cursor_y),
            (cursor_x, cursor_y + 20),
            (cursor_x + 20, cursor_y + 10)
        ])

        pygame.display.flip()

        # --- キー入力処理 ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # 上キーまたは下キーで選択を切り替え
                if event.key == pygame.K_UP:
                    selected_index = 0  # 1Pへ
                if event.key == pygame.K_DOWN:
                    selected_index = 1  # 2Pへ

                # 決定キー
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    return selected_index  # 選んだ番号（0か1）を返して終了


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    game_running = True
    while game_running:
        # スタート画面を表示し、プレイヤーの選択結果を受け取る
        # mode は 0 (1P) か 1 (2P) になる
        mode = show_start_screen(screen)

        # 現状はどちらを選んでも同じゲームが始まりますが
        # ここで if mode == 1: などとすれば2Pモードへの分岐が可能です

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

        # --- ゲームプレイ ---
        run_level = True
        while run_level:
            clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run_level = False
                    game_running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        player.shoot()

            all_sprites.update()

            hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
            for hit in hits:
                new_mob()

            hits = pygame.sprite.spritecollide(player, mobs, False)
            if hits:
                run_level = False

            screen.fill(BLACK)
            all_sprites.draw(screen)
            pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
