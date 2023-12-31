import os
import random
import sys
import time

import pygame as pg


WIDTH = 1200  # ゲームウィンドウの幅
HEIGHT = 600  # ゲームウィンドウの高さ
MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]
NUM_OF_BOMBS = 5  # 爆弾の数


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとん，または，爆弾SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        img0 = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/{num}.png"), 0, 2.0)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
        self.imgs = {  # 0度から反時計回りに定義
            (+5, 0): img,  # 右
            (+5, -5): pg.transform.rotozoom(img, 45, 1.0),  # 右上
            (0, -5): pg.transform.rotozoom(img, 90, 1.0),  # 上
            (-5, -5): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
            (-5, 0): img0,  # 左
            (-5, +5): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
            (0, +5): pg.transform.rotozoom(img, -90, 1.0),  # 下
            (+5, +5): pg.transform.rotozoom(img, -45, 1.0),  # 右下
            (0, 0): img0
        }
        # self.img = pg.transform.flip(  # 左右反転
        #     pg.transform.rotozoom(  # 2倍に拡大
        #         pg.image.load(f"{MAIN_DIR}/fig/{num}.png"), 
        #         0, 
        #         2.0), 
        #     True, 
        #     False
        # )
        self.img = self.imgs[(+5, 0)]  # 右向きこうかとんがデフォルト
        self.rct = self.img.get_rect()
        self.rct.center = xy

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/{num}.png"), 0, 2.0)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        self.img = self.imgs[tuple(sum_mv)]
        screen.blit(self.img, self.rct)


class Bomb:
    """
    爆弾に関するクラス
    """
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), 
              (255, 255, 0), (255, 0, 255), (0, 255, 255)]
    
    def __init__(self):
        """
        爆弾円を生成
        """
        rad = random.randint(20, 90)
        self.img = pg.Surface((2*rad, 2*rad))
        color = random.choice(__class__.colors)
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = random.choice([-5, 5]), random.choice([-5, 5])

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


class Beam:
    """
    ビームの実装
    """
    def __init__(self, bird: Bird):  # 練習1
            self.img = pg.image.load(f"{MAIN_DIR}/fig/beam.png")
            self.rct = self.img.get_rect()
            self.rct.centery = bird.rct.centery  # こうかとんの中心座標を取得
            self.rct.centerx = bird.rct.centerx + bird.rct.width/2
            self.vx, self.vy = +5, 0

    def update(self, screen: pg.Surface):  # 練習1
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


class Explosion:  # 演習1
    """
    爆発エフェクト
    """
    def __init__(self, bomb: Bomb):
        """
        爆発エフェクトを生成
        """
        img_expl = pg.image.load(f"{MAIN_DIR}/fig/explosion.gif")
        self.imgs = [img_expl, 
                     pg.transform.flip(img_expl, True, False),
                     pg.transform.flip(img_expl, False, True), 
                     pg.transform.flip(img_expl, True, True)]
        self.rct = img_expl.get_rect()
        self.rct.center = bomb.rct.center  # 爆弾の中心座標を取得
        self.life = 10  # 爆弾時間

    def update(self, screen: pg.Surface):
        """
        爆発経過時間lifeを1減算
        引数 screen：画面Surface
        """
        self.life -= 1
        screen.blit(self.imgs[self.life%4], self.rct)

def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load(f"{MAIN_DIR}/fig/pg_bg.jpg")
    bird = Bird(3, (900, 400))
    bomb = Bomb()
    # NUM_OF_BOMS個のBombsインスタンス
    bombs = [Bomb() for i in range(NUM_OF_BOMBS)]
    beam = None
    expl_lst = []  # Explosionインスタンス用の空リスト

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:  # スペースキーが押されたら
                beam = Beam(bird)  # ビームインスタンスの生成
        
        screen.blit(bg_img, [0, 0])
        
        for bomb in bombs:
            if bird.rct.colliderect(bomb.rct):
                # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                bird.change_img(8, screen)
                pg.display.update()
                time.sleep(1)
                return
        for i, bomb in enumerate(bombs):
            if beam is not None and beam.rct.colliderect(bomb.rct):
                # 爆弾撃ち落し時に，こうかとん画像を切り替える
                expl_lst.append(Explosion(bombs[i]))
                beam = None
                bombs[i] = None
                bird.change_img(6, screen)
                pg.display.update()
        #  Noneではない爆弾だけのリスト
        bombs = [bomb for bomb in bombs if bomb is not None]
        #  lifeが0より大きいExplosionインスタンスだけのリスト
        expl_lst = [expl for expl in expl_lst if expl.life > 0]

        key_lst = pg.key.get_pressed()
        for expl in expl_lst:
            expl.update(screen)
        bird.update(key_lst, screen)
        for bomb in bombs:
            bomb.update(screen)
        if beam is not None:
            beam.update(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
