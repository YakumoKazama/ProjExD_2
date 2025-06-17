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
    pg.draw.circle(bb_img, (255,0,0), (bb_radius, bb_radius), bb_radius)
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

        key_lst = pg.key.get_pressed()
        sum_mv = [0,0]

        for k in DELTA:
            if key_lst[k]:
                sum_mv[0] += DELTA[k][0]
                sum_mv[1] += DELTA[k][1]

        kk_rct.move_ip(sum_mv)
        bb_rct.move_ip(vx, vy)
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
