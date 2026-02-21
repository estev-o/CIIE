from personajes.character import Character
from dialogos.estructuras.blob import hello_blob
from dialogos.dialog import Dialog
import pygame

class Blob(Character):
    def __init__(self, game):
        super().__init__(
            game=game,
            max_live=1000000,
            # blub es invencible jejejejejeje
            x=0,
            y=0,
            width=32,
            height=32,
            speed=200,
            scale=3.0,
            anim_fps=5,
            hitbox_offset_x=17,
            hitbox_offset_y=17,
            asset_file="assets/Blob/SlimeIdleSheet.png",
        )
        self.set_dialog(Dialog(hello_blob))

    def die(self):
        pass  # Blob no muere, es un NPC invencible
    
    def update(self, dt, acciones, tiles):

        if self._asset_file is not None:
            # Blob es NPC estático: animación idle continua en la primera fila.
            self.facing = "down"
            self.animate(dt, moving=True)

        self.rect.topleft = (int(self.pos_x), int(self.pos_y))

        if self.has_dialog():
            self.update_dialog(dt, acciones)


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

        self._down_sprites = slice_row(0)[:4]
