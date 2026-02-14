from personajes.character import Character
from personajes.constants import PLAYER_DEATH
import pygame
from personajes.ataques.azulejo import Azulejo
from personajes.ataques.attack_pool import AttackPool

class Player(Character):
    def __init__(self, game):
        self._walk_asset_file = "assets/Blub/PNG/Slime1/Walk/Slime1_Walk_full.png"
        self._idle_asset_file = "assets/Blub/PNG/Slime1/Idle/Slime1_Idle_full.png"
        super().__init__(
            game=game,
            max_live=100,
            # la posición la cambiamos porque el spawn cambia según el estado del nivel
            x=0,
            y=0,
            width=64,
            height=64,
            speed=200,
            scale=1.75,
            anim_fps=13,
            hitbox_offset_x=45,
            hitbox_offset_y=45,
            asset_file=self._walk_asset_file,
        )

        self.attack_launcher1 = AttackPool(Azulejo, game)
    
    
    def die(self):
        pygame.event.post(pygame.event.Event(PLAYER_DEATH))

    def attack(self):
        if self.attack_launcher1.is_ready():
            attack = self.attack_launcher1.create(
                self.rect.centerx,
                self.rect.centery, 
                self.facing
                )

    def update(self, dt, acciones,tiles):
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

        if acciones["attack1"]:
            self.attack()

        dx = direction_x * self.speed * dt
        dy = direction_y * self.speed * dt

        self.move_and_collide(dx, dy, tiles)

        self.attack_launcher1.update(dt)

        if self._asset_file is not None:
            moving = bool(direction_x or direction_y)
            self.animate(dt, moving)

    def render(self, pantalla):
        pantalla.blit(self.image, self.rect)

        self.attack_launcher1.render(pantalla)

    def load_sprites(self):
        walk_sheet = pygame.image.load(self._walk_asset_file).convert_alpha()
        idle_sheet = pygame.image.load(self._idle_asset_file).convert_alpha()

        def build_directional_sets(sheet: pygame.Surface):
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

            down = slice_row(0)
            up = slice_row(1) if rows >= 2 else list(down)
            left = (
                slice_row(2)
                if rows >= 3
                else [pygame.transform.flip(f, True, False) for f in down]
            )
            right = (
                slice_row(3)
                if rows >= 4
                else [pygame.transform.flip(f, True, False) for f in left]
            )
            return down, up, left, right

        self._walk_down_sprites, self._walk_up_sprites, self._walk_left_sprites, self._walk_right_sprites = build_directional_sets(walk_sheet)
        self._idle_down_sprites, self._idle_up_sprites, self._idle_left_sprites, self._idle_right_sprites = build_directional_sets(idle_sheet)

        # Compatibilidad con Character: por defecto arranca con walk/down.
        self._down_sprites = self._walk_down_sprites
        self._up_sprites = self._walk_up_sprites
        self._left_sprites = self._walk_left_sprites
        self._right_sprites = self._walk_right_sprites

    def animate(self, dt, moving: bool):
        if moving:
            if self.facing == "right":
                selected = self._walk_right_sprites
            elif self.facing == "left":
                selected = self._walk_left_sprites
            elif self.facing == "up":
                selected = self._walk_up_sprites
            else:
                selected = self._walk_down_sprites
        else:
            if self.facing == "right":
                selected = self._idle_right_sprites
            elif self.facing == "left":
                selected = self._idle_left_sprites
            elif self.facing == "up":
                selected = self._idle_up_sprites
            else:
                selected = self._idle_down_sprites

        # Si cambia de estado (walk <-> idle) o dirección, reinicia ciclo.
        if getattr(self, "_curr_anim_list", None) is not selected:
            self._curr_anim_list = selected
            self._current_frame = 0
            self._anim_timer = 0.0

        self._anim_timer += dt
        frame_time = 1.0 / max(self.anim_fps, 1)
        while self._anim_timer >= frame_time:
            self._anim_timer -= frame_time
            self._current_frame = (self._current_frame + 1) % len(self._curr_anim_list)

        self.image = self._curr_anim_list[self._current_frame]
