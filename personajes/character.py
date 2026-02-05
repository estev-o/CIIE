import pygame
from personajes.constants import RED, PLAYER_DEATH


class Character:
    def __init__(
        self,
        game,
        max_live,
        x,
        y,
        width,
        height,
        scale,
        speed,
        anim_fps,
        asset_file=None,
    ):
        self.game = game
        self.max_live = max_live
        self._actual_life = max_live
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
        self._asset_file = asset_file

        if asset_file is not None:
            self.load_sprites()
            self._curr_anim_list = self._down_sprites
            self._curr_image = self._curr_anim_list[0]
        else:
            self._curr_image = pygame.Surface((self.frame_w, self.frame_h))
            self._curr_image.fill(RED)

    @property
    def remaining_life(self):
        return self._actual_life

    @property
    def remaining_life_percentage(self):
        return (self._actual_life / self.remaining_life) * 100

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

    def apply_damage(self, damage_amount):
        if damage_amount > 0:
            self._actual_life = max(self._actual_life - damage_amount, 0)
            self.alert_if_death()

    def apply_damage_percentage(self, damage_percentage):
        if 0 < damage_percentage <= 100:
            damage = self.max_live * damage_percentage / 100
            self._actual_life = min(self._actual_life - damage, 0)
            self.alert_if_death()

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

    def render(self, pantalla):
        pantalla.blit(self._curr_image, (int(self.pos_x), int(self.pos_y)))

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
            self._curr_image = self._curr_anim_list[0]
            return

        self._anim_timer += dt
        frame_time = 1.0 / max(self.anim_fps, 1)
        while self._anim_timer >= frame_time:
            self._anim_timer -= frame_time
            self._current_frame = (self._current_frame + 1) % len(self._curr_anim_list)

        self._curr_image = self._curr_anim_list[self._current_frame]

    def load_sprites(self):
        sheet = pygame.image.load(self._asset_file).convert_alpha()

        cols = sheet.get_width() // self.frame_w
        rows = sheet.get_height() // self.frame_h

        def slice_row(row_index: int):
            frames = []
            for col in range(cols):
                rect = pygame.Rect(
                    col * self.frame_w,
                    row_index * self.frame_h,
                    self.frame_w,
                    self.frame_h,
                )
                frame = sheet.subsurface(rect).copy()
                if self.scale != 1:
                    frame = pygame.transform.scale(
                        frame,
                        (self.frame_w * self.scale, self.frame_h * self.scale),
                    )
                frames.append(frame)
            return frames

        self._down_sprites = slice_row(0)
        self._up_sprites = slice_row(1) if rows >= 2 else list(self._down_sprites)
        self._left_sprites = (
            slice_row(2)
            if rows >= 3
            else [pygame.transform.flip(f, True, False) for f in self._down_sprites]
        )
        self._right_sprites = (
            slice_row(3)
            if rows >= 4
            else [pygame.transform.flip(f, True, False) for f in self._left_sprites]
        )

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.pos_x),
            int(self.pos_y),
            self.frame_w * self.scale,
            self.frame_h * self.scale,
        )
