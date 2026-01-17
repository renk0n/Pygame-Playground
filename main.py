import pygame
import sys
import random
from settings import *
from sprites import Player, Enemy, Bullet, Star, Mountain, Wall

HS_FILE = "highscore.txt"


def draw_text(screen, text, size, x, y, color=WHITE):
    font_name = pygame.font.match_font('arial')
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    screen.blit(text_surface, text_rect)


def load_high_score():
    try:
        with open(HS_FILE, 'r') as f:
            return int(f.read())
    except:
        return 0


def save_high_score(score):
    with open(HS_FILE, 'w') as f:
        f.write(str(score))


def show_start_screen(screen, high_score):
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
        draw_text(screen, f"HI  {high_score:07}", 25,
                  WIDTH // 2, HEIGHT // 2 + 40, (255, 100, 100))

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

# ★復活時などの初期化用関数


def init_stage_objects(score, all_sprites, stars, hazards):
    all_sprites.empty()
    stars.empty()
    hazards.empty()

    # スコアに応じて初期配置を変える（チェックポイント用）
    # 星はとりあえずばら撒く
    if score < SCORE_STAGE3:
        for i in range(50):
            s = Star(from_right=False)
            all_sprites.add(s)
            stars.add(s)

    # ステージ2エリアなら山も少し置いておく
    if SCORE_STAGE2 <= score < SCORE_STAGE3:
        for i in range(3):
            m = Mountain(is_top=True, from_right=False)
            all_sprites.add(m)
            hazards.add(m)
            m = Mountain(is_top=False, from_right=False)
            all_sprites.add(m)
            hazards.add(m)

    # ステージ3エリアなら壁を置いておく
    if score >= SCORE_STAGE3:
        for i in range(5):
            w = Wall(is_top=True, from_right=False)
            all_sprites.add(w)
            hazards.add(w)
            w = Wall(is_top=False, from_right=False)
            all_sprites.add(w)
            hazards.add(w)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    high_score = load_high_score()

    game_running = True
    while game_running:
        mode = show_start_screen(screen, high_score)

        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        stars = pygame.sprite.Group()
        hazards = pygame.sprite.Group()  # 山や壁

        player = Player(all_sprites, bullets)
        all_sprites.add(player)

        # 最初の初期化（スコア0の状態）
        score = 0
        lives = 2
        death_time = 0

        init_stage_objects(score, all_sprites, stars, hazards)
        # プレイヤー追加（initで消えちゃうので再追加）
        all_sprites.add(player)

        # 敵生成用タイマー
        pygame.time.set_timer(pygame.USEREVENT + 1, 1500)  # 1.5秒ごとに敵出現

        # ★地形生成用タイマー（これがスクロールの鍵）
        pygame.time.set_timer(pygame.USEREVENT + 2, 800)  # 0.8秒ごとに地形チェック

        run_level = True
        while run_level:
            clock.tick(FPS)

            # イベント処理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run_level = False
                    game_running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and player.alive():
                        player.shoot()

                # --- 敵の出現 ---
                elif event.type == pygame.USEREVENT + 1:
                    # 敵はどのステージでも出る
                    m = Enemy()
                    all_sprites.add(m)
                    mobs.add(m)

                # --- 地形/星の出現（シームレス生成） ---
                elif event.type == pygame.USEREVENT + 2:
                    # 1. 星を降らす (Stage 3以外はずっと降る)
                    if score < SCORE_STAGE3:
                        if random.random() < 0.8:  # 80%の確率で星追加
                            s = Star(from_right=True)
                            all_sprites.add(s)
                            stars.add(s)

                    # 2. 山を出す (Stage 2の間)
                    # スコアが近づいたら出し始める (フェードイン効果)
                    if score >= SCORE_STAGE2 and score < SCORE_STAGE3:
                        if random.random() < 0.6:  # 60%の確率で山追加
                            m_top = Mountain(is_top=True, from_right=True)
                            all_sprites.add(m_top)
                            hazards.add(m_top)
                            m_btm = Mountain(is_top=False, from_right=True)
                            all_sprites.add(m_btm)
                            hazards.add(m_btm)

                    # 3. 壁を出す (Stage 3以降)
                    if score >= SCORE_STAGE3:
                        # 確実に壁を出し続けて通路にする
                        w_top = Wall(is_top=True, from_right=True)
                        all_sprites.add(w_top)
                        hazards.add(w_top)
                        w_btm = Wall(is_top=False, from_right=True)
                        all_sprites.add(w_btm)
                        hazards.add(w_btm)

            all_sprites.update()

            # 弾 -> 敵
            hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
            for hit in hits:
                score += 100
                # 敵を即座に補充せず、タイマーで湧かせるのでここはスコア加算のみ

            # 敵/障害物 -> プレイヤー
            if player.alive():
                hits_mob = pygame.sprite.spritecollide(player, mobs, False)
                hits_env = pygame.sprite.spritecollide(player, hazards, False)

                if hits_mob or hits_env:
                    player.kill()
                    lives -= 1
                    death_time = pygame.time.get_ticks()

            # プレイヤー死亡処理
            if not player.alive():
                now = pygame.time.get_ticks()
                if lives < 0:
                    if score > high_score:
                        high_score = score
                        save_high_score(high_score)

                    if now - death_time > 5000:
                        run_level = False
                    else:
                        draw_text(screen, "GAME OVER", 40,
                                  WIDTH // 2, HEIGHT - 100, RED)
                else:
                    if now - death_time > 2000:
                        # ★チェックポイント復活
                        # 全消しして、現在のスコアに応じた地形を再配置
                        mobs.empty()
                        bullets.empty()
                        init_stage_objects(score, all_sprites, stars, hazards)

                        player = Player(all_sprites, bullets)
                        all_sprites.add(player)

                        screen.fill(BLACK)
                        pygame.display.flip()
                        pygame.time.wait(500)

            # 描画
            if lives >= 0 or (lives < 0 and pygame.time.get_ticks() - death_time <= 5000):
                # 背景色は徐々に変えたいが、今はシンプルにステージ3だけ色を変える
                bg_color = BLACK
                if score >= SCORE_STAGE3:
                    bg_color = (20, 20, 40)  # 基地内部色

                screen.fill(bg_color)
                all_sprites.draw(screen)

                draw_text(screen, f"SCORE: {score}", 18, WIDTH // 2, 10, WHITE)
                draw_text(screen, f"LIVES: {lives}", 18, WIDTH - 60, 10, WHITE)

                # 現在のステージ名を右下にこっそり出す
                stage_name = "SPACE"
                if score >= SCORE_STAGE3:
                    stage_name = "BASE"
                elif score >= SCORE_STAGE2:
                    stage_name = "PLANET"
                draw_text(screen, stage_name, 14, 40, HEIGHT - 20, GREY)

                if lives < 0:
                    draw_text(screen, "GAME OVER", 40,
                              WIDTH // 2, HEIGHT - 100, RED)

            pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
