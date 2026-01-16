import pygame
import sys
from settings import *
from sprites import Player, Enemy, Bullet, Star  # Starを追加


def draw_text(screen, text, size, x, y, color=WHITE):
    font_name = pygame.font.match_font('arial')
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    screen.blit(text_surface, text_rect)


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

        draw_text(screen, "PRESS ENTER TO START",
                  18, WIDTH // 2, HEIGHT - 30, WHITE)

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
                if event.key == pygame.K_RETURN:
                    return selected_index


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    game_running = True
    while game_running:
        mode = show_start_screen(screen)

        # --- グループ作成 ---
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        stars = pygame.sprite.Group()  # ★星専用グループ

        # ★星を100個生成
        for i in range(100):
            s = Star()
            all_sprites.add(s)
            stars.add(s)

        player = Player(all_sprites, bullets)
        all_sprites.add(player)

        def new_mob():
            m = Enemy()
            all_sprites.add(m)
            mobs.add(m)

        for i in range(8):
            new_mob()

        score = 0
        lives = 2
        death_time = 0

        run_level = True
        while run_level:
            clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run_level = False
                    game_running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and player.alive():
                        player.shoot()

            all_sprites.update()

            hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
            for hit in hits:
                score += 100
                new_mob()

            if player.alive():
                hits = pygame.sprite.spritecollide(player, mobs, False)
                if hits:
                    player.kill()
                    lives -= 1
                    death_time = pygame.time.get_ticks()

            if not player.alive():
                now = pygame.time.get_ticks()
                if lives < 0:
                    if now - death_time > 5000:
                        run_level = False
                    else:
                        draw_text(screen, "GAME OVER", 40,
                                  WIDTH // 2, HEIGHT - 100, RED)
                else:
                    if now - death_time > 2000:
                        # リスポーン処理
                        # 星以外のスプライトを削除（星は残す）
                        for sprite in all_sprites:
                            if sprite not in stars:
                                sprite.kill()

                        mobs.empty()
                        bullets.empty()

                        player = Player(all_sprites, bullets)
                        all_sprites.add(player)

                        for i in range(8):
                            new_mob()

                        screen.fill(BLACK)
                        pygame.display.flip()
                        pygame.time.wait(200)

            # 描画
            if lives >= 0 or (lives < 0 and pygame.time.get_ticks() - death_time <= 5000):
                screen.fill(BLACK)
                all_sprites.draw(screen)  # 星もここで描画される（先に追加したので奥に表示）

                draw_text(screen, f"SCORE: {score}", 18, WIDTH // 2, 10, WHITE)
                draw_text(screen, f"LIVES: {lives}", 18, WIDTH - 60, 10, WHITE)

                if lives < 0:
                    draw_text(screen, "GAME OVER", 40,
                              WIDTH // 2, HEIGHT - 100, RED)

            pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
