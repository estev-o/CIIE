import random
from abc import ABC

import pygame

from personajes.character import Character

class Enemy(Character, ABC):
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
            max_live,
            asset_file,
    ):
        super().__init__(
            game=game, max_live=max_live, x=x, y=y, width=width, height=height, scale=scale, speed=speed, anim_fps=anim_fps, hitbox_offset_x=hitbox_offset_x, hitbox_offset_y= hitbox_offset_y, asset_file=asset_file
        )

        # VARIABLES PARA IDLE_MOVE
        self.idle_state = "wait"  # Puede ser "wait" o "move"
        self.idle_timer = 1.0  # Tiempo restante en el estado actual
        self.idle_dir_x = 0  # Dirección X actual
        self.idle_dir_y = 0  # Dirección Y actual

        # Configuración de tiempos
        self.wait_time_min = 0.75
        self.wait_time_max = 2.0
        self.move_time_min = 1.0
        self.move_time_max = 3.0

    def idle_move(self, dt):
        """
        Gestiona el movimiento aleatorio.
        Retorna (velocidad_x, velocidad_y) para aplicar al movimiento.
        """
        self.idle_timer -= dt

        # Si el tiempo se acabó, cambiamos de estado
        if self.idle_timer <= 0:

            if self.idle_state == "wait":
                # CAMBIO A MOVERSE
                self.idle_state = "move"
                self.idle_timer = random.uniform(self.move_time_min, self.move_time_max)

                self.idle_dir_x = random.uniform(-1, 1)
                self.idle_dir_y = random.uniform(-1, 1)
                #Limitar espacio de movimiento

            else:
                # CAMBIO A ESPERAR
                self.idle_state = "wait"
                self.idle_timer = random.uniform(self.wait_time_min, self.wait_time_max)
                self.idle_dir_x = 0
                self.idle_dir_y = 0

        # Calcular el movimiento final
        move_x = self.idle_dir_x * self.speed * dt
        move_y = self.idle_dir_y * self.speed * dt
        self.pos_x += move_x
        self.pos_y += move_y
        return

    def ai_behavior(self, dist, dt):
        vision_range = 0  # Rango de detección

        if dist > vision_range:
            # 1. ESTADO: IDLE / PATRULLA
            # El jugador está lejos, deambulamos
            self.idle_move(dt)
        else:
            # 2. ESTADO: PERSECUCIÓN / ATAQUE
            # El jugador fue detectado
            print("Ataque")
            #Lógica de persecución
        return
    def die(self):
        pass
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