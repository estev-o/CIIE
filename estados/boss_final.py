import math
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
    SUMMON_DURATION = 15.0
    DAMAGE_WINDOW_DURATION = 5.0
    SUMMON_INTERVAL = 1.0
    SUMMON_DAMAGE_MULTIPLIER = 0.2
    SUMMON_ENEMIES = ("mock_melee", "mock_ranger", "mock_explosive")

    def __init__(self, juego):
        super().__init__(juego)
        self.player = self.juego.player
        self.tmx_map = TiledTMX(os.path.join("assets", "area_experimentacion", "area_exp1.tmx"))
        self.map_layer_order = list(self.tmx_map.layer_names)
        self._enemy_spawn_points = list(self.tmx_map.get_objects(layer="spawn_enemies"))
        self._summon_spawn_points = []

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
        self._set_boss_vulnerable(True)
        self._set_boss_damage_multiplier(self.SUMMON_DAMAGE_MULTIPLIER)

    def _spawn_player(self):
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
        if self._enemy_spawn_points:
            boss_spawn = self._enemy_spawn_points[0]
            self.boss.pos_x = boss_spawn.x
            self.boss.pos_y = boss_spawn.y
            if len(self._enemy_spawn_points) > 1:
                self._summon_spawn_points = list(self._enemy_spawn_points[1:])
            else:
                self._summon_spawn_points = list(self._enemy_spawn_points)
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

    def _in_damage_window(self):
        cycle_length = self.SUMMON_DURATION + self.DAMAGE_WINDOW_DURATION
        phase_time = self._cycle_elapsed % cycle_length
        return phase_time >= self.SUMMON_DURATION

    def _spawn_summoned_enemy(self):
        if not self.enemies.has(self.boss):
            return

        if self._summon_spawn_points:
            spawn = random.choice(self._summon_spawn_points)
            spawn_x = spawn.x
            spawn_y = spawn.y
        else:
            angle = random.uniform(0.0, math.tau)
            radius = random.uniform(95.0, 150.0)
            spawn_x = self.boss.rect.centerx + math.cos(angle) * radius
            spawn_y = self.boss.rect.centery + math.sin(angle) * radius

        enemy_name = random.choice(self.SUMMON_ENEMIES)
        enemy = self.juego.enemy_factory.create_enemy(enemy_name, spawn_x, spawn_y)
        if enemy is None:
            return
        self.append_enemy(enemy)

    def _update_boss_cycle(self, dt):
        self._cycle_elapsed += dt

        if self._in_damage_window():
            self._set_boss_vulnerable(True)
            self._set_boss_damage_multiplier(1.0)
            self._spawn_accumulator = 0.0
            return

        self._set_boss_vulnerable(True)
        self._set_boss_damage_multiplier(self.SUMMON_DAMAGE_MULTIPLIER)
        self._spawn_accumulator += dt
        while self._spawn_accumulator >= self.SUMMON_INTERVAL:
            self._spawn_accumulator -= self.SUMMON_INTERVAL
            self._spawn_summoned_enemy()

    def actualizar(self, dt, acciones):
        if acciones.get("toggle_pause"):
            self.juego.actions["toggle_pause"] = False
            Pausa(self.juego).entrar_estado()
            return

        solid_tiles = self.tmx_map.get_tiles()
        self._update_boss_cycle(dt)
        blockers = solid_tiles + list(self.enemies)
        self.player.update(dt, acciones, blockers)

        for enemy in self.enemies:
            enemy.ai_behavior(self.player, dt, solid_tiles)

        self.enemy_projectiles.update(dt, solid_tiles)
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
