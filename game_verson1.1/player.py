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
        self.gold = 50

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