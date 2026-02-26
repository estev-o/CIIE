import math
import random

import pygame

from personajes.character import Character
from personajes.enemigos.attacks.melee_attack import MeleeAttack
from personajes.enemigos.attacks.ranged_attack import RangedAttack


class Enemy(Character):
    def __init__(
            self,
            game,
            x,
            y,
            width,
            height,
            scale,
            speed,
            damage,
            vision_range,
            attack_range,
            attack_type,
            attack_cooldown,
            attack_speed,
            anim_fps,
            hitbox_offset_x,
            hitbox_offset_y,
            max_live,
            asset_file,
            drop_table=None,
    ):
        super().__init__(
            game=game, max_live=max_live, x=x, y=y, width=width, height=height, scale=scale, speed=speed,
            anim_fps=anim_fps, hitbox_offset_x=hitbox_offset_x, hitbox_offset_y=hitbox_offset_y, asset_file=asset_file
        )
        self.vision_range = vision_range
        self.attack_range= attack_range
        self.damage = damage
        self.drop_table = list(drop_table or [])

        if attack_type=="melee":
            self.attack_behavior = MeleeAttack(self)

        elif attack_type== "ranged":
            self.attack_behavior = RangedAttack(self)

        self.attack_cooldown = attack_cooldown
        self.attack_speed = attack_speed

        # VARIABLES PARA IDLE_MOVE
        self.ai_state = "idle"
        self.idle_state = "wait"  # Puede ser "wait" o "move"
        self.idle_timer = 1.0  # Tiempo restante en el estado actual
        self.idle_dir_x = 0  # Dirección X actual
        self.idle_dir_y = 0  # Dirección Y actual

        # Configuración de tiempos
        self.wait_time_min = 0.75
        self.wait_time_max = 2.0
        self.move_time_min = 1.0
        self.move_time_max = 3.0
        self.alert_timer = 0
        self.cooldown_timer=0

    def maintain_distance(self, player, dt, solid_tiles):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        if dist == 0: dist = 0.1
        move_dir = 0
        if dist > self.attack_range - 10: #Intenta mantenerse dentro del área de ataque con un margen
            move_dir = 1
        elif dist < self.attack_range/2:
            move_dir = -1

        if move_dir != 0:
            # Normalizamos y aplicamos dirección de movimiento
            dir_x = (dx / dist) * move_dir
            dir_y = (dy / dist) * move_dir

            # Determinar hacia dónde mira
            if abs(dx) > abs(dy):
                self.facing = "right" if dx > 0 else "left"
            else:
                self.facing = "down" if dy > 0 else "up"

            move_x = dir_x * self.speed * dt
            move_y = dir_y * self.speed * dt

            # Aplicar movimiento con colisiones
            if solid_tiles is not None:
                self.move_and_collide(move_x, move_y, solid_tiles)
            else:
                self.pos_x += move_x
                self.pos_y += move_y
                self.rect.topleft = (int(self.pos_x), int(self.pos_y))

            if self._asset_file is not None:
                self.animate(dt, moving=True)
        else:
            if self._asset_file is not None:
                self.animate(dt, moving=False)

    def idle_behavior(self, dt, tiles=None):
        """
        Proporciona al enemigo un movimiento aleatorio.
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
            else:
                # CAMBIO A ESPERAR
                self.idle_state = "wait"
                self.idle_timer = random.uniform(self.wait_time_min, self.wait_time_max)
                self.idle_dir_x = 0
                self.idle_dir_y = 0

        # Calcular el movimiento final
        move_x = self.idle_dir_x * self.speed * dt
        move_y = self.idle_dir_y * self.speed * dt

        # Orientación (para animación)
        if abs(self.idle_dir_x) > abs(self.idle_dir_y):
            if self.idle_dir_x > 0:
                self.facing = "right"
            elif self.idle_dir_x < 0:
                self.facing = "left"
        else:
            if self.idle_dir_y > 0:
                self.facing = "down"
            elif self.idle_dir_y < 0:
                self.facing = "up"

        self.pos_x += move_x
        self.pos_y += move_y

        if tiles is not None:
            # rehacer el movimiento con colisión por ejes (evita glitches en diagonales)
            self.pos_x -= move_x
            self.pos_y -= move_y
            self.move_and_collide(move_x, move_y, tiles)
        self.rect.topleft = (int(self.pos_x), int(self.pos_y))

        if self._asset_file is not None:
            moving = bool(self.idle_dir_x or self.idle_dir_y)
            self.animate(dt, moving)

    def alerted_behavior(self, player, dt, solid_tiles):
        """Comportamiento una vez detectado el jugador"""

        if pygame.Rect.colliderect(self.hitbox, player.hitbox):
            player.apply_damage(self.damage)

        #Calculamos posición y distancia del jugador
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        if dist > self.attack_range or self.cooldown_timer>0:
            self.cooldown_timer -= dt
            self.maintain_distance(player,dt, solid_tiles)
        # Lógica de ataque
        else:
            self.attack_behavior.execute(player, dt, solid_tiles)


    def ai_behavior(self, player, dt, solid_tiles):
        """
        Gestor de estados para el comportamiento del enemigo.
        """
        if self.alert_timer > 0:
            self.alert_timer -= dt

            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery

            # Calculamos la dirección del jugador
            if abs(dx) > abs(dy):
                self.facing = "right" if dx > 0 else "left"
            else:
                self.facing = "down" if dy > 0 else "up"

            self.animate(0, False)

        elif self.ai_state == "alert":
            self.alerted_behavior(player, dt, solid_tiles)

        else:
            # Calculamos si el jugador está en su rango de visión o si ha recibido daño
            dist = math.hypot(
                player.rect.centerx - self.rect.centerx,
                player.rect.centery - self.rect.centery
            )
            taken_damage = self.remaining_life < self.max_live

            if dist <= self.vision_range or taken_damage:
                self.ai_state = "alert"
                self.alert_timer = 0.7
            else:
                self.idle_behavior(dt, solid_tiles)

    def die(self):
        self.drop()
        # Quitar sprite de los grupos
        self.kill()

    def drop(self):
        if self.drop_table:
            object_ids = [entry.get("object") for entry in self.drop_table]
            weights = [entry.get("weight", 0) for entry in self.drop_table]
            drop_object_id = random.choices(object_ids, weights=weights, k=1)[0]
            if drop_object_id is not None:
                drop = self.game.object_factory.create_object(
                    drop_object_id,
                    self.rect.centerx,
                    self.rect.centery,
                )
                if drop is not None:
                    self.game.actual_state.objects.add(drop)

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

    def debug_draw_hitbox(self, pantalla, color):
        if self.remaining_life <= 0:
            return
        pygame.draw.circle(pantalla,(255, 0, 255), self.rect.center, int(self.vision_range),1)
        pygame.draw.circle(pantalla,(255, 0, 0), self.rect.center, int(self.attack_range),1)

        super().debug_draw_hitbox(pantalla, color)

    def render(self, pantalla):
        super().render(pantalla)

        if self.ai_state == "alert" and self.alert_timer > 0:
            if not hasattr(self, 'alert_icon_loaded'):
                try:
                    self.alert_icon = pygame.image.load("assets/enemies/Alert.png").convert_alpha()
                    self.alert_icon = pygame.transform.scale(self.alert_icon, (15 * self.scale, 20 * self.scale))
                    self.alert_icon_loaded = True
                except:
                    self.alert_icon = None

            if self.alert_icon:
                hb = self.hitbox
                icon_x = hb.centerx - (self.alert_icon.get_width() // 2)
                icon_y = hb.top - self.alert_icon.get_height() - 3
                pantalla.blit(self.alert_icon, (icon_x, icon_y))
