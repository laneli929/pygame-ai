class Monster:
    def __init__(self, name, max_hp, attack, defense, speed, exp_reward, gold_reward):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward

    def take_damage(self, damage):
        actual_damage = max(1, damage)
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