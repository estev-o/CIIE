import pygame

from personajes.ataques.attack import Attack


class LavaBurst(Attack):
    DURATION_SECONDS = 3.4

    def __init__(self, game):
        # Superficie dummy; el render real se dibuja proceduralmente.
        image = pygame.Surface((2, 2), pygame.SRCALPHA)
        super().__init__(game=game, image=image, damage=30, speed=0)

        self.center = pygame.math.Vector2(0, 0)
        self.radius = 0.0
        self.expansion_speed = 360.0
        self.ring_thickness = 18.0
        self.elapsed = 0.0
        self._hit_enemy_ids = set()

    def init(self, x, y, *_args, **_kwargs):
        self.activate()
        self.center.update(float(x), float(y))
        self.radius = 0.0
        self.elapsed = 0.0
        self._hit_enemy_ids.clear()
        self._sync_rect()

    def _sync_rect(self):
        r = int(self.radius)
        self.rect = pygame.Rect(int(self.center.x - r), int(self.center.y - r), r * 2, r * 2)

    def _circle_intersects_rect(self, radius: float, rect: pygame.Rect) -> bool:
        closest_x = max(rect.left, min(self.center.x, rect.right))
        closest_y = max(rect.top, min(self.center.y, rect.bottom))
        dx = self.center.x - closest_x
        dy = self.center.y - closest_y
        return (dx * dx + dy * dy) <= (radius * radius)

    def _damage_enemies(self):
        state = getattr(self.game, "actual_state", None)
        enemies = getattr(state, "enemies", None)
        if enemies is None:
            return

        for enemy in list(enemies):
            if enemy.__class__.__name__ == "Chest":
                continue
            enemy_id = id(enemy)
            if enemy_id in self._hit_enemy_ids:
                continue

            enemy_hitbox = getattr(enemy, "hitbox", None) or getattr(enemy, "rect", None)
            if enemy_hitbox is None:
                continue

            # Golpea a todo enemigo que entre en el area de la explosion.
            if self._circle_intersects_rect(self.radius, enemy_hitbox):
                enemy.apply_damage(self.damage)
                self._hit_enemy_ids.add(enemy_id)

    def update(self, dt, tiles=None):
        if not self.in_use():
            return

        self.elapsed += dt
        self.radius = self.expansion_speed * self.elapsed
        self._sync_rect()

        self._damage_enemies()

        if self.elapsed >= self.DURATION_SECONDS:
            self.deactivate()

    def render(self, screen):
        if not self.in_use():
            return

        radius = max(1, int(self.radius))
        thickness = max(2, int(self.ring_thickness))
        size = radius * 2 + thickness * 2 + 8
        fx = pygame.Surface((size, size), pygame.SRCALPHA)
        local_center = (size // 2, size // 2)

        fade = max(0.0, min(1.0, 1.0 - (self.elapsed / self.DURATION_SECONDS)))
        edge_alpha = int(220 * fade + 30)
        fill_alpha = int(70 * fade)

        pygame.draw.circle(fx, (255, 120, 25, fill_alpha), local_center, radius)
        pygame.draw.circle(fx, (255, 220, 120, edge_alpha), local_center, radius, thickness)
        pygame.draw.circle(fx, (255, 70, 15, max(0, edge_alpha - 60)), local_center, max(1, radius - 8), 2)

        screen.blit(fx, fx.get_rect(center=(int(self.center.x), int(self.center.y))))
