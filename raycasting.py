import pygame as pg
import math
from settings import *


class RayCasting:
    def __init__(self, game):
        self.game = game  # 保存游戏实例
        self.ray_casting_result = []  # 存储射线投射结果
        self.objects_to_render = []  # 存储待渲染的物体
        self.textures = self.game.object_renderer.wall_textures  # 获取墙壁纹理

    # 获取待渲染的物体
    def get_objects_to_render(self):
        self.objects_to_render = []  # 初始化待渲染物体列表
        for ray, values in enumerate(self.ray_casting_result):
            depth, proj_height, texture, offset = values  # 解构射线投射结果

            # 如果投影高度小于屏幕高度，则处理墙壁的段
            if proj_height < HEIGHT:
                wall_column = self.textures[texture].subsurface(
                    offset * (TEXTURE_SIZE - SCALE), 0, SCALE, TEXTURE_SIZE
                )
                wall_column = pg.transform.scale(wall_column, (SCALE, proj_height))  # 按投影高度缩放墙壁块
                wall_pos = (ray * SCALE, HALF_HEIGHT - proj_height // 2)  # 计算墙壁的绘制位置
            else:
                texture_height = TEXTURE_SIZE * HEIGHT / proj_height  # 计算纹理高度
                wall_column = self.textures[texture].subsurface(
                    offset * (TEXTURE_SIZE - SCALE), HALF_TEXTURE_SIZE - texture_height // 2,
                    SCALE, texture_height
                )
                wall_column = pg.transform.scale(wall_column, (SCALE, HEIGHT))  # 按屏幕高度缩放墙壁块
                wall_pos = (ray * SCALE, 0)  # 计算墙壁在屏幕上的位置

            self.objects_to_render.append((depth, wall_column, wall_pos))  # 将结果添加到待渲染列表

    # 射线投射主函数
    def ray_cast(self):
        self.ray_casting_result = []  # 初始化射线投射结果列表
        texture_vert, texture_hor = 1, 1  # 初始化纹理变量
        ox, oy = self.game.player.pos  # 获取玩家当前位置
        x_map, y_map = self.game.player.map_pos  # 获取玩家在地图上的位置

        # 计算初始射线角度
        ray_angle = self.game.player.angle - HALF_FOV + 0.0001
        for ray in range(NUM_RAYS):
            sin_a = math.sin(ray_angle)  # 计算角度的正弦值
            cos_a = math.cos(ray_angle)  # 计算角度的余弦值

            # 处理水平线
            y_hor, dy = (y_map + 1, 1) if sin_a > 0 else (y_map - 1e-6, -1)  # 确定y方向的增量

            depth_hor = (y_hor - oy) / sin_a  # 计算到达水平线的深度
            x_hor = ox + depth_hor * cos_a  # 计算x坐标

            delta_depth = dy / sin_a  # 计算深度变化
            dx = delta_depth * cos_a  # 计算x方向上的变化

            # 水平射线循环
            for i in range(MAX_DEPTH):
                tile_hor = int(x_hor), int(y_hor)  # 获取当前的地图网格
                if tile_hor in self.game.map.world_map:  # 如果遇到墙面
                    texture_hor = self.game.map.world_map[tile_hor]  # 获取墙的纹理
                    break
                x_hor += dx  # 更新x坐标
                y_hor += dy  # 更新y坐标
                depth_hor += delta_depth  # 更新深度

            # 处理垂直线
            x_vert, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-6, -1)  # 确定x方向的增量

            depth_vert = (x_vert - ox) / cos_a  # 计算到达垂直线的深度
            y_vert = oy + depth_vert * sin_a  # 计算y坐标

            delta_depth = dx / cos_a  # 计算深度变化
            dy = delta_depth * sin_a  # 计算y方向上的变化

            # 垂直射线循环
            for i in range(MAX_DEPTH):
                tile_vert = int(x_vert), int(y_vert)  # 获取当前的地图网格
                if tile_vert in self.game.map.world_map:  # 如果遇到墙面
                    texture_vert = self.game.map.world_map[tile_vert]  # 获取墙的纹理
                    break
                x_vert += dx  # 更新x坐标
                y_vert += dy  # 更新y坐标
                depth_vert += delta_depth  # 更新深度

            # 确定深度和纹理偏移量
            if depth_vert < depth_hor:
                depth, texture = depth_vert, texture_vert  # 选择更近的深度
                y_vert %= 1  # 计算纹理偏移
                offset = y_vert if cos_a > 0 else (1 - y_vert)  # 根据方向更新偏移
            else:
                depth, texture = depth_hor, texture_hor
                x_hor %= 1  # 计算纹理偏移
                offset = (1 - x_hor) if sin_a > 0 else x_hor  # 根据方向更新偏移

            # 在迷你地图上绘制射线
            pg.draw.line(self.game.screen, "white", (MINI_MAP_SIZE * ox, MINI_MAP_SIZE * oy), 
                         (MINI_MAP_SIZE * ox + depth * MINI_MAP_SIZE * cos_a, 
                          MINI_MAP_SIZE * oy + depth * MINI_MAP_SIZE * sin_a), 2)

            # 去除鱼眼效应
            depth *= math.cos(self.game.player.angle - ray_angle)

            # 计算投影高度
            proj_height = SCREEN_DIST / (depth + 0.0001)

            # 射线投射结果
            self.ray_casting_result.append((depth, proj_height, texture, offset))  # 保存结果

            ray_angle += DELTA_ANGLE  # 更新射线角度

    # 更新函数
    def update(self):
        self.ray_cast()  # 执行射线投射
        self.get_objects_to_render()  # 获取待渲染物体
