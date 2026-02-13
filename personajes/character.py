import pygame
from personajes.constants import RED, PLAYER_DEATH
from abc import ABC, abstractmethod

class Character(pygame.sprite.Sprite, ABC):
    def __init__(
        self,
        game,
        x,
        y,
        width,
        height,
        scale,
        speed,
        anim_fps,
        hitbox_offset_x,
        hitbox_offset_y,
        max_live=None,
        asset_file=None,
    ):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.pos_x = x
        self.pos_y = y
        self.speed = speed
        self.frame_w = width
        self.frame_h = height
        self.scale = scale
        self.anim_fps = anim_fps
        self._current_frame = 0
        self._anim_timer = 0.0
        self.facing = "down"
        self.body_hitbox_offset_x = hitbox_offset_x
        self.body_hitbox_offset_y = hitbox_offset_y
        self._asset_file = asset_file
        self.max_live = max_live
        self._actual_life = max_live

        if asset_file is not None:
            self.load_sprites()
            self._curr_anim_list = self._down_sprites
            self.image = self._curr_anim_list[0]
        else:
            self.image = pygame.Surface((self.frame_w, self.frame_h))
            self.image.fill(RED)

        # Inicializar rect
        self.rect = pygame.Rect(
            int(self.pos_x),
            int(self.pos_y),
            self.frame_w * self.scale,
            self.frame_h * self.scale
        )

    @property
    def remaining_life(self):
        return self._actual_life

    @property
    def remaining_life_percentage(self):
        return (self._actual_life / self.remaining_life) * 100

    @property
    def body_hitbox(self):
        w = self.frame_w * self.scale
        h = self.frame_h * self.scale
        hitbox_w = w - (self.body_hitbox_offset_x * 2)
        hitbox_h = h - (self.body_hitbox_offset_y * 2)
        return pygame.Rect(
            int(self.pos_x + self.body_hitbox_offset_x),
            int(self.pos_y + self.body_hitbox_offset_y),
            int(hitbox_w),
            int(hitbox_h)
        )

    @property
    def hitbox(self) -> pygame.Rect:
        return self.body_hitbox

    def get_hits(self, tiles):
        hits = []
        for tile in tiles:
            if self.hitbox.colliderect(tile.hitbox):
                hits.append(tile)
        return hits

    def _resolve_collisions_x(self, tiles, dx: float):
        if dx == 0:
            return
        for tile in self.get_hits(tiles):
            if dx > 0:
                self.pos_x = tile.hitbox.left - self.hitbox.width - self.body_hitbox_offset_x
            elif dx < 0:
                self.pos_x = tile.hitbox.right - self.body_hitbox_offset_x

    def _resolve_collisions_y(self, tiles, dy: float):
        if dy == 0:
            return
        for tile in self.get_hits(tiles):
            if dy > 0:
                self.pos_y = tile.hitbox.top - self.hitbox.height - self.body_hitbox_offset_y
            elif dy < 0:
                self.pos_y = tile.hitbox.bottom - self.body_hitbox_offset_y

    def move_and_collide(self, dx: float, dy: float, tiles):
        """Mueve y resuelve colisiones por ejes (X y luego Y)."""

        if not tiles:
            self.pos_x += dx
            self.pos_y += dy
            return

        if dx:
            self.pos_x += dx
            self._resolve_collisions_x(tiles, dx)
        if dy:
            self.pos_y += dy
            self._resolve_collisions_y(tiles, dy)

        # Actualizar rect del sprite
        self.rect.topleft = (int(self.pos_x), int(self.pos_y))

    def collide_with_tiles(self, tiles):
        if not tiles:
            return

        # Primero resolvemos X
        for tile in self.get_hits(tiles):
            if self.facing == "right":
                self.pos_x = tile.hitbox.left - self.hitbox.width - self.body_hitbox_offset_x
            elif self.facing == "left":
                self.pos_x = tile.hitbox.right - self.body_hitbox_offset_x

        # Luego resolvemos Y
        for tile in self.get_hits(tiles):
            if self.facing == "down":
                self.pos_y = tile.hitbox.top - self.hitbox.height - self.body_hitbox_offset_y
            elif self.facing == "up":
                self.pos_y = tile.hitbox.bottom - self.body_hitbox_offset_y
        self.rect.topleft = (int(self.pos_x), int(self.pos_y))

    def debug_draw_hitbox(self, pantalla, color):
        # Dibujar Body Hitbox
        pygame.draw.rect(pantalla, color, self.body_hitbox, 1)

    def alert_if_death(self):
        if self.remaining_life <= 0:
            pygame.event.post(PLAYER_DEATH)

    def heal(self, heal_amount):
        if heal_amount > 0:
            self._actual_life = min(self._actual_life + heal_amount, self.max_live)

    def heal_percetage(self, heal_percentage):
        if 0 < heal_percentage <= 100:
            heal = self.max_live * heal_percentage / 100
            self._actual_life = min(self._actual_life + heal, self.max_live)

    @abstractmethod
    def die(self):
        pass

    def apply_damage(self, damage_amount):
        if damage_amount > 0:
            self._actual_life = max(self._actual_life - damage_amount, 0)

            if self.remaining_life <= 0:
                self.die()

    def apply_damage_percentage(self, damage_percentage):
        if 0 < damage_percentage <= 100:
            damage = self.max_live * damage_percentage / 100
            self._actual_life = max(self._actual_life - damage, 0)
            if self.remaining_life <= 0:
                self.die()

    def update(self, dt, acciones):
        direction_x = acciones["right"] - acciones["left"]
        direction_y = acciones["down"] - acciones["up"]

        if direction_x > 0:
            self.facing = "right"
        elif direction_x < 0:
            self.facing = "left"
        elif direction_y > 0:
            self.facing = "down"
        elif direction_y < 0:
            self.facing = "up"

        self.pos_x += direction_x * self.speed * dt
        self.pos_y += direction_y * self.speed * dt

        if self._asset_file is not None:
            moving = bool(direction_x or direction_y)
            self.animate(dt, moving)

        # Actualizar rect
        self.rect.topleft = (int(self.pos_x), int(self.pos_y))

    def animate(self, dt, moving: bool):
        if self.facing == "right":
            self._curr_anim_list = self._right_sprites
        elif self.facing == "left":
            self._curr_anim_list = self._left_sprites
        elif self.facing == "up":
            self._curr_anim_list = self._up_sprites
        else:
            self._curr_anim_list = self._down_sprites

        if not moving:
            self._current_frame = 0
            self._anim_timer = 0.0
            self.image = self._curr_anim_list[0]
            return

        self._anim_timer += dt
        frame_time = 1.0 / max(self.anim_fps, 1)
        while self._anim_timer >= frame_time:
            self._anim_timer -= frame_time
            self._current_frame = (self._current_frame + 1) % len(self._curr_anim_list)

        self.image = self._curr_anim_list[self._current_frame]

    @abstractmethod
    def load_sprites(self):
        '''
            Inicializa las variables:
                self._down_sprites
                self._up_sprites
                self._left_sprites
                self._right_sprites
        '''
        pass

    def get_rect(self) -> pygame.Rect:
        return self.rect
    
    def render(self, pantalla):
        pantalla.blit(self.image, self.rect.topleft)
