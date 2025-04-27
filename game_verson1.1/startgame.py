import pygame
import sys
import random
import math
import time
from enum import Enum

# 初始化
pygame.init()

# 屏幕设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("村庄探索-大地图模式")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
BROWN = (139, 69, 19)

# 帧率
clock = pygame.time.Clock()
FPS = 60

# 字体
font_small = pygame.font.SysFont("simhei", 20)
font_medium = pygame.font.SysFont("simhei", 24)
font_large = pygame.font.SysFont("simhei", 32)


# 游戏状态
class GameState(Enum):
    EXPLORING = 1
    BATTLE = 2
    DIALOG = 3
    GAME_OVER = 4
    LEVEL_UP = 5


def load_resources():
    """加载所有资源"""
    try:
        # 加载地图
        village_original = pygame.image.load("liyangcun.jpg").convert()
        hubei_original = pygame.image.load("liyanghubei.jpg").convert()
        hunan_original = pygame.image.load("liyanghunan.jpg").convert()
        MAP_SCALE = 4
        village_map = pygame.transform.scale(village_original,
                                             (village_original.get_width() * MAP_SCALE,
                                              village_original.get_height() * MAP_SCALE))
        hubei_map = pygame.transform.scale(hubei_original,
                                           (hubei_original.get_width() * MAP_SCALE,
                                            hubei_original.get_height() * MAP_SCALE))
        hunan_map = pygame.transform.scale(hunan_original,
                                           (hunan_original.get_width() * MAP_SCALE,
                                            hunan_original.get_height() * MAP_SCALE))

        # 角色
        character_sheet = pygame.image.load("characterss.png").convert()
        character_sheet.set_colorkey(WHITE)
        sprite_width = 384 // 12
        sprite_height = 384 // 8

        animations = {
            'down': [character_sheet.subsurface((frame * sprite_width, 0 * sprite_height, sprite_width, sprite_height))
                     for frame in range(3)],
            'left': [character_sheet.subsurface((frame * sprite_width, 1 * sprite_height, sprite_width, sprite_height))
                     for frame in range(3)],
            'right': [character_sheet.subsurface((frame * sprite_width, 2 * sprite_height, sprite_width, sprite_height))
                      for frame in range(3)],
            'up': [character_sheet.subsurface((frame * sprite_width, 3 * sprite_height, sprite_width, sprite_height))
                   for frame in range(3)]
        }

        # 治安官动画
        officer_frames = [
            character_sheet.subsurface((3 * sprite_width, 4 * sprite_height, sprite_width, sprite_height)),
            character_sheet.subsurface((4 * sprite_width, 4 * sprite_height, sprite_width, sprite_height))
        ]

        slime_sheet = pygame.image.load("shilaimu.png").convert_alpha()
        slime_width = 192 // 4
        slime_height = 256 // 4
        slime_animations = {
            'down': [slime_sheet.subsurface((col * slime_width, 0 * slime_height, slime_width, slime_height)) for col in
                     range(4)],
            'left': [slime_sheet.subsurface((col * slime_width, 1 * slime_height, slime_width, slime_height)) for col in
                     range(4)],
            'right': [slime_sheet.subsurface((col * slime_width, 2 * slime_height, slime_width, slime_height)) for col
                      in range(4)],
            'up': [slime_sheet.subsurface((col * slime_width, 3 * slime_height, slime_width, slime_height)) for col in
                   range(4)]
        }

        portal_img = pygame.image.load("chuansongmen.png").convert_alpha()
        exclamation_img = pygame.image.load("exclamation.png").convert_alpha()

        battle_bg = pygame.image.load("battle_bg.jpg").convert()
        battle_bg = pygame.transform.scale(battle_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

        attack_btn_img = pygame.Surface((150, 50))
        attack_btn_img.fill(RED)
        defend_btn_img = pygame.Surface((150, 50))
        defend_btn_img.fill(BLUE)
        flee_btn_img = pygame.Surface((150, 50))
        flee_btn_img.fill(GREEN)

        return (village_map, hubei_map, hunan_map, animations, sprite_width, sprite_height,
                MAP_SCALE, portal_img, officer_frames, exclamation_img, slime_animations,
                slime_width, slime_height, battle_bg, attack_btn_img, defend_btn_img, flee_btn_img)

    except pygame.error as e:
        print(f"资源加载失败: {e}")
        sys.exit()


class Player:
    def __init__(self):
        self.max_hp = 100
        self.hp = 100
        self.attack = 15
        self.defense = 10
        self.speed = 5
        self.exp = 0
        self.level = 1
        self.exp_to_level = 100
        self.gold = 50  # 新增金币系统

    def level_up(self):
        self.level += 1
        self.max_hp += 20
        self.hp = self.max_hp
        self.attack += 5
        self.defense += 3
        self.exp_to_level = int(self.exp_to_level * 1.5)
        return True

    def gain_exp(self, amount):
        self.exp += amount
        if self.exp >= self.exp_to_level:
            self.exp -= self.exp_to_level
            return self.level_up()
        return False


class Monster:
    def __init__(self, name, max_hp, attack, defense, speed, exp_reward, gold_reward):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward  # 新增金币奖励

    def take_damage(self, damage):
        actual_damage = max(1, damage)  # 确保至少造成1点伤害
        self.hp -= actual_damage
        if self.hp < 0:
            self.hp = 0
        return self.hp <= 0, actual_damage


def create_monster(area_level):
    if area_level == 1:
        return Monster("小史莱姆", 30, 8, 5, 3, 20, 10)
    elif area_level == 2:
        return Monster("大史莱姆", 50, 12, 8, 4, 35, 20)
    else:
        return Monster("史莱姆王", 80, 18, 12, 5, 60, 40)


def draw_health_bar(surface, x, y, width, height, current, max_val, color):
    ratio = min(1.0, max(0.0, current / max_val))  # 确保比例在0-1之间
    pygame.draw.rect(surface, GRAY, (x, y, width, height))
    pygame.draw.rect(surface, color, (x, y, width * ratio, height))


def draw_battle_screen(screen, player, monster, battle_bg, attack_btn, defend_btn, flee_btn,
                       player_animations, current_direction, current_frame,
                       slime_animations, slime_frame, is_monster_attacking=False,
                       message=None):
    screen.blit(battle_bg, (0, 0))

    monster_x, monster_y = (100, 100)
    if is_monster_attacking:
        monster_x = SCREEN_WIDTH - 250
        monster_y = SCREEN_HEIGHT - 200

    screen.blit(slime_animations['down'][slime_frame % 2], (monster_x, monster_y))

    char_x = SCREEN_WIDTH - 100 - player_animations[current_direction][current_frame].get_width()
    char_y = SCREEN_HEIGHT - 100 - player_animations[current_direction][current_frame].get_height()
    screen.blit(player_animations[current_direction][current_frame], (char_x, char_y))

    # 绘制血条和信息
    draw_health_bar(screen, 50, 50, 200, 20, player.hp, player.max_hp, GREEN)
    player_text = font_medium.render(f"玩家 Lv.{player.level} (HP: {player.hp}/{player.max_hp})", True, WHITE)
    screen.blit(player_text, (50, 30))

    draw_health_bar(screen, SCREEN_WIDTH - 250, 50, 200, 20, monster.hp, monster.max_hp, RED)
    monster_text = font_medium.render(f"{monster.name} (HP: {monster.hp}/{monster.max_hp})", True, WHITE)
    screen.blit(monster_text, (SCREEN_WIDTH - 250, 30))

    # 按钮
    screen.blit(attack_btn, (50, SCREEN_HEIGHT - 150))
    attack_text = font_medium.render("攻击", True, WHITE)
    screen.blit(attack_text, (125 - attack_text.get_width() // 2, SCREEN_HEIGHT - 135))

    screen.blit(defend_btn, (SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 150))
    defend_text = font_medium.render("防御", True, WHITE)
    screen.blit(defend_text, (SCREEN_WIDTH // 2 - defend_text.get_width() // 2, SCREEN_HEIGHT - 135))

    screen.blit(flee_btn, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 150))
    flee_text = font_medium.render("逃跑", True, WHITE)
    screen.blit(flee_text, (SCREEN_WIDTH - 125 - flee_text.get_width() // 2, SCREEN_HEIGHT - 135))

    # 消息
    if message:
        message_lines = message.split('\n')
        message_height = len(message_lines) * 30 + 20

        message_bg = pygame.Surface((SCREEN_WIDTH - 100, message_height), pygame.SRCALPHA)
        message_bg.fill((0, 0, 0, 200))
        screen.blit(message_bg, (50, SCREEN_HEIGHT - message_height - 40))

        for i, line in enumerate(message_lines):
            message_text = font_medium.render(line, True, WHITE)
            screen.blit(message_text, (70, SCREEN_HEIGHT - message_height - 20 + i * 30))

        hint_text = font_small.render("按空格继续...", True, (200, 200, 200))
        screen.blit(hint_text, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 50))


def draw_level_up_screen(screen, player, font_large, font_medium):
    """绘制升级界面"""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    title = font_large.render("升级!", True, YELLOW)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

    stats = [
        f"等级: {player.level - 1} → {player.level}",
        f"最大HP: {player.max_hp - 20} → {player.max_hp}",
        f"攻击力: {player.attack - 5} → {player.attack}",
        f"防御力: {player.defense - 3} → {player.defense}"
    ]

    for i, stat in enumerate(stats):
        stat_text = font_medium.render(stat, True, WHITE)
        screen.blit(stat_text, (SCREEN_WIDTH // 2 - stat_text.get_width() // 2, 200 + i * 40))

    continue_text = font_medium.render("按空格继续...", True, (200, 200, 200))
    screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT - 100))


def draw_game_over_screen(screen, font_large, font_medium):
    """绘制游戏结束界面"""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))
    screen.blit(overlay, (0, 0))

    title = font_large.render("游戏结束", True, RED)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))

    options = [
        "按R键重新开始游戏",
        "按ESC键退出游戏"
    ]

    for i, option in enumerate(options):
        option_text = font_medium.render(option, True, WHITE)
        screen.blit(option_text, (SCREEN_WIDTH // 2 - option_text.get_width() // 2, 300 + i * 50))


def main():
    (village_map, hubei_map, hunan_map, animations, sprite_width, sprite_height, MAP_SCALE,
     portal_img, officer_frames, exclamation_img, slime_animations, slime_width, slime_height,
     battle_bg, attack_btn_img, defend_btn_img, flee_btn_img) = load_resources()

    player = Player()
    game_state = GameState.EXPLORING

    # 地图相关设置
    current_map = village_map
    map_width, map_height = current_map.get_size()
    player_x = map_width // 2
    player_y = map_height // 2
    camera_x = 0
    camera_y = 0
    speed = 5

    # 角色动画
    current_direction = 'down'
    current_frame = 0
    animation_counter = 0
    animation_speed = 8

    # 战斗相关
    in_battle = False
    current_monster = None
    battle_message = ""
    waiting_for_input = False
    player_defending = False
    monster_defending = False
    steps_since_last_battle = 0
    battle_chances = {
        "village": 0,
        "hubei": 0,
        "hunan": 0
    }
    area_level = 1  # 1=村庄, 2=湖北, 3=湖南

    # 史莱姆动画
    slime_frame = 0
    slime_animation_counter = 0
    is_monster_attacking = False
    monster_attack_timer = 0

    # 史莱姆NPC (湖北地图)
    class Slime:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.speed = 1.5
            self.direction = 'down'
            self.frame_index = 0
            self.animation_counter = 0
            self.move_counter = 0
            self.move_duration = 60
            self.wait_duration = 30
            self.state = 'moving'

        def update(self):
            if self.state == 'moving':
                self.move_counter += 1
                if self.move_counter >= self.move_duration:
                    self.state = 'waiting'
                    self.move_counter = 0
                    self.direction = random.choice(['down', 'left', 'right', 'up'])
            else:
                self.move_counter += 1
                if self.move_counter >= self.wait_duration:
                    self.state = 'moving'
                    self.move_counter = 0

            if self.state == 'moving':
                if self.direction == 'down':
                    self.y += self.speed
                elif self.direction == 'up':
                    self.y -= self.speed
                elif self.direction == 'left':
                    self.x -= self.speed
                elif self.direction == 'right':
                    self.x += self.speed

            self.animation_counter += 1
            if self.animation_counter >= 10:
                self.animation_counter = 0
                self.frame_index = (self.frame_index + 1) % 4

    # 创建史莱姆实例 (湖北地图)
    slimes = []
    if hubei_map:
        slimes.append(Slime(500, 700))
        slimes.append(Slime(1000, 800))

    # 治安官设置
    officer_pos = (190, 803)
    officer_frame_index = 0
    officer_animation_counter = 0
    officer_animation_speed = 15
    show_exclamation = False
    current_dialog = 0
    dialog_lines = [
        "治安官：最近村里不太平...",
        "治安官：有村民报告看到可疑人物",
        "治安官：如果你发现什么可疑情况，请立即告诉我"
    ]

    # 传送门设置
    portals = {
        "village": {
            "pos": [(751, 79), (1470, 1173)],
            "target": ["hubei", "hunan"]
        },
        "hubei": {
            "pos": [(335, 1187)],
            "target": ["village"]
        },
        "hunan": {
            "pos": [(109, 1104)],
            "target": ["village"]
        }
    }

    # 地图引用字典
    maps = {
        "village": village_map,
        "hubei": hubei_map,
        "hunan": hunan_map
    }

    # 获取当前地图类型
    def get_map_type(map_obj):
        if map_obj == village_map:
            return "village"
        elif map_obj == hubei_map:
            return "hubei"
        else:
            return "hunan"

    portal_radius = 20
    portal_cooldown = 0

    running = True
    while running:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state == GameState.GAME_OVER:
                        running = False
                    elif game_state == GameState.DIALOG:
                        game_state = GameState.EXPLORING
                    else:
                        running = False
                elif event.key == pygame.K_r and game_state == GameState.GAME_OVER:
                    # 重新开始游戏
                    player = Player()
                    game_state = GameState.EXPLORING
                    current_map = village_map
                    map_width, map_height = current_map.get_size()
                    player_x = map_width // 2
                    player_y = map_height // 2
                    camera_x, camera_y = 0, 0
                elif event.key == pygame.K_SPACE:
                    if game_state == GameState.DIALOG:
                        current_dialog += 1
                        if current_dialog >= len(dialog_lines):
                            game_state = GameState.EXPLORING
                    elif game_state == GameState.BATTLE and waiting_for_input:
                        waiting_for_input = False
                        battle_message = ""
                    elif game_state == GameState.LEVEL_UP:
                        game_state = GameState.EXPLORING
                elif event.key == pygame.K_SPACE and show_exclamation and game_state == GameState.EXPLORING:
                    game_state = GameState.DIALOG
                    current_dialog = 0

            elif event.type == pygame.MOUSEBUTTONDOWN and game_state == GameState.BATTLE and not waiting_for_input:
                mouse_pos = pygame.mouse.get_pos()
                if 50 <= mouse_pos[0] <= 200 and SCREEN_HEIGHT - 150 <= mouse_pos[1] <= SCREEN_HEIGHT - 100:
                    damage = max(1, player.attack - (current_monster.defense // 2 if monster_defending else 0))
                    is_dead, actual_damage = current_monster.take_damage(damage)
                    battle_message = f"你对{current_monster.name}造成了{actual_damage}点伤害！"

                    if is_dead:
                        exp_gained = current_monster.exp_reward
                        leveled_up = player.gain_exp(exp_gained)
                        player.gold += current_monster.gold_reward  # 获得金币奖励
                        battle_message += f"\n击败了{current_monster.name}，获得{exp_gained}经验值和{current_monster.gold_reward}金币！"
                        if leveled_up:
                            game_state = GameState.LEVEL_UP
                        waiting_for_input = True
                    else:
                        monster_damage = max(1, current_monster.attack - (player.defense if player_defending else 0))
                        player.hp = max(0, player.hp - monster_damage)  # 确保HP不低于0
                        battle_message += f"\n{current_monster.name}对你造成了{monster_damage}点伤害！"
                        if player.hp <= 0:
                            battle_message += "\n你被打败了！"
                            game_state = GameState.GAME_OVER
                        waiting_for_input = True

                    player_defending = False
                    monster_defending = False

                elif SCREEN_WIDTH // 2 - 75 <= mouse_pos[0] <= SCREEN_WIDTH // 2 + 75 and SCREEN_HEIGHT - 150 <= \
                        mouse_pos[1] <= SCREEN_HEIGHT - 100:
                    player_defending = True
                    battle_message = "你采取了防御姿态！"

                    if random.random() < 0.5:
                        monster_defending = True
                        battle_message += f"\n{current_monster.name}也采取了防御姿态！"
                    else:
                        monster_damage = max(1, current_monster.attack - player.defense)
                        player.hp = max(0, player.hp - monster_damage)
                        battle_message += f"\n{current_monster.name}对你造成了{monster_damage}点伤害！"
                        if player.hp <= 0:
                            battle_message += "\n你被打败了！"
                            game_state = GameState.GAME_OVER

                    waiting_for_input = True

                elif SCREEN_WIDTH - 200 <= mouse_pos[0] <= SCREEN_WIDTH - 50 and SCREEN_HEIGHT - 150 <= mouse_pos[
                    1] <= SCREEN_HEIGHT - 100:
                    if random.random() < 0.7:
                        battle_message = "你成功逃跑了！"
                        game_state = GameState.EXPLORING
                    else:
                        battle_message = "逃跑失败！"
                        monster_damage = max(1, current_monster.attack - (player.defense if player_defending else 0))
                        player.hp = max(0, player.hp - monster_damage)
                        battle_message += f"\n{current_monster.name}对你造成了{monster_damage}点伤害！"
                        if player.hp <= 0:
                            battle_message += "\n你被打败了！"
                            game_state = GameState.GAME_OVER

                    waiting_for_input = True
                    player_defending = False

        # 根据游戏状态更新
        if game_state == GameState.BATTLE:
            # 更新史莱姆动画
            slime_animation_counter += 1
            if slime_animation_counter >= 15:
                slime_animation_counter = 0
                slime_frame += 1

            # 更新怪物攻击动画
            if is_monster_attacking:
                monster_attack_timer += 1
                if monster_attack_timer >= 10:
                    is_monster_attacking = False
                    monster_attack_timer = 0

            # 绘制战斗界面
            draw_battle_screen(screen, player, current_monster, battle_bg,
                               attack_btn_img, defend_btn_img, flee_btn_img,
                               animations, current_direction, current_frame,
                               slime_animations, slime_frame, is_monster_attacking,
                               battle_message if battle_message else None)

            pygame.display.flip()
            clock.tick(FPS)
            continue
        elif game_state == GameState.LEVEL_UP:
            draw_level_up_screen(screen, player, font_large, font_medium)
            pygame.display.flip()
            clock.tick(FPS)
            continue
        elif game_state == GameState.GAME_OVER:
            draw_game_over_screen(screen, font_large, font_medium)
            pygame.display.flip()
            clock.tick(FPS)
            continue
        elif game_state == GameState.DIALOG:
            # 绘制对话框
            screen.fill(BLACK)
            if current_map:
                screen.blit(current_map, (camera_x, camera_y))

            # 绘制角色和NPC
            char_screen_x = player_x + camera_x - sprite_width // 2
            char_screen_y = player_y + camera_y - sprite_height // 2
            screen.blit(animations[current_direction][current_frame], (char_screen_x, char_screen_y))

            officer_screen_x = officer_pos[0] + camera_x - sprite_width // 2
            officer_screen_y = officer_pos[1] + camera_y - sprite_height // 2
            screen.blit(officer_frames[officer_frame_index], (officer_screen_x, officer_screen_y))

            # 绘制对话框
            dialog_bg = pygame.Surface((SCREEN_WIDTH - 100, 120), pygame.SRCALPHA)
            dialog_bg.fill((0, 0, 0, 200))
            screen.blit(dialog_bg, (50, SCREEN_HEIGHT - 140))

            text = font_medium.render(dialog_lines[current_dialog], True, WHITE)
            screen.blit(text, (70, SCREEN_HEIGHT - 120))

            hint = font_medium.render("按空格继续...", True, (200, 200, 200))
            screen.blit(hint, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 80))

            pygame.display.flip()
            clock.tick(FPS)
            continue

        # 探索状态更新
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -speed
            current_direction = 'left'
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = speed
            current_direction = 'right'
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -speed
            current_direction = 'up'
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = speed
            current_direction = 'down'

        # 更新玩家位置
        new_x = player_x + dx
        new_y = player_y + dy
        new_x = max(sprite_width // 2, min(map_width - sprite_width // 2, new_x))
        new_y = max(sprite_height // 2, min(map_height - sprite_height // 2, new_y))

        # 更新动画
        moving = dx != 0 or dy != 0
        if moving:
            animation_counter += 1
            if animation_counter >= animation_speed:
                animation_counter = 0
                current_frame = (current_frame + 1) % len(animations[current_direction])

            # 更新步数计数器
            steps_since_last_battle += 1

            # 检查是否遇敌
            current_map_type = get_map_type(current_map)
            if steps_since_last_battle > 30 and random.random() < battle_chances[current_map_type]:
                if current_map_type == "village":
                    area_level = 1
                elif current_map_type == "hubei":
                    area_level = 2
                else:
                    area_level = 3

                current_monster = create_monster(area_level)
                game_state = GameState.BATTLE
                battle_message = f"遭遇了{current_monster.name}！"
                waiting_for_input = False
                steps_since_last_battle = 0
        else:
            current_frame = 0

        # 检测传送门碰撞
        current_map_type = get_map_type(current_map)
        for i, portal_pos in enumerate(portals[current_map_type]["pos"]):
            distance = ((new_x - portal_pos[0]) ** 2 + (new_y - portal_pos[1]) ** 2) ** 0.5
            if distance < portal_radius and portal_cooldown == 0:
                target_map = portals[current_map_type]["target"][i]
                current_map = maps[target_map]
                map_width, map_height = current_map.get_size()
                player_x = map_width // 2
                player_y = map_height // 2
                camera_x, camera_y = 0, 0
                portal_cooldown = 60
                break
        else:
            player_x, player_y = new_x, new_y

        # 计算相机偏移
        screen_relative_x = player_x + camera_x
        screen_relative_y = player_y + camera_y

        if map_width > SCREEN_WIDTH:
            if screen_relative_x < SCREEN_WIDTH * 0.3:
                camera_x += (SCREEN_WIDTH * 0.3 - screen_relative_x)
            elif screen_relative_x > SCREEN_WIDTH * 0.7:
                camera_x -= (screen_relative_x - SCREEN_WIDTH * 0.7)
            camera_x = max(SCREEN_WIDTH - map_width, min(0, camera_x))

        if map_height > SCREEN_HEIGHT:
            if screen_relative_y < SCREEN_HEIGHT * 0.3:
                camera_y += (SCREEN_HEIGHT * 0.3 - screen_relative_y)
            elif screen_relative_y > SCREEN_HEIGHT * 0.7:
                camera_y -= (screen_relative_y - SCREEN_HEIGHT * 0.7)
            camera_y = max(SCREEN_HEIGHT - map_height, min(0, camera_y))

        # 检测与治安官的距离
        officer_distance = ((player_x - officer_pos[0]) ** 2 + (player_y - officer_pos[1]) ** 2) ** 0.5
        show_exclamation = officer_distance < 50 and current_map == village_map and game_state == GameState.EXPLORING

        # 更新治安官动画
        officer_animation_counter += 1
        if officer_animation_counter >= officer_animation_speed:
            officer_animation_counter = 0
            officer_frame_index = 1 - officer_frame_index

        # 更新史莱姆NPC (只在湖北地图)
        if current_map == hubei_map:
            for slime in slimes:
                slime.update()
                slime.x = max(slime_width // 2, min(hubei_map.get_width() - slime_width // 2, slime.x))
                slime.y = max(slime_height // 2, min(hubei_map.get_height() - slime_height // 2, slime.y))

        # 传送门冷却
        if portal_cooldown > 0:
            portal_cooldown -= 1

        # 绘制
        screen.fill(BLACK)
        screen.blit(current_map, (camera_x, camera_y))

        # 绘制史莱姆NPC (只在湖北地图)
        if current_map == hubei_map:
            for slime in slimes:
                screen.blit(
                    slime_animations[slime.direction][slime.frame_index],
                    (slime.x - slime_width // 2 + camera_x,
                     slime.y - slime_height // 2 + camera_y)
                )

        # 绘制传送门
        current_map_type = get_map_type(current_map)
        for portal_pos in portals[current_map_type]["pos"]:
            screen.blit(
                portal_img,
                (portal_pos[0] - portal_img.get_width() // 2 + camera_x,
                 portal_pos[1] - portal_img.get_height() // 2 + camera_y)
            )

        # 绘制治安官和感叹号
        if current_map == village_map:
            screen.blit(
                officer_frames[officer_frame_index],
                (officer_pos[0] - sprite_width // 2 + camera_x,
                 officer_pos[1] - sprite_height // 2 + camera_y)
            )

            if show_exclamation:
                screen.blit(
                    exclamation_img,
                    (officer_pos[0] - exclamation_img.get_width() // 2 + camera_x,
                     officer_pos[1] - sprite_height + camera_y)
                )

        # 绘制角色
        char_screen_x = player_x + camera_x - sprite_width // 2
        char_screen_y = player_y + camera_y - sprite_height // 2
        screen.blit(animations[current_direction][current_frame], (char_screen_x, char_screen_y))

        # 绘制玩家状态
        status_bg = pygame.Surface((200, 80), pygame.SRCALPHA)
        status_bg.fill((0, 0, 0, 150))
        screen.blit(status_bg, (10, 10))

        level_text = font_small.render(f"等级: {player.level}", True, WHITE)
        hp_text = font_small.render(f"HP: {player.hp}/{player.max_hp}", True, WHITE)
        exp_text = font_small.render(f"经验: {player.exp}/{player.exp_to_level}", True, WHITE)
        gold_text = font_small.render(f"金币: {player.gold}", True, YELLOW)

        screen.blit(level_text, (20, 15))
        screen.blit(hp_text, (20, 35))
        screen.blit(exp_text, (20, 55))
        screen.blit(gold_text, (20, 75))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()