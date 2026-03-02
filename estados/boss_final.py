import pygame

from estados.estado import Estado
from estados.pausa import Pausa
from personajes.enemigos.gilbertov import Gilbertov
from ui.adn_counter import ADNCounter
from ui.health_bar import HealthBarManager
from ui.player_health_bar import PlayerHealthBar


class BossFinal(Estado):
    def __init__(self, juego):
        super().__init__(juego)
        self.player = self.juego.player

        # Sala minima: spawns fijos, sin mapa y sin fondo.
        self._spawn_player()
        self._spawn_boss()

        self.health_bar_manager = HealthBarManager(self.enemies)
        self.player_health_bar = PlayerHealthBar(25, self.juego.alto - 65)
        self.adn_counter = ADNCounter()
        self.adn_counter.set_position(
            self.player_health_bar.x,
            self.player_health_bar.y - self.adn_counter.height - 8,
        )

    def _spawn_player(self):
        rect = self.player.get_rect()
        self.player.pos_x = (self.juego.ancho - rect.width) / 2
        self.player.pos_y = self.juego.alto - rect.height - 30
        self.player.rect.topleft = (int(self.player.pos_x), int(self.player.pos_y))
        self.player.facing = "up"

    def _spawn_boss(self):
        # Gilbertov arriba centrado.
        self.boss = Gilbertov(self.juego, x=0, y=0)
        boss_rect = self.boss.get_rect()
        self.boss.pos_x = (self.juego.ancho - boss_rect.width) / 2
        self.boss.pos_y = 70
        self.boss.rect.topleft = (int(self.boss.pos_x), int(self.boss.pos_y))
        self.boss.facing = "down"
        self.append_enemy(self.boss)

    def actualizar(self, dt, acciones):
        if acciones.get("toggle_pause"):
            self.juego.actions["toggle_pause"] = False
            Pausa(self.juego).entrar_estado()
            return

        solid_tiles = []
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
