import os
import pygame


class ADNCounter:
    def __init__(
        self,
        x=20,
        y=20,
        scale=2.0,
        sprite_path=os.path.join("assets", "UI", "ADN", "ADN.png"),
    ):
        self.x = x
        self.y = y
        self.gap = 8
        self.text_color = (255, 255, 255)
        self.shadow_color = (0, 0, 0)

        icon = pygame.image.load(sprite_path).convert_alpha()
        self.icon = pygame.transform.scale(
            icon,
            (int(icon.get_width() * scale), int(icon.get_height() * scale)),
        )
        self.width = self.icon.get_width()
        self.height = self.icon.get_height()
        self.font = pygame.font.Font(None, max(20, int(self.height * 0.9)))

    def set_position(self, x, y):
        self.x = int(x)
        self.y = int(y)

    def draw(self, surface, adn_amount):
        amount = int(adn_amount)
        text = self.font.render(str(amount), True, self.text_color)
        shadow = self.font.render(str(amount), True, self.shadow_color)

        text_x = self.x + self.width + self.gap
        text_y = self.y + (self.height - text.get_height()) // 2

        surface.blit(self.icon, (self.x, self.y))
        surface.blit(shadow, (text_x + 2, text_y + 2))
        surface.blit(text, (text_x, text_y))
