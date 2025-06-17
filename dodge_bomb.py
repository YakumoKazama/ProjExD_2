import os
import sys
import pygame as pg
import random


WIDTH, HEIGHT = 1100, 650 #画面サイズ
DELTA = { #押下キーと移動量を対応させる
    pg.K_UP:(0,-5), 
    pg.K_DOWN:(0,5), 
    pg.K_LEFT:(-5,0), 
    pg.K_RIGHT:(5,0), 
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


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    #爆弾Surfaceを作成
    bb_radius = 10 #大きさ(半径)
    vx, vy = 5, 5 #速度
    bb_img = pg.Surface((2*bb_radius,2*bb_radius))
    pg.draw.circle(
        bb_img, 
        (255,0,0), 
        (bb_radius, bb_radius), 
        bb_radius
    )
    bb_img.set_colorkey((0,0,0))
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
        sum_mv = [0,0]

        for k in DELTA:
            if key_lst[k]:
                sum_mv[0] += DELTA[k][0]
                sum_mv[1] += DELTA[k][1]

        kk_rct.move_ip(sum_mv)
        bb_rct.move_ip(vx, vy)

        #画面端判定
        kk_bound = check_bound(kk_rct) #こうかとん. 画面外に出るとき, 移動前の位置に戻る
        sum_mv_bound = [0, 0] #横, 縦
        if not kk_bound[0]: sum_mv_bound[0] = -1 * sum_mv[0]
        if not kk_bound[1]: sum_mv_bound[1] = -1 * sum_mv[1]
        kk_rct.move_ip(sum_mv_bound)

        bb_bound = check_bound(bb_rct) #爆弾. 画面端にぶつかると、バウンドする
        if not bb_bound[0]: vx = -1 * vx
        if not bb_bound[1]: vy = -1 * vy

        #画面に表示
        screen.blit(kk_img, kk_rct)
        screen.blit(bb_img, bb_rct)
        pg.display.update()

        #衝突判定
        if pg.Rect.colliderect(kk_rct, bb_rct):
            return #ゲーム終了

        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
