import pygame
import sys
import random
from settings import *
from sprites import Player, Enemy, Bullet, Star, Mountain, Wall, FormationEnemy, TrackingEnemy

HS_FILE = "highscore.txt"

# ステージ切り替えタイミングのオーバーライド (設定ファイルより優先)
# Stage 2 (惑星) 開始: 20秒
TIME_STAGE2_START = 20000
# Stage 3 (要塞) 開始: 60秒 (40-50秒の山イベントを入れるため延長)
TIME_STAGE3_START = 60000


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


def init_stage_objects(current_time, all_sprites, stars, hazards):
    all_sprites.empty()
    stars.empty()
    hazards.empty()

    # 宇宙 (Stage 1)
    if current_time < TIME_STAGE3_START:
        for i in range(50):
            s = Star(from_right=False)
            all_sprites.add(s)
            stars.add(s)

    # Stage 2 (惑星) の初期配置は「平坦」なので山は配置しない
    # (時間経過のスクリプトで配置する)

    # Stage 3 (要塞)
    if current_time >= TIME_STAGE3_START:
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
        hazards = pygame.sprite.Group()

        player = Player(all_sprites, bullets)

        score = 0
        lives = 2
        death_time = 0
        current_time = 0

        init_stage_objects(current_time, all_sprites, stars, hazards)
        all_sprites.add(player)

        pygame.time.set_timer(pygame.USEREVENT + 2, 800)

        top_y = HEIGHT // 4
        bottom_y = HEIGHT * 3 // 4
        center_y = HEIGHT // 2

        # ★イベントスクリプト
        base_script = [
            # --- 前半: 青い編隊 (2, 4, 6, 8秒) ---
            {'time': 2000, 'type': 'formation', 'pos': 'top'},
            {'time': 4000, 'type': 'formation', 'pos': 'bottom'},
            {'time': 6000, 'type': 'formation', 'pos': 'top'},
            {'time': 8000, 'type': 'formation', 'pos': 'bottom'},

            # --- 後半: 紫の追尾 (12, 14, 16秒 - 3体くの字) ---
            # 12秒: 上
            {'time': 12000, 'type': 'tracker', 'exact_y': top_y,     'offset_x': 0},
            {'time': 12000, 'type': 'tracker',
                'exact_y': top_y - 40, 'offset_x': 40},
            {'time': 12000, 'type': 'tracker',
                'exact_y': top_y + 40, 'offset_x': 40},

            # 14秒: 下
            {'time': 14000, 'type': 'tracker',
                'exact_y': bottom_y,     'offset_x': 0},
            {'time': 14000, 'type': 'tracker',
                'exact_y': bottom_y - 40, 'offset_x': 40},
            {'time': 14000, 'type': 'tracker',
                'exact_y': bottom_y + 40, 'offset_x': 40},

            # 16秒: 真ん中
            {'time': 16000, 'type': 'tracker',
                'exact_y': center_y,     'offset_x': 0},
            {'time': 16000, 'type': 'tracker',
                'exact_y': center_y - 40, 'offset_x': 40},
            {'time': 16000, 'type': 'tracker',
                'exact_y': center_y + 40, 'offset_x': 40},

            # --- Stage 2 地形イベント: 山 (40, 45, 50秒) ---
            {'time': 40000, 'type': 'mountain'},
            {'time': 45000, 'type': 'mountain'},
            {'time': 50000, 'type': 'mountain'},
        ]
        enemy_script = list(base_script)

        run_level = True
        while run_level:
            dt = clock.tick(FPS)

            if player.alive():
                current_time += dt

                # スクリプト実行
                if len(enemy_script) > 0:
                    while len(enemy_script) > 0 and current_time >= enemy_script[0]['time']:
                        next_spawn = enemy_script[0]
                        enemy_type = next_spawn['type']

                        # --- 青い編隊 ---
                        if enemy_type == 'formation':
                            start_y = 0
                            y_dir = 1
                            if next_spawn['pos'] == 'top':
                                start_y = HEIGHT // 4
                                y_dir = 1
                            else:
                                start_y = HEIGHT * 3 // 4
                                y_dir = -1

                            for i in range(4):
                                offset = i * 30
                                fe = FormationEnemy(offset, start_y, y_dir)
                                all_sprites.add(fe)
                                mobs.add(fe)

                        # --- 紫の追尾 ---
                        elif enemy_type == 'tracker':
                            start_y = 0
                            offset_x = 0

                            if 'exact_y' in next_spawn:
                                start_y = next_spawn['exact_y']
                            elif next_spawn['pos'] == 'top':
                                start_y = HEIGHT // 4
                            else:
                                start_y = HEIGHT * 3 // 4

                            if 'offset_x' in next_spawn:
                                offset_x = next_spawn['offset_x']

                            te = TrackingEnemy(start_y, player, offset_x)
                            all_sprites.add(te)
                            mobs.add(te)

                        # --- 山 (地形) ---
                        elif enemy_type == 'mountain':
                            # 上下の山を同時に出現させる
                            m_top = Mountain(is_top=True, from_right=True)
                            all_sprites.add(m_top)
                            hazards.add(m_top)
                            m_btm = Mountain(is_top=False, from_right=True)
                            all_sprites.add(m_btm)
                            hazards.add(m_btm)

                        enemy_script.pop(0)

            # イベント処理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run_level = False
                    game_running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and player.alive():
                        player.shoot()

                # 背景・星の出現 (地形はスクリプト管理になったのでランダム生成は削除)
                elif event.type == pygame.USEREVENT + 2:
                    # Stage 1 & 2: 星は出し続ける
                    if current_time < TIME_STAGE3_START:
                        if random.random() < 0.8:
                            s = Star(from_right=True)
                            all_sprites.add(s)
                            stars.add(s)

                    # Stage 3: 壁のランダム生成
                    if current_time >= TIME_STAGE3_START:
                        w_top = Wall(is_top=True, from_right=True)
                        all_sprites.add(w_top)
                        hazards.add(w_top)
                        w_btm = Wall(is_top=False, from_right=True)
                        all_sprites.add(w_btm)
                        hazards.add(w_btm)

            all_sprites.update()

            hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
            for hit in hits:
                score += 100

            if player.alive():
                hits_mob = pygame.sprite.spritecollide(player, mobs, False)
                hits_env = pygame.sprite.spritecollide(player, hazards, False)

                if hits_mob or hits_env:
                    player.kill()
                    lives -= 1
                    death_time = pygame.time.get_ticks()

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
                        mobs.empty()
                        bullets.empty()

                        # リスポーン時の時間巻き戻し処理
                        if current_time >= TIME_STAGE3_START:
                            current_time = TIME_STAGE3_START
                        elif current_time >= TIME_STAGE2_START:
                            current_time = TIME_STAGE2_START
                        else:
                            current_time = 0

                        # 通過済みのスクリプトを除去
                        enemy_script = [
                            e for e in base_script if e['time'] > current_time]

                        init_stage_objects(
                            current_time, all_sprites, stars, hazards)
                        player = Player(all_sprites, bullets)
                        all_sprites.add(player)

                        screen.fill(BLACK)
                        pygame.display.flip()
                        pygame.time.wait(500)

            # 描画
            if lives >= 0 or (lives < 0 and pygame.time.get_ticks() - death_time <= 5000):
                bg_color = BLACK
                if current_time >= TIME_STAGE3_START:
                    bg_color = (20, 20, 40)

                screen.fill(bg_color)
                all_sprites.draw(screen)

                draw_text(screen, f"SCORE: {score}", 18, WIDTH // 2, 10, WHITE)
                draw_text(screen, f"LIVES: {lives}", 18, WIDTH - 60, 10, WHITE)

                stage_name = "SPACE"
                if current_time >= TIME_STAGE3_START:
                    stage_name = "BASE"
                elif current_time >= TIME_STAGE2_START:
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
