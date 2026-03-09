import os
import random

import pygame

from assets.tiles import TiledTMX
from estados.estado import Estado
from estados.pausa import Pausa
from personajes.enemigos.gilbertov import Gilbertov
from ui.adn_counter import ADNCounter
from ui.health_bar import HealthBarManager
from ui.player_health_bar import PlayerHealthBar


class BossFinal(Estado):
    DOOR_CLOSED_DURATION = 10.0
    DOOR_OPEN_DURATION = 5.0
    SUMMON_INTERVAL = 1.0
    SUMMON_DAMAGE_MULTIPLIER = 0.2
    SUMMON_ENEMIES = ("mock_melee", "mock_ranger", "mock_explosive")

    def __init__(self, juego):
        super().__init__(juego)
        imagen_original = pygame.image.load("assets/UI/cursor/crosshair.png").convert_alpha()
        self.cursor_img = pygame.transform.scale(imagen_original, (30, 30))

        juego.sound_engine.play_music_if_changed("boss", 3000)

        self.player = self.juego.player
        self.tmx_map = TiledTMX(os.path.join("assets", "sala_boss_final", "sala_boss_final.tmx"))
        self._base_layer_order = [
            name for name in self.tmx_map.layer_names
            if name not in ("puerta_abierta", "puerta_cerrada")
        ]
        self.map_layer_order = list(self._base_layer_order)
        self._door_closed = True
        self._summon_spawns = list(self.tmx_map.get_objects(layer="spawn_enemigos"))
        self._summon_spawn_index = 0
        self._map_bounds = pygame.Rect(
            0,
            0,
            self.tmx_map.width * self.tmx_map.tile_width,
            self.tmx_map.height * self.tmx_map.tile_height,
        )
        self._player_spawn_pos = (0.0, 0.0)

        self._spawn_player()
        self._spawn_boss()

        self.health_bar_manager = HealthBarManager(self.enemies)
        self.player_health_bar = PlayerHealthBar(25, self.juego.alto - 65, max_hp=self.player.max_live, current_hp=self.player.remaining_life)
        self.adn_counter = ADNCounter()
        self.adn_counter.set_position(
            self.player_health_bar.x,
            self.player_health_bar.y - self.adn_counter.height - 8,
        )

        self._cycle_elapsed = 0.0
        self._spawn_accumulator = 0.0
        self._victory_screen_opened = False
        self._update_door_state(force=True)
        self._set_boss_vulnerable(True)
        self._set_boss_damage_multiplier(self.SUMMON_DAMAGE_MULTIPLIER)

        # Fade in de entrada (tono ominoso)
        self._fade_timer = 0.0
        self._black_duration = 1.5
        self._fade_duration = 3.5
        self._intro_done = False

        self.iniciar_texto_nivel(
            f"DESPACHO DE GILBERTOV", 5000)

    def _spawn_player(self):
        spawn_points = self.tmx_map.get_objects(layer="spawn_point")
        if not spawn_points:
            spawn_points = self.tmx_map.get_objects(layer="spawn_ponint")
        rect = self.player.get_rect()
        if spawn_points:
            spawn = spawn_points[0]
            self.player.pos_x = spawn.x - (rect.width / 2)
            self.player.pos_y = spawn.y - (rect.height / 2)
        else:
            self.player.pos_x = (self.juego.ancho - rect.width) / 2
            self.player.pos_y = self.juego.alto - rect.height - 30
        self.player.rect.topleft = (int(self.player.pos_x), int(self.player.pos_y))
        self._player_spawn_pos = (float(self.player.pos_x), float(self.player.pos_y))
        self.player.facing = "up"
        if hasattr(self.player, "last_aim_axis"):
            self.player.last_aim_axis = pygame.math.Vector2(0, -1)

    def _spawn_boss(self):
        self.boss = Gilbertov(self.juego, x=0, y=0)
        boss_spawns = self.tmx_map.get_objects(layer="spawn_boss")
        if boss_spawns:
            boss_spawn = boss_spawns[0]
            self.boss.pos_x = boss_spawn.x
            self.boss.pos_y = boss_spawn.y
        else:
            boss_rect = self.boss.get_rect()
            self.boss.pos_x = (self.juego.ancho - boss_rect.width) / 2
            self.boss.pos_y = 70
        self.boss.rect.topleft = (int(self.boss.pos_x), int(self.boss.pos_y))
        self.boss.facing = "down"
        self.append_enemy(self.boss)

    def _set_boss_vulnerable(self, vulnerable: bool):
        if hasattr(self.boss, "set_vulnerable"):
            self.boss.set_vulnerable(vulnerable)

    def _set_boss_damage_multiplier(self, multiplier: float):
        if hasattr(self.boss, "set_damage_multiplier"):
            self.boss.set_damage_multiplier(multiplier)

    def _in_open_window(self):
        cycle_length = self.DOOR_CLOSED_DURATION + self.DOOR_OPEN_DURATION
        phase_time = self._cycle_elapsed % cycle_length
        return phase_time >= self.DOOR_CLOSED_DURATION

    def _update_door_state(self, force=False):
        should_close = not self._in_open_window()
        if not force and should_close == self._door_closed:
            return
        self._door_closed = should_close

        self.map_layer_order = list(self._base_layer_order)
        if self._door_closed:
            if "puerta_cerrada" in self.tmx_map.layer_names:
                self.map_layer_order.append("puerta_cerrada")
        else:
            if "puerta_abierta" in self.tmx_map.layer_names:
                self.map_layer_order.append("puerta_abierta")

    def _spawn_summoned_enemy(self):
        if not self.enemies.has(self.boss):
            return

        if self._summon_spawns:
            spawn = self._summon_spawns[self._summon_spawn_index % len(self._summon_spawns)]
            self._summon_spawn_index += 1
            spawn_x = spawn.x
            spawn_y = spawn.y
        else:
            # Fallback seguro si faltan puntos en el TMX.
            spawn_x = self.boss.rect.centerx
            spawn_y = self.boss.rect.centery

        enemy_name = random.choice(self.SUMMON_ENEMIES)
        enemy = self.juego.enemy_factory.create_enemy(enemy_name, spawn_x, spawn_y)
        if enemy is None:
            return
        # Entra ya en estado de persecución al spawnear.
        if hasattr(enemy, "ai_state"):
            enemy.ai_state = "alert"
        if hasattr(enemy, "alert_timer"):
            enemy.alert_timer = 0.0
        self.append_enemy(enemy)

    def _update_boss_cycle(self, dt):
        self._cycle_elapsed += dt
        self._update_door_state()

        if self._in_open_window():
            self._set_boss_vulnerable(True)
            self._set_boss_damage_multiplier(1.0)
        else:
            self._set_boss_vulnerable(True)
            self._set_boss_damage_multiplier(self.SUMMON_DAMAGE_MULTIPLIER)

        # Frecuencia igual que antes: 1 enemigo por segundo.
        # Solo salen cuando la puerta está cerrada.
        if not self._in_open_window():
            self._spawn_accumulator += dt
            while self._spawn_accumulator >= self.SUMMON_INTERVAL:
                self._spawn_accumulator -= self.SUMMON_INTERVAL
                self._spawn_summoned_enemy()
        else:
            self._spawn_accumulator = 0.0

    def _player_inside_map_bounds(self):
        return self._map_bounds.contains(self.player.body_hitbox)

    def _teleport_player_to_spawn(self):
        target_x, target_y = self._player_spawn_pos
        self.player.pos_x = target_x
        self.player.pos_y = target_y
        self.player.rect.topleft = (int(self.player.pos_x), int(self.player.pos_y))

    def actualizar(self, dt, acciones):
        if not self._intro_done:
            self._fade_timer += dt
            if self._fade_timer >= (self._black_duration + self._fade_duration):
                self._intro_done = True
            return  # bloquea input y lógica durante el fade

        if acciones.get("toggle_pause"):
            self.juego.actions["toggle_pause"] = False
            Pausa(self.juego).entrar_estado()
            return

        self._update_boss_cycle(dt)
        enemy_tiles = list(self.tmx_map.get_tiles())
        player_tiles = list(enemy_tiles)
        if self._door_closed:
            player_tiles.extend(self.tmx_map.get_tiles("hitbox_puerta_cerrada"))
        self.player.update(dt, acciones, player_tiles)
        if not self._player_inside_map_bounds():
            self._teleport_player_to_spawn()

        if (
                not self._victory_screen_opened
                and (not self.boss.alive() or self.boss.remaining_life <= 0)
        ):
            self._victory_screen_opened = True
            from estados.final_screen import FinalScreen
            self.juego.fade_to(lambda: FinalScreen(self.juego).entrar_estado())
            return

        for enemy in self.enemies:
            enemy.ai_behavior(self.player, dt, enemy_tiles)

        self.enemy_projectiles.update(dt, enemy_tiles)
        self.objects.update(self.player, dt)

        self.health_bar_manager.update()
        self.player_health_bar.update(dt, self.player.remaining_life, self.player.max_live)

    def dibujar(self, pantalla):
        pantalla.fill((0, 0, 0))
        self.tmx_map.draw(pantalla, only=self.map_layer_order)

        for enemy in self.enemies:
            enemy.render(pantalla)

        self.objects.draw(pantalla)
        self.enemy_projectiles.draw(pantalla)
        self.player.render(pantalla)

        self.health_bar_manager.draw(pantalla)
        self.player_health_bar.draw(pantalla)
        self.adn_counter.draw(pantalla, self.juego.adn)
        self.player.render_upgrade_cooldowns(pantalla, x=25, y=25)

        if not self._intro_done:
            if self._fade_timer < self._black_duration:
                alpha = 255
            else:
                progress = (self._fade_timer - self._black_duration) / self._fade_duration
                alpha = max(0, int(255 * (1.0 - progress)))
                
            overlay = pygame.Surface((pantalla.get_width(), pantalla.get_height()))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(alpha)
            pantalla.blit(overlay, (0, 0))

        self.dibujar_texto_nivel(pantalla)

        if self.juego.debug:
            self.player.debug_draw_hitbox(pantalla, (0, 255, 0))
            for enemy in self.enemies:
                enemy.debug_draw_hitbox(pantalla, (0, 255, 255))
            for projectile in self.enemy_projectiles:
                pygame.draw.rect(pantalla, (255, 0, 0), projectile.rect, 1)
