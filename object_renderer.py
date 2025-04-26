import pygame as pg
from settings import *

# 定义一个类ObjectRenderer，用于渲染游戏中的对象
class ObjectRenderer:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.wall_textures = self.load_wall_textures()
        self.sky_image = self.get_texture('resources/textures/sky.png', (WIDTH, HALF_HEIGHT))
        self.sky_offset = 0
        self.blood_screen = self.get_texture('resources/textures/blood_screen.png', RES)
        self.digit_size = 30
        self.digit_images = [self.get_texture(f'resources/textures/digits/{i}.png', [self.digit_size] * 2)
                             for i in range(11)]
        self.digits = dict(zip(map(str, range(11)), self.digit_images))
        self.game_over_image = self.get_texture('resources/textures/game_over.png', RES)
        self.win_image = self.get_texture('resources/textures/win.png', RES)

    def draw(self):
        self.draw_background()
        self.render_game_objects()
        self.draw_player_health()
        self.draw_crosshair()

    def win(self):
        self.screen.blit(self.win_image, (0, 0))

        pg.time.delay(4000)

    def game_over(self):
        self.screen.blit(self.game_over_image, (0, 0))


    def draw_player_health(self):
        health = str(self.game.player.health)
        total_width = len(health) * self.digit_size + self.digits['10'].get_width()  # 计算总宽度
        center_x = (self.screen.get_width() - total_width) // 2  # 计算中心位置的 x 坐标
        # 设定 y 坐标为屏幕的高度减去设置的边距
        bottom_margin = 20  # 为底部保留一些边距
        y_position = self.screen.get_height() - self.digit_size - bottom_margin  # 计算 y 坐标
        
        for i, char in enumerate(health):
            self.screen.blit(self.digits[char], (center_x + i * self.digit_size, y_position))
        
        self.screen.blit(self.digits['10'], (center_x - len(health) * self.digit_size, y_position))

    def player_damage(self):
        self.screen.blit(self.blood_screen, (0, 0))

    def draw_background(self):
        self.sky_offset = (self.sky_offset + 4.5 * self.game.player.rel) % WIDTH
        self.screen.blit(self.sky_image, (-self.sky_offset, 0))
        self.screen.blit(self.sky_image, (-self.sky_offset + WIDTH, 0))
        # floor 填充为图片
        # floor_path = 'resources/textures/background.jpg'
        # floor_texture = pg.image.load(floor_path).convert()
        # floor_texture = pg.transform.scale(floor_texture, (WIDTH, HALF_HEIGHT))
        # self.screen.blit(floor_texture, (0, HALF_HEIGHT))

        pg.draw.rect(self.screen, FLOOR_COLOR, (0, HALF_HEIGHT, WIDTH, HEIGHT))

    def render_game_objects(self):
        list_objects = sorted(self.game.raycasting.objects_to_render, key=lambda t: t[0], reverse=True)
        for depth, image, pos in list_objects:
            self.screen.blit(image, pos)

    @staticmethod
    def get_texture(path, res=(TEXTURE_SIZE, TEXTURE_SIZE)):
        texture = pg.image.load(path).convert_alpha()
        return pg.transform.scale(texture, res)

    def load_wall_textures(self):
        return {
            
            # 1: self.get_texture(r'C:\Users\SOULLaptop\Desktop\CounterStrike\resources\textures\1.png'),  # 墙壁类型1纹理
            # 2: self.get_texture(r'C:\Users\SOULLaptop\Desktop\CounterStrike\resources\textures\2.png'),  # 墙壁类型2纹理
            # 3: self.get_texture(r'C:\Users\SOULLaptop\Desktop\CounterStrike\resources\textures\3.png'),  # 墙壁类型3纹理
            # 4: self.get_texture(r'C:\Users\SOULLaptop\Desktop\CounterStrike\resources\textures\4.png'),  # 墙壁类型4纹理
            # 5: self.get_texture(r'C:\Users\SOULLaptop\Desktop\CounterStrike\resources\textures\5.png'),  # 墙壁类型5纹理
            1: self.get_texture('./resources/textures/1.png'),
            2: self.get_texture('./resources/textures/2.png'),
            3: self.get_texture('./resources/textures/3.png'),
            4: self.get_texture('./resources/textures/4.png'),
            # 5: self.get_texture('./resources/textures/5.png'),
        }
    
    def draw_crosshair(self ,path='resources/sprites/weapon/crosshair.png'):
        # 绘制准星在屏幕中间，图片大小缩小2倍
        crosshair_img = pg.image.load(path).convert_alpha()
        crosshair_img = pg.transform.scale(crosshair_img, (int(crosshair_img.get_width() * 0.5), int(crosshair_img.get_height() * 0.5)))
        self.screen.blit(crosshair_img, (HALF_WIDTH - crosshair_img.get_width() // 2, HALF_HEIGHT - crosshair_img.get_height() // 2))