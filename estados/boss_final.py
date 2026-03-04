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
    DOOR_OPEN_DURATION = 10.0
    SUMMON_INTERVAL = 1.0
    SUMMON_DAMAGE_MULTIPLIER = 0.2
    SUMMON_ENEMIES = ("mock_melee", "mock_ranger", "mock_explosive")

    def __init__(self, juego):
        super().__init__(juego)
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

        self._spawn_player()
        self._spawn_boss()

        self.health_bar_manager = HealthBarManager(self.enemies)
        self.player_health_bar = PlayerHealthBar(25, self.juego.alto - 65)
        self.adn_counter = ADNCounter()
        self.adn_counter.set_position(
            self.player_health_bar.x,
            self.player_health_bar.y - self.adn_counter.height - 8,
        )

        self._cycle_elapsed = 0.0
        self._spawn_accumulator = 0.0
        self._update_door_state(force=True)
        self._set_boss_vulnerable(True)
        self._set_boss_damage_multiplier(self.SUMMON_DAMAGE_MULTIPLIER)

    def _spawn_player(self):
        spawn_points = self.tmx_map.get_objects(layer="spawn_ponint")
        if not spawn_points:
            spawn_points = self.tmx_map.get_objects(layer="spawn_point")
        rect = self.player.get_rect()
        if spawn_points:
            spawn = spawn_points[0]
            self.player.pos_x = spawn.x - (rect.width / 2)
            self.player.pos_y = spawn.y - (rect.height / 2)
        else:
            self.player.pos_x = (self.juego.ancho - rect.width) / 2
            self.player.pos_y = self.juego.alto - rect.height - 30
        self.player.rect.topleft = (int(self.player.pos_x), int(self.player.pos_y))
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

    def actualizar(self, dt, acciones):
        if acciones.get("toggle_pause"):
            self.juego.actions["toggle_pause"] = False
            Pausa(self.juego).entrar_estado()
            return

        self._update_boss_cycle(dt)
        enemy_tiles = list(self.tmx_map.get_tiles())
        player_tiles = list(enemy_tiles)
        if self._door_closed:
            player_tiles.extend(self.tmx_map.get_tiles("hitbox_puerta_cerrada"))
        blockers = player_tiles + list(self.enemies)
        self.player.update(dt, acciones, blockers)

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

        if self.juego.debug:
            self.player.debug_draw_hitbox(pantalla, (0, 255, 0))
            for enemy in self.enemies:
                enemy.debug_draw_hitbox(pantalla, (0, 255, 255))
            for projectile in self.enemy_projectiles:
                pygame.draw.rect(pantalla, (255, 0, 0), projectile.rect, 1)
