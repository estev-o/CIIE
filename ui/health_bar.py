"""
Visualización y gestión de las barras de salud de las entidades del juego.
"""
import pygame

# -----------------------------------------------------------------
# --- Barra de Salud Individual
# -----------------------------------------------------------------

class HealthBar:
    """
    Representa visualmente la vida restante de una entidad específica.
    """
    def __init__(self, entity, width=30, height=4, offset_y=10):
        self.entity = entity
        self.width = int(getattr(entity, "health_bar_width", width))
        self.height = int(getattr(entity, "health_bar_height", height))
        self.offset_y = int(getattr(entity, "health_bar_offset_y", offset_y))
        self.border_color = (0, 0, 0)
        self.bg_color = (60, 60, 60)

    def draw(self, surface):
        if not self.entity.alive():
            return

        x = self.entity.rect.centerx - self.width // 2
        y = self.entity.rect.top + self.offset_y
        
        if hasattr(self.entity, "remaining_life") and hasattr(self.entity, "max_live"):
            if self.entity.max_live <= 0:
                pct = 0
            else:
                pct = self.entity.remaining_life / self.entity.max_live
        else:
            pct = 0
        
        pct = max(0, min(1, pct))

        if pct > 0.6:
            color = (0, 255, 0)
        elif pct > 0.3:
            color = (255, 255, 0)
        else:
            color = (255, 0, 0)

        bg_rect = pygame.Rect(x, y, self.width, self.height)
        pygame.draw.rect(surface, self.bg_color, bg_rect)

        fill_width = int(self.width * pct)
        fill_rect = pygame.Rect(x, y, fill_width, self.height)
        pygame.draw.rect(surface, color, fill_rect)

        pygame.draw.rect(surface, self.border_color, bg_rect, 1)


# -----------------------------------------------------------------
# --- Gestor de Barras de Salud para Grupos
# -----------------------------------------------------------------

class HealthBarManager:
    """
    Gestiona y sincroniza automáticamente las barras de salud de un grupo de entidades.
    """
    def __init__(self, enemy_group):
        self.enemy_group = enemy_group
        self.bars = {}

    def update(self):
        current_sprites = set(self.enemy_group.sprites())
        tracked_sprites = set(self.bars.keys())

        for sprite in current_sprites:
            if sprite not in tracked_sprites:
                if sprite.__class__.__name__ == "Chest":
                    continue
                self.bars[sprite] = HealthBar(sprite)

        for sprite in list(tracked_sprites):
            if sprite not in current_sprites:
                del self.bars[sprite]

    def draw(self, surface):
        for bar in self.bars.values():
            bar.draw(surface)
