from sprite_object import *
from random import randint, random

NPC_Death_count = 0
NPC_Death_flag = False

class NPC(AnimatedSprite):
    def __init__(self, game, path='resources/sprites/npc/soldier/0.png', pos=(10.5, 5.5),
                 scale=0.6, shift=0.38, animation_time=180):
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.attack_images = self.get_images(self.path + '/attack')
        self.death_images = self.get_images(self.path + '/death')
        self.idle_images = self.get_images(self.path + '/idle')
        self.pain_images = self.get_images(self.path + '/pain')
        self.walk_images = self.get_images(self.path + '/walk')

        self.attack_dist = randint(3, 6)
        self.speed = 0.02
        self.size = 20
        self.health = 100
        self.attack_damage = 10 # 攻击伤害
        self.accuracy = 0.20 # 命中率
        self.alive = True
        self.pain = False
        self.ray_cast_value = False
        self.frame_counter = 0
        self.player_search_trigger = False

    def update(self):
        self.check_animation_time()
        self.get_sprite()
        self.run_logic()
        # self.draw_ray_cast() # npc射线检测

    def check_wall(self, x, y):
        return (x, y) not in self.game.map.world_map

    def check_wall_collision(self, dx, dy):
        if self.check_wall(int(self.x + dx * self.size), int(self.y)):
            self.x += dx
        if self.check_wall(int(self.x), int(self.y + dy * self.size)):
            self.y += dy

    def movement(self):
        next_pos = self.game.pathfinding.get_path(self.map_pos, self.game.player.map_pos)
        next_x, next_y = next_pos
        # npc寻路，下一个位置
        # pg.draw.rect(self.game.screen, 'blue', (100 * next_x, 100 * next_y, 100, 100))
        if next_pos not in self.game.object_handler.npc_positions:
            angle = math.atan2(next_y + 0.5 - self.y, next_x + 0.5 - self.x)
            dx = math.cos(angle) * self.speed
            dy = math.sin(angle) * self.speed
            self.check_wall_collision(dx, dy)

    def attack(self):
        if self.animation_trigger:
            self.game.sound.npc_shot.play()
            if random() < self.accuracy:
                self.game.player.get_damage(self.attack_damage)

    def animate_death(self):

        if not self.alive:
            if self.game.global_trigger and self.frame_counter < len(self.death_images) - 1:
                self.death_images.rotate(-1)
                self.image = self.death_images[0]
                self.frame_counter += 1

    def animate_pain(self):
        self.animate(self.pain_images)
        if self.animation_trigger:
            self.pain = False

    def check_hit_in_npc(self):
        if self.ray_cast_value and self.game.player.shot:
            if HALF_WIDTH - self.sprite_half_width < self.screen_x < HALF_WIDTH + self.sprite_half_width:
                self.game.sound.npc_pain.play()
                self.game.player.shot = False
                self.pain = True
                self.health -= self.game.weapon.damage
                self.check_health()

    def check_health(self):
        global NPC_Death_flag  # 声明使用全局变量
        global NPC_Death_count  # 声明使用全局变量
        if self.health < 1:
            self.alive = False
            # self.game.sound.npc_death.play()
            NPC_Death_count += 1
            NPC_Death_flag = True
            if NPC_Death_flag == True:
                print(f"NPC_Death_count: {NPC_Death_count}")
                print(NPC_Death_count%7)
                if (NPC_Death_count % 7) == 1:
                    self.game.sound.npc_death.play()
                    NPC_Death_flag = False
                if (NPC_Death_count % 7) == 2:
                    self.game.sound.npc_death2.play()
                    NPC_Death_flag = False
                if (NPC_Death_count % 7) == 3:
                    self.game.sound.npc_death3.play()
                    NPC_Death_flag = False
                if (NPC_Death_count % 7) == 4:
                    self.game.sound.npc_death1.play()
                    NPC_Death_flag = False
                if (NPC_Death_count % 7) == 5:
                    self.game.sound.npc_death1.play()
                    NPC_Death_flag = False
                if (NPC_Death_count % 7) == 6:
                    self.game.sound.npc_death1.play()
                    NPC_Death_flag = False


                if NPC_Death_count == NPC_COUNT:
                    self.game.sound.victory.play()
                    win_image_path = 'resources/textures/win.png'
                    win_image = pg.image.load(win_image_path).convert_alpha()
                    win_image = pg.transform.scale(win_image, (WIDTH, HEIGHT))
                    self.game.screen.blit(win_image, (0, 0))
                    self.game.global_trigger = False

                    NPC_Death_flag = False
                    NPC_Death_count = 0


    def run_logic(self):
        # 检查NPC是否存活
        if self.alive:
            # 进行射线检测以获取与玩家的接触值
            self.ray_cast_value = self.ray_cast_player_npc()
            # 检查NPC是否受到伤害
            self.check_hit_in_npc()

            # 如果NPC受到伤害，执行疼痛动画
            if self.pain:
                self.animate_pain()

            # 如果与玩家接触
            elif self.ray_cast_value:
                # 激活玩家搜索触发器
                self.player_search_trigger = True

                # 检查与玩家的距离是否在攻击范围内
                if self.dist < self.attack_dist:
                    # 执行攻击动画并进行攻击
                    self.animate(self.attack_images)
                    self.attack()
                else:
                    # 超出攻击范围，执行行走动画并进行移动
                    self.animate(self.walk_images)
                    self.movement()

            # 如果已经激活玩家搜索触发器
            elif self.player_search_trigger:
                # 执行行走动画并继续移动
                self.animate(self.walk_images)
                self.movement()

            # 如果不存在上述情况，执行闲置动画
            else:
                self.animate(self.idle_images)
        # 如果NPC不再存活，执行死亡动画
        else:
            self.animate_death()


    @property
    def map_pos(self):
        return int(self.x), int(self.y)

    def ray_cast_player_npc(self):
        if self.game.player.map_pos == self.map_pos:
            return True

        wall_dist_v, wall_dist_h = 0, 0
        player_dist_v, player_dist_h = 0, 0

        ox, oy = self.game.player.pos
        x_map, y_map = self.game.player.map_pos

        ray_angle = self.theta

        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        # horizontals
        y_hor, dy = (y_map + 1, 1) if sin_a > 0 else (y_map - 1e-6, -1)

        depth_hor = (y_hor - oy) / sin_a
        x_hor = ox + depth_hor * cos_a

        delta_depth = dy / sin_a
        dx = delta_depth * cos_a

        for i in range(MAX_DEPTH):
            tile_hor = int(x_hor), int(y_hor)
            if tile_hor == self.map_pos:
                player_dist_h = depth_hor
                break
            if tile_hor in self.game.map.world_map:
                wall_dist_h = depth_hor
                break
            x_hor += dx
            y_hor += dy
            depth_hor += delta_depth

        # verticals
        x_vert, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-6, -1)

        depth_vert = (x_vert - ox) / cos_a
        y_vert = oy + depth_vert * sin_a

        delta_depth = dx / cos_a
        dy = delta_depth * sin_a

        for i in range(MAX_DEPTH):
            tile_vert = int(x_vert), int(y_vert)
            if tile_vert == self.map_pos:
                player_dist_v = depth_vert
                break
            if tile_vert in self.game.map.world_map:
                wall_dist_v = depth_vert
                break
            x_vert += dx
            y_vert += dy
            depth_vert += delta_depth

        player_dist = max(player_dist_v, player_dist_h)
        wall_dist = max(wall_dist_v, wall_dist_h)

        if 0 < player_dist < wall_dist or not wall_dist:
            return True
        return False

    def draw_ray_cast(self):
        pg.draw.circle(self.game.screen, 'red', (MINI_MAP_SIZE * self.x, MINI_MAP_SIZE * self.y), MINI_MAP_PLAYER_SIZE)
        if self.ray_cast_player_npc():
            pg.draw.line(self.game.screen, 'orange', (MINI_MAP_SIZE * self.game.player.x, MINI_MAP_SIZE * self.game.player.y),
                         (MINI_MAP_SIZE * self.x, MINI_MAP_SIZE * self.y), 2)


class SoldierNPC(NPC):
    def __init__(self, game, path='resources/sprites/npc/soldier/0.png', pos=(10.5, 5.5),
                 scale=0.6, shift=0.38, animation_time=180):
        super().__init__(game, path, pos, scale, shift, animation_time)




















