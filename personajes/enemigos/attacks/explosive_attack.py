import math

import pygame

from personajes.enemigos.attacks.attack_behavior import AttackBehavior


class ExplosiveAttack(AttackBehavior):
    def __init__(self, enemy):
        super().__init__(enemy)
        self.has_exploded = False  # Control para evitar bucles infinitos al morir

    def execute(self, player, dt, solid_tiles):
        # Forzamos al enemigo a moverse hacia adelante.
        self.chase_player(player, dt, solid_tiles)

    def chase_player(self, player, dt, solid_tiles):
        if self.enemy.remaining_life <= 0 or pygame.Rect.colliderect(player.hitbox, self.enemy.hitbox):
            self.explode()
        dx = player.rect.centerx - self.enemy.hitbox.centerx
        dy = player.rect.centery - self.enemy.hitbox.centery
        dist = math.hypot(dx, dy)
        # Normalizamos y aplicamos dirección de movimiento
        dir_x = (dx / dist)
        dir_y = (dy / dist)

        # Determinar hacia dónde mira
        if abs(dx) > abs(dy):
            self.enemy.facing = "right" if dx > 0 else "left"
        else:
            self.enemy.facing = "down" if dy > 0 else "up"

        move_x = dir_x * self.enemy.speed * dt
        move_y = dir_y * self.enemy.speed * dt

        # Aplicar movimiento con colisiones
        if solid_tiles is not None:
            self.enemy.move_and_collide(move_x, move_y, solid_tiles)
        else:
            self.enemy.pos_x += move_x
            self.enemy.pos_y += move_y
            self.enemy.rect.topleft = (int(self.enemy.pos_x), int(self.enemy.pos_y))

        self.enemy.animate(dt, moving=True)
    def explode(self):
        state = self.enemy.game.actual_state

        # Dañar al jugador si está dentro del radio de explosión (attack_range)
        player = state.player
        dist_to_player = math.hypot(
            player.rect.centerx - self.enemy.rect.centerx,
            player.rect.centery - self.enemy.rect.centery
        )
        if dist_to_player <= self.enemy.attack_range:
            player.apply_damage(self.enemy.damage)

        # Dañar a los enemigos dentro de su radio
        for other_enemy in state.enemies:
            if other_enemy != self.enemy:
                dist_to_enemy = math.hypot(
                    other_enemy.rect.centerx - self.enemy.rect.centerx,
                    other_enemy.rect.centery - self.enemy.rect.centery
                )
                if dist_to_enemy <= self.enemy.attack_range:
                    other_enemy.apply_damage(self.enemy.damage)
                    if other_enemy.remaining_life <= 0:
                        other_enemy.die()

        explosion = ExplosionSprite(self.enemy.rect.centerx, self.enemy.rect.centery, radio=self.enemy.attack_range)
        state.objects.add(explosion)
        # Matar al enemigo explosivo si no estaba muerto ya
        if self.enemy.remaining_life > 0:
            self.enemy.apply_damage_percentage(100)
            self.enemy.die()


class ExplosionSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, radio):
        super().__init__()

        size = int(radio * 2)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)

        # Dibujamos el círculo usando el radio
        centro = (size // 2, size // 2)
        pygame.draw.circle(self.image, (255, 100, 0), centro, int(radio))
        self.rect = self.image.get_rect(center=(x, y))

        # Variables para a animación
        # self.frames = []
        self.current_frame = 0
        self.anim_timer = 0.5
        self.anim_fps = 15

    def update(self, player, dt):
        self.anim_timer -= dt

        # Hacer que desaparezca tras un rato
        if self.anim_timer <=0:
            self.kill()