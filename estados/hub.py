import os
import pygame
from assets.tiles import TiledTMX
from estados.estado import Estado
from estados.area_experiment import AreaExperiment
from personajes.player import Player

class Hub(Estado):
    def __init__(self, juego):
        Estado.__init__(self,juego)

        # guarda el mapa desde Tiled como TMX (layers en CSV) en esta ruta.
        tmx_path = os.path.join("assets", "Fondo_Hub", "hub.tmx")

        # Esto detecta todos los tilesets 
        self.tmx_map = TiledTMX(tmx_path)

        self.map_layer_order = list(self.tmx_map.layer_names)
        
        # TODO: meter el spawn_point del player, que está en el TMX
        self.player = Player(self.juego)       

        # Punto medio de la puerta del hub
        doors = self.tmx_map.get_objects(layer="puerta")
        door = next((d for d in doors if d.width > 0 and d.height > 0), None)
        self._door_center = door.rect.center
        #Modificamos hardcodeado el punto de la puerta, en el juego coincide demasiado abajo
        self._door_center = (self._door_center[0], self._door_center[1] - 70)

    def actualizar(self, dt, acciones):
        self.player.update(dt, acciones)

        if self.player.get_rect().collidepoint(self._door_center):
            AreaExperiment(self.juego).entrar_estado()
            return

    def dibujar(self, pantalla):
        pantalla.fill((0, 0, 0))
        self.tmx_map.draw(pantalla, only=self.map_layer_order)
        self.player.render(pantalla)