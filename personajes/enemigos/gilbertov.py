import pygame

from personajes.enemigos.enemy import Enemy


class Gilbertov(Enemy):
    """Boss final usando la ultima fila del spritesheet de Gilbertov."""

    def __init__(self, game, x, y):
        super().__init__(
            game=game,
            x=x,
            y=y,
            width=50,
            height=100,
            scale=1,
            speed=150,
            damage=20,
            vision_range=2000,
            attack_range=150,
            attack_type="melee",
            attack_cooldown=0.8,
            attack_speed=250,
            anim_fps=7,
            hitbox_offset_x=20,
            hitbox_offset_y=10,
            max_live=600,
            asset_file="assets/Gilvertov/Gilvertov.png",
            drop_table=[],
        )

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
