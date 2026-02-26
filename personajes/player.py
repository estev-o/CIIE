from personajes.character import Character
from personajes.constants import PLAYER_DEATH
import pygame
from personajes.ataques.azulejo import Azulejo
from personajes.ataques.lava_burst import LavaBurst
from personajes.ataques.attack_pool import AttackPool
from objetos.mejoras.catalogo import obtener_mejora

class Player(Character):
    SUPER_AZULEJO_DURATION = 20.0

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
        
        self.last_aim_axis = pygame.math.Vector2(1, 0)
        self.escudo_activo = False
        self.blub_lava_activo = False
        self.super_azulejo_habilitado = False
        self.super_azulejo_remaining = 0.0
        self.upgrade_cooldowns = {}

        self.attack_launcher1 = AttackPool(Azulejo, game)
        self.lava_burst_attack = LavaBurst(game)
        self._aplicar_mejoras_persistentes()
    
    
    def die(self):
        pygame.event.post(pygame.event.Event(PLAYER_DEATH))

    def _aplicar_mejoras_persistentes(self):
        if not hasattr(self.game, "mejoras"):
            return

        for mejora_id in self.game.mejoras.owned_ids():
            mejora = obtener_mejora(mejora_id)
            if not mejora:
                continue
            aplicar = mejora.get("apply")
            if callable(aplicar):
                aplicar(self)

    def register_upgrade_cooldown(self, upgrade_id, duration_seconds, asset_path=None, key_hint=None):
        entry = self.upgrade_cooldowns.get(upgrade_id)
        if entry is None:
            image = None
            if asset_path:
                try:
                    image = pygame.image.load(asset_path).convert_alpha()
                except Exception:
                    image = None
            entry = {
                "id": upgrade_id,
                "duration": float(duration_seconds),
                "remaining": 0.0,
                "image": image,
                "key_hint": (str(key_hint).upper() if key_hint else None),
            }
            self.upgrade_cooldowns[upgrade_id] = entry
        else:
            entry["duration"] = float(duration_seconds)
            if asset_path and entry.get("image") is None:
                try:
                    entry["image"] = pygame.image.load(asset_path).convert_alpha()
                except Exception:
                    pass
            if key_hint:
                entry["key_hint"] = str(key_hint).upper()
        return entry

    def is_upgrade_cooldown_ready(self, upgrade_id):
        entry = self.upgrade_cooldowns.get(upgrade_id)
        if entry is None:
            return True
        return entry.get("remaining", 0.0) <= 0.0

    def trigger_upgrade_cooldown(self, upgrade_id):
        entry = self.upgrade_cooldowns.get(upgrade_id)
        if entry is None:
            return False
        entry["remaining"] = float(entry.get("duration", 0.0))
        return True

    def _update_upgrade_cooldowns(self, dt):
        for entry in self.upgrade_cooldowns.values():
            remaining = float(entry.get("remaining", 0.0))
            if remaining > 0.0:
                entry["remaining"] = max(0.0, remaining - dt)

    def _try_block_with_shield(self):
        if not getattr(self, "escudo_activo", False):
            return False
        if not self.is_upgrade_cooldown_ready("escudo"):
            return False
        self.trigger_upgrade_cooldown("escudo")
        return True

    def _try_use_lava_burst(self):
        if not getattr(self, "blub_lava_activo", False):
            return False
        if not self.is_upgrade_cooldown_ready("blub_lava"):
            return False
        if self.lava_burst_attack.in_use():
            return False
        if not self.trigger_upgrade_cooldown("blub_lava"):
            return False
        self.lava_burst_attack.init(self.rect.centerx, self.rect.centery)
        return True

    def _try_use_super_azulejo(self):
        if not getattr(self, "super_azulejo_habilitado", False):
            return False
        if not self.is_upgrade_cooldown_ready("super_azulejo"):
            return False
        self.super_azulejo_remaining = float(self.SUPER_AZULEJO_DURATION)
        self.trigger_upgrade_cooldown("super_azulejo")
        return True

    def _is_super_azulejo_active(self):
        return self.super_azulejo_remaining > 0.0

    def apply_damage(self, damage_amount):
        if damage_amount > 0 and self._try_block_with_shield():
            return
        super().apply_damage(damage_amount)

    def apply_damage_percentage(self, damage_percentage):
        if damage_percentage > 0 and self._try_block_with_shield():
            return
        super().apply_damage_percentage(damage_percentage)

    def attack(self, acciones):
        if self.attack_launcher1.is_ready():
            if self._is_super_azulejo_active():
                directions = [
                    pygame.math.Vector2(1, 0),
                    pygame.math.Vector2(-1, 0),
                    pygame.math.Vector2(0, 1),
                    pygame.math.Vector2(0, -1),
                    pygame.math.Vector2(1, 1).normalize(),
                    pygame.math.Vector2(1, -1).normalize(),
                    pygame.math.Vector2(-1, 1).normalize(),
                    pygame.math.Vector2(-1, -1).normalize(),
                ]
            else:
                direction = pygame.math.Vector2(self.last_aim_axis)
                if direction.length() > 0:
                    direction = direction.normalize()
                else:
                    direction = pygame.math.Vector2(1, 0) # Fallback to right

                directions = [direction]
                if getattr(self, "disparo_triple_activo", False):
                    spread_angle = 12
                    directions.append(direction.rotate(spread_angle))
                    directions.append(direction.rotate(-spread_angle))

            for shot_direction in directions:
                self.attack_launcher1.create(
                    self.rect.centerx,
                    self.rect.centery,
                    shot_direction,
                )

    def update(self, dt, acciones,tiles):
        self._update_upgrade_cooldowns(dt)
        if self.super_azulejo_remaining > 0.0:
            self.super_azulejo_remaining = max(0.0, self.super_azulejo_remaining - dt)

        direction_x = acciones["right"] - acciones["left"]
        direction_y = acciones["down"] - acciones["up"]
        
        # Constantly update facing/aim direction
        current_mode = acciones.get("current_mode", "keyboard_mouse")
        aim_axis = acciones.get("aim_axis", (0.0, 0.0))

        if aim_axis[0] != 0.0 or aim_axis[1] != 0.0:
            self.last_aim_axis = pygame.math.Vector2(aim_axis)
        elif current_mode == "controller" and (direction_x != 0 or direction_y != 0):
            # Fallback to movement direction for D-pad users and general stick moving
            self.last_aim_axis = pygame.math.Vector2(direction_x, direction_y)
        elif current_mode == "keyboard_mouse":
            mouse_pos = acciones.get("mouse_pos")
            if mouse_pos:
                player_center = pygame.math.Vector2(self.rect.center)
                target = pygame.math.Vector2(mouse_pos)
                self.last_aim_axis = target - player_center

        if self.last_aim_axis.length() > 0:
            self.last_aim_axis = self.last_aim_axis.normalize()

        if direction_x > 0:
            self.facing = "right"
        elif direction_x < 0:
            self.facing = "left"
        elif direction_y > 0:
            self.facing = "down"
        elif direction_y < 0:
            self.facing = "up"

        if acciones["attack1"]:
            self.attack(acciones)
        if acciones.get("attack2"):
            self._try_use_lava_burst()
        if acciones.get("attack3"):
            self._try_use_super_azulejo()

        # Normalize the movement vector to prevent going faster diagonally
        move_vector = pygame.math.Vector2(direction_x, direction_y)
        if move_vector.length() > 0:
            move_vector = move_vector.normalize()
            
        dx = move_vector.x * self.speed * dt
        dy = move_vector.y * self.speed * dt

        self.move_and_collide(dx, dy, tiles)

        self.attack_launcher1.update(dt, tiles)
        self.lava_burst_attack.update(dt, tiles)

        if self._asset_file is not None:
            moving = bool(direction_x or direction_y)
            self.animate(dt, moving)

    def render(self, pantalla):
        pantalla.blit(self.image, self.rect)
        self.lava_burst_attack.render(pantalla)

        self.attack_launcher1.render(pantalla)

    def render_upgrade_cooldowns(self, pantalla, x=25, y=25):
        if not self.upgrade_cooldowns:
            return

        icon_size = 36
        pad = 8
        font = pygame.font.Font(None, 20)
        idx = 0
        for entry in self.upgrade_cooldowns.values():
            rect = pygame.Rect(x, y + idx * (icon_size + pad), icon_size, icon_size)
            idx += 1

            pygame.draw.rect(pantalla, (20, 20, 28), rect, border_radius=8)
            pygame.draw.rect(pantalla, (190, 210, 255), rect, 2, border_radius=8)

            image = entry.get("image")
            if image is not None:
                scaled = pygame.transform.scale(image, (icon_size - 6, icon_size - 6))
                pantalla.blit(scaled, scaled.get_rect(center=rect.center))

            key_hint = entry.get("key_hint")
            if key_hint:
                label = font.render(str(key_hint), True, (235, 240, 255))
                badge_rect = pygame.Rect(
                    rect.right + 6,
                    rect.centery - 11,
                    max(22, label.get_width() + 10),
                    22,
                )
                pygame.draw.rect(pantalla, (20, 20, 28), badge_rect, border_radius=7)
                pygame.draw.rect(pantalla, (190, 210, 255), badge_rect, 2, border_radius=7)
                pantalla.blit(label, label.get_rect(center=badge_rect.center))

            duration = float(entry.get("duration", 0.0))
            remaining = float(entry.get("remaining", 0.0))
            if duration <= 0.0 or remaining <= 0.0:
                continue

            cooldown_progress = max(0.0, min(1.0, remaining / duration))
            ready_progress = 1.0 - cooldown_progress

            # Sombra sobre el icono mientras recarga
            overlay = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 90))
            pantalla.blit(overlay, rect.topleft)

            bar_rect = rect.inflate(-4, -4)
            pygame.draw.rect(pantalla, (50, 50, 70), bar_rect, 1, border_radius=4)
            fill_h = max(1, int(bar_rect.height * ready_progress))
            fill_rect = pygame.Rect(bar_rect.x, bar_rect.bottom - fill_h, bar_rect.width, fill_h)
            pygame.draw.rect(pantalla, (120, 200, 255), fill_rect, border_radius=4)

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
