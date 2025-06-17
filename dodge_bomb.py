import os
import sys
import time
import random

import pygame as pg


WIDTH, HEIGHT = 1100, 650 #画面サイズ
DELTA = { #押下キーと移動量を対応させる
    pg.K_UP:   (0, -5), 
    pg.K_DOWN: (0, 5), 
    pg.K_LEFT: (-5, 0), 
    pg.K_RIGHT:(5, 0), 
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数: こうかとんRect or 爆弾Rect\n
    戻り値: 横方向, 縦方向の真理値tuple（True:画面内 / False:画面外）\n
    概要: Rectオブジェクトのleft, right, top, bottomの値から画面内・外を判定する\n
    """
    flag_x, flag_y = True, True

    if (rct.left < 0) | (rct.right > WIDTH): flag_x = False #横
    if (rct.top < 0) | (rct.bottom > HEIGHT): flag_y = False #縦

    return (flag_x, flag_y)


def gameover(screen: pg.Surface) -> None:
    """
    引数: 画面のSurface (screen)\n
    概要: ゲームオーバー時に, 半透明の黒い画面上に「Game Over」と表示し, 泣いているこうかとん画像を貼り付ける関数
    """
    mid_x = WIDTH // 2
    mid_y = HEIGHT // 2

    #ブラックアウト
    black_img = pg.Surface((WIDTH, HEIGHT))
    black_rct = black_img.get_rect()
    pg.draw.rect(black_img, (0, 0, 0), black_rct)
    black_img.set_alpha(150)

    #「Game Over」の文字列
    fnt = pg.font.Font(None, 50)
    txt = fnt.render("Game Over", True, (255, 255, 255))
    txt_rct = txt.get_rect()
    txt_rct.centerx = mid_x #画面中央に表示する
    txt_rct.centery = mid_y

    #泣いているこうかとんの画像
    kk_img_l = pg.image.load("fig/8.png") #左(left)
    kk_img_r = pg.image.load("fig/8.png") #右(right)
    kk_rct_l = kk_img_l.get_rect()
    kk_rct_r = kk_img_r.get_rect()
    kk_rct_l.centerx = mid_x - 150
    kk_rct_l.centery = mid_y
    kk_rct_r.centerx = mid_x + 150
    kk_rct_r.centery = mid_y

    #画面に表示(5秒間)
    screen.blit(black_img, black_rct)
    screen.blit(txt, txt_rct)
    screen.blit(kk_img_l, kk_rct_l)
    screen.blit(kk_img_r, kk_rct_r)
    pg.display.update()
    time.sleep(5)


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    概要: サイズの異なる爆弾Surfaceを要素としたリストと加速度リストを返す
    """
    bb_accs = [a for a in range(1, 11)]
    bb_imgs = []

    for r in range(1, 11):
        bb_img = pg.Surface((20 * r, 20 * r))
        pg.draw.circle(
            bb_img, 
            (255, 0, 0),
            (10 * r, 10 * r), 
            10 * r
        )
        bb_img.set_colorkey((0, 0, 0))
        bb_imgs.append(bb_img)
    
    return (bb_imgs, bb_accs)


def get_kk_img(sum_mv: tuple[int, int]) -> pg.Surface:
    """
    概要: 移動量の合計値タプルに対応する向きの画像Surfaceを返す
    """

    kk_img = pg.image.load("fig/3.png")

    #下方向. rotozoom単体では作れない.
    kk_img_down = pg.transform.rotozoom(kk_img, 90, 0.9)
    kk_img_down = pg.transform.flip(kk_img_down, True, False)

    mv_rotation = {
        (0, 0)  :pg.transform.rotozoom(kk_img, 0, 0.9), #停止
        (-5, 0) :pg.transform.rotozoom(kk_img, 0, 0.9), #左
        (-5, 5) :pg.transform.rotozoom(kk_img, 45, 0.9), #左下
        (0, 5)  :kk_img_down, #下
        (5, 5)  :pg.transform.rotozoom(kk_img_down, 45, 1), #右下
        (5, 0)  :pg.transform.rotozoom(kk_img_down, 90, 1), #右
        (5, -5) :pg.transform.rotozoom(kk_img_down, 135, 1), #右上
        (0, -5) :pg.transform.rotozoom(kk_img_down, 180, 1), #上
        (-5, -5):pg.transform.rotozoom(kk_img, -45, 0.9), #左上
    }

    return mv_rotation[sum_mv]


def calc_orientation(org: pg.Rect, dst: pg.Rect, current_xy: tuple[float, float]) -> tuple[float, float]:
    """
    引数: 爆弾Rect, こうかとんRect, 爆弾の速度タプル(vx, vy)
    概要: orgから見て, dstがどこにあるかを計算し, 方向ベクトルをタプルで返す
    """
    diff_x = dst.centerx - org.centerx
    diff_y = dst.centery - org.centery
    distance: float = (diff_x ** 2 + diff_y ** 2) ** 0.5 #差ベクトルの長さを取得

    vec_norm: float = (current_xy[0] ** 2 + current_xy[1] ** 2) ** 0.5 #爆弾の速度ベクトルの長さを取得
    
    new_x: float = vec_norm * diff_x / distance #方向ベクトルのx成分
    new_y: float = vec_norm * diff_y / distance #方向ベクトルのy成分

    if distance < 300.0:
        new_x = current_xy[0]
        new_y = current_xy[1]

    return (new_x, new_y)


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    
    kk_img = get_kk_img((0, 0))
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    #爆弾Surfaceを作成
    bb_radius = 10 #大きさ(半径)
    vx, vy = 5, 5 #速度
    bb_img = pg.Surface((2 * bb_radius, 2 * bb_radius))
    pg.draw.circle(
        bb_img, 
        (255, 0, 0), 
        (bb_radius, bb_radius), 
        bb_radius
    )
    bb_img.set_colorkey((0, 0, 0))
    bb_rct = bb_img.get_rect()
    bb_rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT) #初期位置はランダム

    clock = pg.time.Clock()
    tmr = 0
    
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        screen.blit(bg_img, [0, 0]) 

        #こうかとんの移動量を押下キーに応じて決める
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]

        for k in DELTA:
            if key_lst[k]:
                sum_mv[0] += DELTA[k][0]
                sum_mv[1] += DELTA[k][1]
        
        #移動方向に応じて向きを変える
        kk_img = get_kk_img(tuple(sum_mv))
        
        #爆弾の追従
        vx, vy = calc_orientation(bb_rct, kk_rct, (vx, vy))

        #爆弾の拡大/加速
        bb_x_before = bb_rct.centerx #座標を保存する
        bb_y_before = bb_rct.centery
        bb_imgs, bb_accs = init_bb_imgs()
        acc_phase = min(tmr//500, 9) #加速/拡大の段階. 時間とともに進む. 0~9.
        avx = vx * bb_accs[acc_phase]
        avy = vy * bb_accs[acc_phase]
        bb_img = bb_imgs[acc_phase]
        bb_rct = bb_img.get_rect()
        bb_rct.center = bb_x_before, bb_y_before

        #移動
        kk_rct.move_ip(sum_mv)
        bb_rct.move_ip((avx, avy))

        #画面端判定
        kk_bound = check_bound(kk_rct) #こうかとん. 画面外に出るとき, 移動前の位置に戻る
        sum_mv_bound = [0, 0] #横, 縦
        if not kk_bound[0]: sum_mv_bound[0] = -1 * sum_mv[0]
        if not kk_bound[1]: sum_mv_bound[1] = -1 * sum_mv[1]
        kk_rct.move_ip(sum_mv_bound)

        bb_bound = check_bound(bb_rct) #爆弾. 画面端にぶつかると、バウンドする
        if not bb_bound[0]: vx = -1 * vx
        if not bb_bound[1]: vy = -1 * vy

        #衝突判定
        if pg.Rect.colliderect(kk_rct, bb_rct):
            gameover(screen)
            #こうかとんと爆弾を再設定する. (しないと無限にゲームオーバーになる)
            kk_rct.center = 300, 200
            bb_rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT) #初期位置はランダム
            vx, vy = 5, 5
            tmr = 0

        #画面に表示
        screen.blit(kk_img, kk_rct)
        screen.blit(bb_img, bb_rct)
        pg.display.update()

        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()