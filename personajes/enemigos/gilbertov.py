import math

import pygame

from personajes.enemigos.enemy import Enemy


class Gilbertov(Enemy):
    """Boss final usando la ultima fila del spritesheet de Gilbertov."""
    DAMAGE_FLASH_DURATION = 0.12

    def __init__(self, game, x, y):
        super().__init__(
            game=game,
            x=x,
            y=y,
            width=50,
            height=100,
            scale=1,
            speed=150,
            damage=55,
            vision_range=2000,
            attack_range=150,
            attack_type="melee",
            attack_cooldown=0.8,
            attack_speed=250,
            anim_fps=7,
            hitbox_offset_x=4,
            hitbox_offset_y=6,
            max_live=3000,
            asset_file="assets/Gilvertov/Gilvertov.png",
            drop_table=[],
        )
        self.vulnerable = True
        self.damage_multiplier = 1.0
        self._damage_flash_timer = 0.0

    def load_sprites(self):
        sheet = pygame.image.load(self._asset_file).convert_alpha()
        cols = sheet.get_width() // self.frame_w
        # La animacion frontal ocupa el bloque inferior del sheet (y=150..249).
        row_top = max(0, sheet.get_height() - self.frame_h)

        def frame_from(col_index: int):
            rect = pygame.Rect(
                col_index * self.frame_w,
                row_top,
                self.frame_w,
                self.frame_h,
            )
            frame = sheet.subsurface(rect).copy()
            if self.scale != 1:
                frame = pygame.transform.scale(
                    frame,
                    (self.frame_w * self.scale, self.frame_h * self.scale),
                )
            return frame

        def is_empty(frame: pygame.Surface):
            return frame.get_bounding_rect().width == 0

        frames = []
        for col in range(cols):
            frame = frame_from(col)
            if not is_empty(frame):
                frames.append(frame)

        if not frames:
            frames = [frame_from(0)]

        # El boss usa la misma animacion para todas las direcciones.
        self._down_sprites = list(frames)
        self._up_sprites = list(frames)
        self._left_sprites = list(frames)
        self._right_sprites = list(frames)

    def ai_behavior(self, player, dt, solid_tiles):
        if self._damage_flash_timer > 0:
            self._damage_flash_timer = max(0.0, self._damage_flash_timer - dt)

        if not hasattr(self, "_anchor_pos"):
            self._anchor_pos = (float(self.pos_x), float(self.pos_y))

        self.pos_x, self.pos_y = self._anchor_pos
        self.rect.topleft = (int(self.pos_x), int(self.pos_y))

        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        # Sprite siempre orientado hacia abajo.
        self.facing = "down"

        # Ataque estatico: sin desplazarse, pero hace dano por cercania.
        if self.cooldown_timer > 0:
            self.cooldown_timer = max(0, self.cooldown_timer - dt)
        elif dist <= self.attack_range or self.hitbox.colliderect(player.hitbox):
            player.apply_damage(self.damage)
            self.cooldown_timer = self.attack_cooldown

        # Mantener animacion activa aunque no se desplace.
        self.animate(dt, moving=True)

    def set_vulnerable(self, vulnerable: bool):
        self.vulnerable = bool(vulnerable)

    def set_damage_multiplier(self, multiplier: float):
        self.damage_multiplier = max(0.0, float(multiplier))

    def apply_damage(self, damage_amount):
        if not self.vulnerable:
            return
        scaled_damage = damage_amount * self.damage_multiplier
        if scaled_damage <= 0:
            return
        prev_life = self.remaining_life
        super().apply_damage(scaled_damage)
        if self.remaining_life < prev_life:
            self._damage_flash_timer = self.DAMAGE_FLASH_DURATION

    def apply_damage_percentage(self, damage_percentage):
        if not self.vulnerable:
            return
        scaled_percentage = damage_percentage * self.damage_multiplier
        if scaled_percentage <= 0:
            return
        prev_life = self.remaining_life
        super().apply_damage_percentage(scaled_percentage)
        if self.remaining_life < prev_life:
            self._damage_flash_timer = self.DAMAGE_FLASH_DURATION

    def render(self, pantalla):
        radius = int(self.attack_range)
        overlay_size = radius * 2
        overlay = pygame.Surface((overlay_size, overlay_size), pygame.SRCALPHA)
        pygame.draw.circle(
            overlay,
            (255, 0, 0, 40),
            (radius, radius),
            radius,
        )
        pantalla.blit(overlay, (self.rect.centerx - radius, self.rect.centery - radius))
        pygame.draw.circle(pantalla, (255, 0, 0), self.rect.center, radius, 2)

        if self._damage_flash_timer <= 0:
            super().render(pantalla)
            return

        original = self.image
        flashed = original.copy()
        flashed.fill((120, 0, 0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        self.image = flashed
        super().render(pantalla)
        self.image = original
