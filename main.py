import pygame
import sys
import random
from settings import *
from sprites import Player, Enemy, Bullet, Star, Mountain, Wall, FormationEnemy, TrackingEnemy, FlatGround, CeilingTurret, HoppingEnemy, WaveEnemy

HS_FILE = "highscore.txt"

TIME_STAGE2_START = 20000
TIME_STAGE3_START = 40000


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

    # --- Stage 1: 宇宙 ---
    if current_time < TIME_STAGE3_START:
        for i in range(50):
            s = Star(from_right=False)
            all_sprites.add(s)
            stars.add(s)

    # --- Stage 2: 惑星 (地面の初期配置) ---
    if TIME_STAGE2_START <= current_time < TIME_STAGE3_START:
        num_blocks = WIDTH // 50 + 2
        for i in range(num_blocks):
            x_pos = i * 50
            g_top = FlatGround(x_pos, is_top=True)
            all_sprites.add(g_top)
            hazards.add(g_top)
            g_btm = FlatGround(x_pos, is_top=False)
            all_sprites.add(g_btm)
            hazards.add(g_btm)

    # --- Stage 3: 要塞 ---
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

        base_script = [
            # --- Stage 1: 青い編隊 (2, 4, 6, 8秒) ---
            {'time': 2000, 'type': 'formation', 'pos': 'top'},
            {'time': 4000, 'type': 'formation', 'pos': 'bottom'},
            {'time': 6000, 'type': 'formation', 'pos': 'top'},
            {'time': 8000, 'type': 'formation', 'pos': 'bottom'},

            # ★ Stage 1: ウェーブ飛行機 (上下交互)
            {'time': 10000, 'type': 'wave', 'base_y': top_y},    # 上
            {'time': 10500, 'type': 'wave', 'base_y': bottom_y},  # 下
            {'time': 11000, 'type': 'wave', 'base_y': top_y},    # 上
            {'time': 11500, 'type': 'wave', 'base_y': bottom_y},  # 下

            # --- Stage 1: 紫の追尾 (12, 14, 16秒) ---
            {'time': 12000, 'type': 'tracker', 'exact_y': top_y,     'offset_x': 0},
            {'time': 12000, 'type': 'tracker',
                'exact_y': top_y - 40, 'offset_x': 40},
            {'time': 12000, 'type': 'tracker',
                'exact_y': top_y + 40, 'offset_x': 40},

            {'time': 14000, 'type': 'tracker',
                'exact_y': bottom_y,     'offset_x': 0},
            {'time': 14000, 'type': 'tracker',
                'exact_y': bottom_y - 40, 'offset_x': 40},
            {'time': 14000, 'type': 'tracker',
                'exact_y': bottom_y + 40, 'offset_x': 40},

            {'time': 16000, 'type': 'tracker',
                'exact_y': center_y,     'offset_x': 0},
            {'time': 16000, 'type': 'tracker',
                'exact_y': center_y - 40, 'offset_x': 40},
            {'time': 16000, 'type': 'tracker',
                'exact_y': center_y + 40, 'offset_x': 40},

            # --- Stage 2 (20秒〜40秒): 砲台, ホッパー, ウェーブ ---

            # 22秒: 砲台3連
            {'time': 22000, 'type': 'turret', 'offset_x': 0},
            {'time': 22000, 'type': 'turret', 'offset_x': 60},
            {'time': 22000, 'type': 'turret', 'offset_x': 120},

            # 23秒: ホッパー
            {'time': 23000, 'type': 'hopper', 'offset_x': 0},

            # 25秒: 砲台
            {'time': 25000, 'type': 'turret', 'offset_x': 0},

            # 26.5秒: ホッパー
            {'time': 26500, 'type': 'hopper', 'offset_x': 0},

            # 28秒: 砲台
            {'time': 28000, 'type': 'turret', 'offset_x': 0},

            # ★ Stage 2: ウェーブ飛行機 (上下交互)
            {'time': 29000, 'type': 'wave', 'base_y': top_y},    # 上
            {'time': 29500, 'type': 'wave', 'base_y': bottom_y},  # 下
            {'time': 30000, 'type': 'wave', 'base_y': top_y},    # 上
            {'time': 30500, 'type': 'wave', 'base_y': bottom_y},  # 下

            # 30秒: ホッパー2体
            {'time': 30000, 'type': 'hopper', 'offset_x': 0},
            {'time': 30000, 'type': 'hopper', 'offset_x': 100},

            # 32秒: 砲台
            {'time': 32000, 'type': 'turret', 'offset_x': 0},

            # 34秒: ホッパー
            {'time': 34000, 'type': 'hopper', 'offset_x': 0},

            # 35秒: 砲台
            {'time': 35000, 'type': 'turret', 'offset_x': 0},

            # 37秒: ホッパー
            {'time': 37000, 'type': 'hopper', 'offset_x': 0},

            # 38秒: 砲台
            {'time': 38000, 'type': 'turret', 'offset_x': 0},
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

                        elif enemy_type == 'mountain':
                            m_top = Mountain(is_top=True, from_right=True)
                            all_sprites.add(m_top)
                            hazards.add(m_top)
                            m_btm = Mountain(is_top=False, from_right=True)
                            all_sprites.add(m_btm)
                            hazards.add(m_btm)

                        elif enemy_type == 'turret':
                            offset_x = next_spawn.get('offset_x', 0)
                            turret = CeilingTurret(
                                WIDTH + offset_x, player, all_sprites, hazards)
                            all_sprites.add(turret)
                            mobs.add(turret)

                        elif enemy_type == 'hopper':
                            offset_x = next_spawn.get('offset_x', 0)
                            hopper = HoppingEnemy(
                                WIDTH + offset_x, player, all_sprites, hazards)
                            all_sprites.add(hopper)
                            mobs.add(hopper)

                        elif enemy_type == 'wave':
                            base_y = next_spawn.get('base_y', HEIGHT // 2)
                            we = WaveEnemy(0, base_y)
                            all_sprites.add(we)
                            mobs.add(we)

                        enemy_script.pop(0)

            # 地面の継続生成処理
            if TIME_STAGE2_START <= current_time < TIME_STAGE3_START:
                grounds = [h for h in hazards if isinstance(h, FlatGround)]
                rightmost_x = 0
                if grounds:
                    rightmost_x = max([g.rect.right for g in grounds])

                if rightmost_x < WIDTH + 10:
                    g_top = FlatGround(
                        rightmost_x if grounds else WIDTH, is_top=True)
                    all_sprites.add(g_top)
                    hazards.add(g_top)
                    g_btm = FlatGround(
                        rightmost_x if grounds else WIDTH, is_top=False)
                    all_sprites.add(g_btm)
                    hazards.add(g_btm)

            # イベント処理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run_level = False
                    game_running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and player.alive():
                        player.shoot()

                # 背景・星・壁の出現
                elif event.type == pygame.USEREVENT + 2:
                    if current_time < TIME_STAGE3_START:
                        if random.random() < 0.8:
                            s = Star(from_right=True)
                            all_sprites.add(s)
                            stars.add(s)

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
                        hazards.empty()

                        if current_time >= 41000:
                            current_time = 41000
                        elif current_time >= 21000:
                            current_time = 21000
                        else:
                            current_time = 1000

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
