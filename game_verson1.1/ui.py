import pygame
from config import *

# 初始化字体（如果config.py中未定义）
if 'font_small' not in globals():
    pygame.font.init()
    font_small = pygame.font.SysFont("simhei", 20)
    font_medium = pygame.font.SysFont("simhei", 24)
    font_large = pygame.font.SysFont("simhei", 32)


def draw_health_bar(surface, x, y, width, height, current, max_val, color):
    """绘制血条"""
    ratio = min(1.0, max(0.0, current / max_val))  # 确保比例在0-1之间
    pygame.draw.rect(surface, GRAY, (x, y, width, height))
    pygame.draw.rect(surface, color, (x, y, width * ratio, height))


def draw_battle_screen(screen, player, monster, battle_bg, attack_btn, defend_btn, flee_btn,
                       player_animations, current_direction, current_frame,
                       slime_animations, slime_frame, is_monster_attacking=False,
                       message=None):
    """
    绘制战斗界面
    :param is_monster_attacking: 是否播放怪物攻击动画
    :param message: 多行消息（用\n分隔）
    """
    # 绘制背景
    screen.blit(battle_bg, (0, 0))

    # 动态调整怪物位置（攻击动画）
    monster_x, monster_y = (100, 100)
    if is_monster_attacking:
        monster_x = SCREEN_WIDTH - 250
        monster_y = SCREEN_HEIGHT - 200

    # 绘制怪物和玩家角色
    screen.blit(slime_animations['down'][slime_frame % 4], (monster_x, monster_y))

    char_x = SCREEN_WIDTH - 100 - player_animations[current_direction][current_frame].get_width()
    char_y = SCREEN_HEIGHT - 100 - player_animations[current_direction][current_frame].get_height()
    screen.blit(player_animations[current_direction][current_frame], (char_x, char_y))

    # ---- 绘制血条和信息 ----
    # 玩家血条
    draw_health_bar(screen, 50, 50, 200, 20, player.hp, player.max_hp, GREEN)
    player_text = font_medium.render(f"玩家 Lv.{player.level} (HP: {player.hp}/{player.max_hp})", True, WHITE)
    screen.blit(player_text, (50, 30))

    # 怪物血条
    draw_health_bar(screen, SCREEN_WIDTH - 250, 50, 200, 20, monster.hp, monster.max_hp, RED)
    monster_text = font_medium.render(f"{monster.name} (HP: {monster.hp}/{monster.max_hp})", True, WHITE)
    screen.blit(monster_text, (SCREEN_WIDTH - 250, 30))

    # ---- 绘制战斗按钮 ----
    # 攻击按钮
    screen.blit(attack_btn, (50, SCREEN_HEIGHT - 150))
    attack_text = font_medium.render("攻击", True, WHITE)
    screen.blit(attack_text, (125 - attack_text.get_width() // 2, SCREEN_HEIGHT - 135))

    # 防御按钮
    screen.blit(defend_btn, (SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 150))
    defend_text = font_medium.render("防御", True, WHITE)
    screen.blit(defend_text, (SCREEN_WIDTH // 2 - defend_text.get_width() // 2, SCREEN_HEIGHT - 135))

    # 逃跑按钮
    screen.blit(flee_btn, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 150))
    flee_text = font_medium.render("逃跑", True, WHITE)
    screen.blit(flee_text, (SCREEN_WIDTH - 125 - flee_text.get_width() // 2, SCREEN_HEIGHT - 135))

    # ---- 绘制战斗消息 ----
    if message:
        message_lines = message.split('\n')
        message_height = len(message_lines) * 30 + 20

        # 半透明消息背景
        message_bg = pygame.Surface((SCREEN_WIDTH - 100, message_height), pygame.SRCALPHA)
        message_bg.fill((0, 0, 0, 200))
        screen.blit(message_bg, (50, SCREEN_HEIGHT - message_height - 40))

        # 逐行绘制消息
        for i, line in enumerate(message_lines):
            message_text = font_medium.render(line, True, WHITE)
            screen.blit(message_text, (70, SCREEN_HEIGHT - message_height - 20 + i * 30))

        # 提示继续文字
        hint_text = font_small.render("按空格继续...", True, (200, 200, 200))
        screen.blit(hint_text, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 50))


def draw_dialog(screen, dialog_lines, current_dialog, camera_x, camera_y, npc_image, npc_pos):
    """
    绘制对话框界面
    :param dialog_lines: 所有对话文本列表
    :param current_dialog: 当前显示的对话索引
    """
    # 绘制NPC
    screen.blit(npc_image, (npc_pos[0] + camera_x, npc_pos[1] + camera_y))

    # 对话框背景
    dialog_bg = pygame.Surface((SCREEN_WIDTH - 100, 120), pygame.SRCALPHA)
    dialog_bg.fill((0, 0, 0, 200))
    screen.blit(dialog_bg, (50, SCREEN_HEIGHT - 140))

    # 对话文本
    text = font_medium.render(dialog_lines[current_dialog], True, WHITE)
    screen.blit(text, (70, SCREEN_HEIGHT - 120))

    # 继续提示
    hint = font_medium.render("按空格继续...", True, (200, 200, 200))
    screen.blit(hint, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 80))


def draw_level_up_screen(screen, player):
    """绘制升级界面"""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    # 标题
    title = font_large.render("升级!", True, YELLOW)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

    # 属性变化列表
    stats = [
        f"等级: {player.level - 1} → {player.level}",
        f"最大HP: {player.max_hp - 20} → {player.max_hp}",
        f"攻击力: {player.attack - 5} → {player.attack}",
        f"防御力: {player.defense - 3} → {player.defense}"
    ]

    # 绘制每条属性变化
    for i, stat in enumerate(stats):
        stat_text = font_medium.render(stat, True, WHITE)
        screen.blit(stat_text, (SCREEN_WIDTH // 2 - stat_text.get_width() // 2, 200 + i * 40))

    # 继续提示
    continue_text = font_medium.render("按空格继续...", True, (200, 200, 200))
    screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT - 100))


def draw_game_over_screen(screen):
    """绘制游戏结束界面"""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))
    screen.blit(overlay, (0, 0))

    # 标题
    title = font_large.render("游戏结束", True, RED)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))

    # 选项
    options = [
        "按R键重新开始游戏",
        "按ESC键退出游戏"
    ]
    for i, option in enumerate(options):
        option_text = font_medium.render(option, True, WHITE)
        screen.blit(option_text, (SCREEN_WIDTH // 2 - option_text.get_width() // 2, 300 + i * 50))


def draw_hud(screen, player, map_name):
    """绘制游戏主界面的HUD（状态栏）"""
    # 半透明背景
    status_bg = pygame.Surface((200, 100), pygame.SRCALPHA)
    status_bg.fill((0, 0, 0, 150))
    screen.blit(status_bg, (10, 10))

    # 玩家状态信息
    level_text = font_small.render(f"等级: {player.level}", True, WHITE)
    hp_text = font_small.render(f"HP: {player.hp}/{player.max_hp}", True, WHITE)
    exp_text = font_small.render(f"经验: {player.exp}/{player.exp_to_level}", True, WHITE)
    gold_text = font_small.render(f"金币: {player.gold}", True, YELLOW)
    map_text = font_small.render(f"区域: {map_name}", True, (200, 200, 255))

    # 绘制文本
    screen.blit(level_text, (20, 15))
    screen.blit(hp_text, (20, 35))
    screen.blit(exp_text, (20, 55))
    screen.blit(gold_text, (20, 75))
    screen.blit(map_text, (20, 95))