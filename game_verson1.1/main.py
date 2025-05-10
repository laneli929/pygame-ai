import pygame
import sys
import random
from enum import Enum
from config import *
from player import Player
from monster import create_monster
from ui import *
from game_state import GameState


class SlimeNPC:
    """史莱姆NPC类，用于湖北地图的巡逻行为"""

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
        self.state = 'moving'  # 'moving' 或 'waiting'

    def update(self):
        """更新史莱姆NPC的状态和位置"""
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


def load_resources():
    """加载游戏所有资源"""
    try:
        # 加载地图
        village_original = pygame.image.load("liyangcun.jpg").convert()
        hubei_original = pygame.image.load("liyanghubei.jpg").convert()
        hunan_original = pygame.image.load("liyanghunan.jpg").convert()

        village_map = pygame.transform.scale(
            village_original,
            (village_original.get_width() * MAP_SCALE, village_original.get_height() * MAP_SCALE)
        )
        hubei_map = pygame.transform.scale(
            hubei_original,
            (hubei_original.get_width() * MAP_SCALE, hubei_original.get_height() * MAP_SCALE)
        )
        hunan_map = pygame.transform.scale(
            hunan_original,
            (hunan_original.get_width() * MAP_SCALE, hunan_original.get_height() * MAP_SCALE)
        )

        # 加载角色动画
        character_sheet = pygame.image.load("characterss.png").convert()
        character_sheet.set_colorkey(WHITE)
        sprite_width = 384 // 12
        sprite_height = 384 // 8

        animations = {
            'down': [character_sheet.subsurface((frame * sprite_width, 0, sprite_width, sprite_height)) for frame in
                     range(3)],
            'left': [character_sheet.subsurface((frame * sprite_width, sprite_height, sprite_width, sprite_height)) for
                     frame in range(3)],
            'right': [character_sheet.subsurface((frame * sprite_width, sprite_height * 2, sprite_width, sprite_height))
                      for frame in range(3)],
            'up': [character_sheet.subsurface((frame * sprite_width, sprite_height * 3, sprite_width, sprite_height))
                   for frame in range(3)]
        }

        # 加载怪物资源
        slime_sheet = pygame.image.load("shilaimu.png").convert_alpha()
        slime_width = 192 // 4
        slime_height = 256 // 4
        slime_animations = {
            'down': [slime_sheet.subsurface((col * slime_width, 0, slime_width, slime_height)) for col in range(4)],
            'left': [slime_sheet.subsurface((col * slime_width, slime_height, slime_width, slime_height)) for col in
                     range(4)],
            'right': [slime_sheet.subsurface((col * slime_width, slime_height * 2, slime_width, slime_height)) for col
                      in range(4)],
            'up': [slime_sheet.subsurface((col * slime_width, slime_height * 3, slime_width, slime_height)) for col in
                   range(4)]
        }

        # 加载其他资源
        portal_img = pygame.image.load("chuansongmen.png").convert_alpha()
        exclamation_img = pygame.image.load("exclamation.png").convert_alpha()
        battle_bg = pygame.image.load("battle_bg.jpg").convert()
        battle_bg = pygame.transform.scale(battle_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # 创建战斗按钮
        attack_btn = pygame.Surface((150, 50))
        attack_btn.fill(RED)
        defend_btn = pygame.Surface((150, 50))
        defend_btn.fill(BLUE)
        flee_btn = pygame.Surface((150, 50))
        flee_btn.fill(GREEN)

        return {
            'maps': {'village': village_map, 'hubei': hubei_map, 'hunan': hunan_map},
            'animations': animations,
            'slime_animations': slime_animations,
            'portal_img': portal_img,
            'exclamation_img': exclamation_img,
            'battle_bg': battle_bg,
            'attack_btn': attack_btn,
            'defend_btn': defend_btn,
            'flee_btn': flee_btn,
            'sprite_size': (sprite_width, sprite_height),
            'slime_size': (slime_width, slime_height)
        }

    except pygame.error as e:
        print(f"资源加载失败: {e}")
        sys.exit()


def handle_events(game_state, player, current_dialog, dialog_lines):
    """处理所有游戏事件"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False  # 退出游戏

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == GameState.GAME_OVER:
                    return False
                elif game_state == GameState.DIALOG:
                    game_state = GameState.EXPLORING
                else:
                    return False

            elif event.key == pygame.K_r and game_state == GameState.GAME_OVER:
                # 重置游戏状态
                player = Player()
                game_state = GameState.EXPLORING
                return True, player, game_state

            elif event.key == pygame.K_SPACE:
                if game_state == GameState.DIALOG:
                    current_dialog += 1
                    if current_dialog >= len(dialog_lines):
                        game_state = GameState.EXPLORING
                elif game_state in [GameState.BATTLE, GameState.LEVEL_UP]:
                    # 允许通过空格键继续
                    pass

    return True, player, game_state


def update_game_state(keys, player, game_state, current_map, map_type, steps_since_last_battle):
    """更新游戏状态（探索模式下）"""
    dx, dy = 0, 0
    current_direction = 'down'  # 添加默认方向
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        dx = -player.speed
        current_direction = 'left'
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        dx = player.speed
        current_direction = 'right'
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        dy = -player.speed
        current_direction = 'up'
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        dy = player.speed
        current_direction = 'down'

    # 更新玩家位置和遇敌逻辑
    if dx != 0 or dy != 0:
        steps_since_last_battle += 1
        if steps_since_last_battle > 30 and random.random() < 0.02:  # 遇敌概率2%
            area_level = 1 if map_type == "village" else 2 if map_type == "hubei" else 3
            current_monster = create_monster(area_level)
            game_state = GameState.BATTLE
            battle_message = f"遭遇了{current_monster.name}！"
            steps_since_last_battle = 0

    return game_state, current_direction, steps_since_last_battle


def main():
    """主游戏入口"""
    # 初始化
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("村庄探索-大地图模式")
    clock = pygame.time.Clock()

    # 加载资源
    resources = load_resources()
    player = Player()
    game_state = GameState.EXPLORING

    # 初始化游戏状态
    current_map = resources['maps']['village']
    map_type = "village"
    map_width, map_height = current_map.get_size()
    player_x, player_y = map_width // 2, map_height // 2
    camera_x, camera_y = 0, 0
    current_direction = 'down'
    current_frame = 0
    animation_counter = 0
    steps_since_last_battle = 0  # <-- 添加这行修复错误

    # 战斗相关
    current_monster = None
    battle_message = ""
    slime_frame = 0
    is_monster_attacking = False

    # NPC和对话
    officer_pos = (190, 803)
    officer_frame_index = 0
    show_exclamation = False
    current_dialog = 0
    dialog_lines = [
        "治安官：最近村里不太平...",
        "治安官：有村民报告看到可疑人物",
        "治安官：如果你发现什么可疑情况，请立即告诉我"
    ]

    # 主游戏循环
    running = True
    while running:
        # 处理事件
        event_result = handle_events(game_state, player, current_dialog, dialog_lines)
        if isinstance(event_result, tuple):
            running, player, game_state = event_result
        else:
            running = event_result
        if not running:
            break

        # 根据游戏状态更新
        if game_state == GameState.EXPLORING:
            keys = pygame.key.get_pressed()
            game_state, current_direction, steps_since_last_battle = update_game_state(
                keys, player, game_state, current_map, map_type, steps_since_last_battle
            )

            # 更新动画帧
            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]:
                animation_counter += 1
                if animation_counter >= ANIMATION_SPEED:
                    animation_counter = 0
                    current_frame = (current_frame + 1) % len(resources['animations'][current_direction])
            else:
                current_frame = 0

            # 检测与治安官的距离
            officer_distance = ((player_x - officer_pos[0]) ** 2 + (player_y - officer_pos[1]) ** 2) ** 0.5
            show_exclamation = officer_distance < 50 and map_type == "village"

        # 渲染
        screen.fill(BLACK)
        if game_state == GameState.EXPLORING:
            # 绘制探索模式界面
            screen.blit(current_map, (camera_x, camera_y))
            # 绘制角色和UI
            draw_hud(screen, player, map_type)
        elif game_state == GameState.BATTLE:
            # 绘制战斗界面
            draw_battle_screen(
                screen, player, current_monster, resources['battle_bg'],
                resources['attack_btn'], resources['defend_btn'], resources['flee_btn'],
                resources['animations'], current_direction, current_frame,
                resources['slime_animations'], slime_frame, is_monster_attacking,
                battle_message
            )

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()