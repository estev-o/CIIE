import pygame
import os

class PlayerHealthBar:
    def __init__(self, x, y, max_hp=100, scale=3):
        self.x = x
        self.y = y
        self.scale = scale
        self.max_hp = max_hp
        self.display_hp = max_hp
        self.target_hp = max_hp
        
        # Load and scale assets
        base_path = os.path.join("assets", "UI", "barra de vida")
        self.bg_image = pygame.image.load(os.path.join(base_path, "fondo barra.png")).convert_alpha()
        self.hp_image = pygame.image.load(os.path.join(base_path, "vida barra.png")).convert_alpha()
        self.heart_image = pygame.image.load(os.path.join(base_path, "corazon barra.png")).convert_alpha()
        
        self.bg_image = pygame.transform.scale(self.bg_image, (int(self.bg_image.get_width() * scale), int(self.bg_image.get_height() * scale)))
        self.hp_image = pygame.transform.scale(self.hp_image, (int(self.hp_image.get_width() * scale), int(self.hp_image.get_height() * scale)))
        self.heart_image = pygame.transform.scale(self.heart_image, (int(self.heart_image.get_width() * scale), int(self.heart_image.get_height() * scale)))
        
        self.width = self.bg_image.get_width()
        self.height = self.bg_image.get_height()
        
        # HP Text Font
        font_size = int(self.height * 0.4)
        self.font = pygame.font.Font("assets/fonts/Snowbell-Wp4g9.ttf", font_size)

    def update(self, dt, target_hp, max_hp):
        self.max_hp = max_hp
        self.target_hp = target_hp
        
        # Smooth interpolation
        speed = 5
        diff = target_hp - self.display_hp
        if abs(diff) < 0.1:
            self.display_hp = target_hp
        else:
            self.display_hp += diff * speed * dt

    def draw(self, surface):
        if self.max_hp <= 0:
            pct = 0
        else:
            pct = max(0, min(1, self.display_hp / self.max_hp))
            
        # Draw layers: BG -> HP (clipped) -> Heart
        surface.blit(self.bg_image, (self.x, self.y))
        
        # Clipping logic for sliding HP bar
        old_clip = surface.get_clip()
        clip_rect = pygame.Rect(self.x + 40, self.y, self.width, self.height)
        
        if old_clip:
            clip_rect = clip_rect.clip(old_clip)
        
        surface.set_clip(clip_rect)
        
        # Sliding calculation
        draw_x = self.x - (self.width - 50) * (1 - pct)
        surface.blit(self.hp_image, (int(draw_x), self.y))
        
        surface.set_clip(old_clip)
        surface.blit(self.heart_image, (self.x, self.y))
        
        # HP Text
        text = f"{int(self.target_hp)}/{int(self.max_hp)}"
        text_surf = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(clip_rect.centerx - 20, clip_rect.centery - 2))
        surface.blit(text_surf, text_rect)
