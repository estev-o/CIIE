from abc import ABC


class AttackBehavior(ABC):
    def __init__(self, enemy):
        self.enemy = enemy
        self.cooldown = 0
        self.attack_speed = 1.0  # Segundos entre ataques

    def execute(self, player, dt, solid_tiles):
        pass