from personajes.character import Character
import pygame

class Blob(Character):
    def __init__(self, game):
        super().__init__(
            game=game,
            max_live=1000000,
            # blub es invencible jejejejejeje
            x=0,
            y=0,
            width=64,
            height=64,
            speed=200,
            scale=1.75,
            anim_fps=15,
            hitbox_offset_x=45,
            hitbox_offset_y=45,
            asset_file="assets/Blob/SlimeIdleSheet.png",
        )

    def die(self):
        pass  # Blob no muere, es un NPC invencible
    
    def update(self, dt, acciones, tiles):

        if self._asset_file is not None:
            self.animate(dt, moving=False)

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
