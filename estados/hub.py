import pygame, os
from estados.estado import Estado

class Hub(Estado):
    def __init__(self, juego):
        Estado.__init__(self,juego)
        # CARGAR FONDO AQUÍ

        # Puerta de salida (rectángulo) a la derecha en el centro
        self.puerta_rect = pygame.Rect(
            self.juego.ancho - 100,
            self.juego.alto // 2 - 50,
            80,
            100,
        )

        self.player = Player(self.juego)       

    def actualizar(self, dt, acciones):
        self.player.update(dt, acciones)

        # Si el rect del jugador toca cualquier parte del rectángulo de la puerta, cambiar de área
        if self.player.get_rect().colliderect(self.puerta_rect):
            from estados.area_experiment import AreaExperiment
            AreaExperiment(self.juego).entrar_estado()
            return

    def dibujar(self, pantalla):
        # Dibujar el Hub en la pantalla
        pantalla.fill((50, 50, 100))  # Fondo azul oscuro como ejemplo
        pygame.draw.rect(pantalla, (200, 100, 50), self.puerta_rect)

        self.juego.draw_text(pantalla, "HUB DEL JUEGO", (255, 255, 255), self.juego.ancho // 2, self.juego.alto // 2)
        self.player.render(pantalla)

# TODO: La clase Player debe estar separada en otro archivo, pero el tutorial lo deja aquí por simplicidad.
class Player():
    def __init__(self,game):
        self.game = game
        self.pos_x, self.pos_y = 100.0, 100.0
        self.speed = 250  # px/seg
        self.frame_w, self.frame_h = 64, 64
        # Multiplicador de tamaño del sprite (2 = el doble, 3 = el triple, etc.)
        self.scale = 2
        self.anim_fps = 10
        self.current_frame = 0
        self.anim_timer = 0.0
        # 4 direcciones típicas en spritesheets: down, left, right, up
        self.facing = "down"
        self.load_sprites()
        self.curr_anim_list = self.down_sprites
        self.curr_image = self.curr_anim_list[0]

    def update(self, dt, acciones):
        direction_x = acciones["right"] - acciones["left"]
        direction_y = acciones["down"] - acciones["up"]
        # Actualizar hacia dónde mira (prioriza el último eje presionado)
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

        moving = bool(direction_x or direction_y)
        self.animate(dt, moving)

    def render(self, pantalla):
        pantalla.blit(self.curr_image, (int(self.pos_x), int(self.pos_y)))

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.pos_x),
            int(self.pos_y),
            self.frame_w * self.scale,
            self.frame_h * self.scale,
        )

    def animate(self, dt, moving: bool):
        # Elegir animación según hacia dónde miramos
        if self.facing == "right":
            self.curr_anim_list = self.right_sprites
        elif self.facing == "left":
            self.curr_anim_list = self.left_sprites
        elif self.facing == "up":
            self.curr_anim_list = self.up_sprites
        else:
            self.curr_anim_list = self.down_sprites

        if not moving:
            self.current_frame = 0
            self.anim_timer = 0.0
            self.curr_image = self.curr_anim_list[0]
            return

        self.anim_timer += dt
        frame_time = 1.0 / max(self.anim_fps, 1)
        while self.anim_timer >= frame_time:
            self.anim_timer -= frame_time
            self.current_frame = (self.current_frame + 1) % len(self.curr_anim_list)

        self.curr_image = self.curr_anim_list[self.current_frame]


    def load_sprites(self):
        # Spritesheet del Slime1 (varios frames dentro de un solo PNG)
        sheet_path = os.path.join(
            "assets",
            "Blub",
            "PNG",
            "Slime1",
            "Walk",
            "Slime1_Walk_full.png",
        )
        sheet = pygame.image.load(sheet_path).convert_alpha()

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

        # Tu sheet (según indicas):
        # fila 1 -> abajo, fila 2 -> arriba, fila 3 -> izquierda, fila 4 -> derecha
        # (aquí es 0-indexed: 0,1,2,3)
        self.down_sprites = slice_row(0)
        self.up_sprites = slice_row(1) if rows >= 2 else list(self.down_sprites)
        self.left_sprites = slice_row(2) if rows >= 3 else [pygame.transform.flip(f, True, False) for f in self.down_sprites]
        self.right_sprites = slice_row(3) if rows >= 4 else [pygame.transform.flip(f, True, False) for f in self.left_sprites]
