import pygame
import sys
from settings import *
from sprites import Player, Enemy, Bullet  # Bulletを追加


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    # スプライトグループ
    all_sprites = pygame.sprite.Group()
    mobs = pygame.sprite.Group()
    bullets = pygame.sprite.Group()  # 弾グループ

    # プレイヤー生成（引数にグループを渡すように変更）
    player = Player(all_sprites, bullets)
    all_sprites.add(player)

    # 敵の生成関数（何回も使うので関数化しておくと便利）
    def new_mob():
        m = Enemy()
        all_sprites.add(m)
        mobs.add(m)

    for i in range(8):
        new_mob()

    running = True
    while running:
        clock.tick(FPS)

        # 1. イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()  # スペースキーで発射

        # 2. 更新
        all_sprites.update()

        # ★当たり判定：弾が敵に当たったか？
        # groupcollide(group1, group2, dokill1, dokill2)
        # True, True なので、当たったら「敵」も「弾」も消える
        hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
        for hit in hits:
            # 敵が減った分だけ補充する
            new_mob()

        # ★当たり判定：敵がプレイヤーに当たったか？
        hits = pygame.sprite.spritecollide(player, mobs, False)
        if hits:
            running = False  # 当たったらゲーム終了

        # 3. 描画
        screen.fill(BLACK)
        all_sprites.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
