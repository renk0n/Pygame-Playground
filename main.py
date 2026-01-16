import pygame
import sys
from settings import *
from sprites import Player, Enemy, Bullet

# 文字描画関数


def draw_text(screen, text, size, x, y, color=WHITE):
    font_name = pygame.font.match_font('arial')
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    screen.blit(text_surface, text_rect)

# スタート画面


def show_start_screen(screen):
    selected_index = 0
    waiting = True
    while waiting:
        screen.fill(BLACK)
        draw_text(screen, "Konami", 30, WIDTH // 2, HEIGHT // 6, WHITE)
        draw_text(screen, "GRADIUS", 80, WIDTH //
                  2 + 4, HEIGHT // 4 + 4, (200, 0, 0))
        draw_text(screen, "GRADIUS", 80, WIDTH //
                  2, HEIGHT // 4, (0, 100, 255))
        draw_text(screen, "(c) KONAMI 1986", 20,
                  WIDTH // 2, HEIGHT // 2, WHITE)
        draw_text(screen, "HI  0050000", 25, WIDTH //
                  2, HEIGHT // 2 + 40, (255, 100, 100))

        color_1p = WHITE if selected_index == 0 else (100, 100, 100)
        color_2p = WHITE if selected_index == 1 else (100, 100, 100)

        draw_text(screen, "1 PLAYER", 30, WIDTH // 2, HEIGHT * 3 / 4, color_1p)
        draw_text(screen, "2 PLAYERS", 30, WIDTH //
                  2, HEIGHT * 3 / 4 + 40, color_2p)

        cursor_y = (HEIGHT * 3 / 4 + 10) + (40 * selected_index)
        cursor_x = WIDTH // 2 - 100
        pygame.draw.polygon(screen, WHITE, [(
            cursor_x, cursor_y), (cursor_x, cursor_y + 20), (cursor_x + 20, cursor_y + 10)])

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = 0
                if event.key == pygame.K_DOWN:
                    selected_index = 1
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    return selected_index


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    game_running = True
    while game_running:
        mode = show_start_screen(screen)

        # --- ゲーム開始準備 ---
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        player = Player(all_sprites, bullets)
        all_sprites.add(player)

        # ★スコア変数を初期化
        score = 0

        def new_mob():
            m = Enemy()
            all_sprites.add(m)
            mobs.add(m)

        for i in range(8):
            new_mob()

        # --- ゲーム本編ループ ---
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

            # ★敵と弾の衝突判定
            hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
            for hit in hits:
                score += 100  # ★100点加算
                new_mob()     # 敵を補充

            # 敵とプレイヤーの衝突判定
            hits = pygame.sprite.spritecollide(player, mobs, False)
            if hits:
                run_level = False  # ゲームオーバー

            # 描画
            screen.fill(BLACK)
            all_sprites.draw(screen)

            # ★スコア表示 (画面上部中央)
            draw_text(screen, str(score), 18, WIDTH // 2, 10, WHITE)

            pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
