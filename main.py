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
                # ★修正：エンターキー（RETURN）のみで開始
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

        # --- ゲーム開始初期化 ---
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()

        # プレイヤー生成
        player = Player(all_sprites, bullets)
        all_sprites.add(player)

        # 敵生成関数
        def new_mob():
            m = Enemy()
            all_sprites.add(m)
            mobs.add(m)

        for i in range(8):
            new_mob()

        score = 0
        lives = 2  # ★残機：2機（死ぬと減る）
        death_time = 0  # 死んだ時刻を記録する変数

        # --- ステージループ ---
        run_level = True
        while run_level:
            clock.tick(FPS)

            # イベント処理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run_level = False
                    game_running = False
                elif event.type == pygame.KEYDOWN:
                    # プレイヤーが生きてる時だけ発射可能
                    if event.key == pygame.K_SPACE and player.alive():
                        player.shoot()

            # 更新
            all_sprites.update()

            # 衝突判定：弾 -> 敵
            hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
            for hit in hits:
                score += 100
                new_mob()

            # 衝突判定：敵 -> プレイヤー（プレイヤーが生きてる時のみ）
            if player.alive():
                hits = pygame.sprite.spritecollide(player, mobs, False)
                if hits:
                    player.kill()  # プレイヤーを消す
                    lives -= 1    # 残機を減らす
                    death_time = pygame.time.get_ticks()  # 死んだ時間を記録

            # ★プレイヤー死亡中の処理
            if not player.alive():
                now = pygame.time.get_ticks()

                # --- ゲームオーバー処理（残機がマイナスになったら）---
                if lives < 0:
                    # 5秒 (5000ms) 経過したらタイトルへ
                    if now - death_time > 5000:
                        run_level = False
                    else:
                        # 画面下にGAME OVER表示
                        draw_text(screen, "GAME OVER", 40,
                                  WIDTH // 2, HEIGHT - 100, RED)

                # --- リスポーン処理（残機があるなら）---
                else:
                    # 2秒 (2000ms) 経過したら復活
                    if now - death_time > 2000:
                        # ブラックアウト的なリセット処理
                        # 全てのスプライトを一度消す（敵も弾も）
                        all_sprites.empty()
                        mobs.empty()
                        bullets.empty()

                        # プレイヤー再生成
                        player = Player(all_sprites, bullets)
                        all_sprites.add(player)

                        # 敵を再配置
                        for i in range(8):
                            new_mob()

                        # 一瞬画面を黒くしてリセット感を出す（任意）
                        screen.fill(BLACK)
                        pygame.display.flip()
                        pygame.time.wait(200)  # 0.2秒だけ止める

            # 描画
            # ゲームオーバー時以外は通常描画（ゲームオーバー時は文字を上書きするためfill後に描画）
            if lives >= 0 or (lives < 0 and pygame.time.get_ticks() - death_time <= 5000):
                screen.fill(BLACK)
                all_sprites.draw(screen)
                # UI表示
                draw_text(screen, f"SCORE: {score}", 18, WIDTH // 2, 10, WHITE)
                draw_text(screen, f"LIVES: {lives}", 18, WIDTH - 60, 10, WHITE)

                # ゲームオーバーの文字を再描画（draw順序のため）
                if lives < 0:
                    draw_text(screen, "GAME OVER", 40,
                              WIDTH // 2, HEIGHT - 100, RED)

            pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
