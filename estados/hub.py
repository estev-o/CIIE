import os
import pygame
from assets.tiles import TiledTMX
from estados.estado import Estado
from estados.area_experiment import AreaExperiment
from personajes.player import Player
DEBUG = True
class Hub(Estado):
    def __init__(self, juego):
        Estado.__init__(self,juego)

        # guarda el mapa desde Tiled como TMX (layers en CSV) en esta ruta.
        tmx_path = os.path.join("assets", "Fondo_Hub", "hub.tmx")

        # ataques que estan activos en este nivel
        self.attacks = []

        # Esto detecta todos los tilesets
        self.tmx_map = TiledTMX(tmx_path)
        self.map_layer_order = list(self.tmx_map.layer_names)

        # Cargamos el jugador y su spawn
        self.player = Player(self.juego)
        # get_objects devuelve una lista de objetos, aunque en este caso solo hay uno, el spawn del jugador
        spawn = self.tmx_map.get_objects(layer="spawn_point")[0]
        r = self.player.get_rect()
        self.player.pos_x = spawn.x - (r.width / 2)
        self.player.pos_y = spawn.y - (r.height / 2)

        # Punto medio de la puerta del hub, para detectar la colisión con jugador
        door = self.tmx_map.get_objects(layer="puerta")[0]
        self._door_center = door.rect.center

    def actualizar(self, dt, acciones):
        self.player.update(dt, acciones)

        for attack in self.attacks[:]:
            attack.update(dt, acciones)
        if self.player.body_hitbox.collidepoint(self._door_center):
            AreaExperiment(self.juego).entrar_estado()
            return

    def dibujar(self, pantalla):
        pantalla.fill((0, 0, 0))
        self.tmx_map.draw(pantalla, only=self.map_layer_order)
        self.player.render(pantalla)
        if DEBUG:
            self.player.debug_draw_hitbox(pantalla, (0,255, 0))
            pygame.draw.circle(pantalla, (255, 0, 255), self._door_center, 5)  # Punto Magenta
        
        for attack in self.attacks[:]:
            attack.render(pantalla)
