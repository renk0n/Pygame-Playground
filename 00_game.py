import random as r
import pygame as pg


def main():

    # 初期化処理
    pg.init()
    pg.display.set_caption('ぼくのかんがえたさいきょうのげーむ')
    disp_w, disp_h = 800, 600  # DisplaySize(WindowSize)
    screen = pg.display.set_mode((disp_w, disp_h))
    clock = pg.time.Clock()
    exit_flag = False
    exit_code = '000'
    shape_type = 0  # 描画図形の形状

    # ゲームループ [ここから]
    while not exit_flag:

        # システムイベントの検出
        for event in pg.event.get():
            if event.type == pg.QUIT:  # ウィンドウ[X]の押下
                exit_flag = True
                exit_code = '001'
            if event.type == pg.KEYDOWN:  # キーの押下
                if event.key == pg.K_SPACE:  # SpaceKey
                    shape_type += 1
                    if shape_type == 2:
                        shape_type = 0

        # 指定色で画面を塗りつぶし(fill)。実質的な画面クリア
        screen.fill(pg.Color('BLACK'))

        # 円(circle) or 四角形(rect) を描画
        x = r.randint(0, disp_w)
        y = r.randint(0, disp_h)
        rr = r.randint(5, 20)
        c = pg.Color('GREEN')
        if shape_type == 0:
            # 円 (描画先,色,(中心X,中心Y),半径)
            pg.draw.circle(screen, c, (x, y), rr)
        elif shape_type == 1:
            # 四角形 (描画先,色,(左上X,左上Y,幅,高さ))
            pg.draw.rect(screen, c, (x, y, rr, rr))

        # 画面出力の更新と同期
        pg.display.update()
        clock.tick(30)  # 最高速度を 30フレーム/秒 に制限

    # ゲームループ [ここまで]
    pg.quit()
    return exit_code


if __name__ == "__main__":
    code = main()
    print(f'プログラムを「コード{code}」で終了しました。')
