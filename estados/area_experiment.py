import os
from estados.estado import Estado
from assets.tiles import TiledTMX
import random

from personajes.player import Player
NIVEL_FORZADO = "area_exp1.tmx"  # Para pruebas, fuerza a entrar a esta área de experimentación específica


class AreaExperiment(Estado):
    def __init__(self, juego):
        Estado.__init__(self,juego)
        # Elige aleatoriamente entre dos mapas de experimentación
        distintas_areas = ["area_exp1.tmx", "area_exp2.tmx"]
        tmx_elegido = random.choice(distintas_areas)
        tmx_path = os.path.join("assets", "area_experimentacion", tmx_elegido)

        # CODIGO DEBUG, BORRAR
        if juego.debug:
            tmx_path = os.path.join("assets", "area_experimentacion", NIVEL_FORZADO)

        self.tmx_map = TiledTMX(tmx_path)
        self.map_layer_order = list(self.tmx_map.layer_names)

        self.player = Player(self.juego)
        r = self.player.get_rect()
        spawn = self.tmx_map.get_objects(layer="spawn_point")[0]
        self.player.pos_x = spawn.x - (r.width / 2)
        self.player.pos_y = spawn.y - (r.height / 2)

        self.enemy = juego.enemy_factory.create_enemy("mock_enemy", 500, 300)
        self.append_enemy(self.enemy)
        self.enemy = juego.enemy_factory.create_enemy("mock_enemy", 200, 300)
        self.append_enemy(self.enemy)

    def actualizar(self, dt, acciones):
        if acciones.get("esc"):
            self.juego.actions["esc"] = False
            from estados.pausa import Pausa
            Pausa(self.juego).entrar_estado()
            return
        solid_tiles = self.tmx_map.get_tiles()
        self.player.update(dt, acciones, solid_tiles)
        for enemy in self.enemies:
            enemy.ai_behavior(self.player, dt, solid_tiles)

    def dibujar(self, pantalla):
        pantalla.fill((0, 0, 0))
        self.tmx_map.draw(pantalla, only=self.map_layer_order)
        self.enemies.draw(pantalla)
        self.player.render(pantalla)
        if self.juego.debug:
            self.player.debug_draw_hitbox(pantalla, (0, 255 ,0))
            for enemy in self.enemies:
                enemy.debug_draw_hitbox(pantalla, (0, 255 ,255))
