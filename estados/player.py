import pygame, os
from estados.abstract_character import AbstractCharacter

class Player(AbstractCharacter):
    def __init__(self, game):
        super().__init__(
            game = game,
            x = 100,
            y = 100,
            width = 64,
            height = 64,
            speed = 250,
            scale = 2,
            anim_fps = 10,
            asset_file = "assets/Blub/PNG/Slime1/Walk/Slime1_Walk_full.png"
        )

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.pos_x),
            int(self.pos_y),
            self.frame_w * self.scale,
            self.frame_h * self.scale,
        )
