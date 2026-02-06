import os
import pygame
from assets.tiles import TiledTMX
from estados.estado import Estado
from personajes.player import Player

class Hub(Estado):
    def __init__(self, juego):
        Estado.__init__(self,juego)

        # guarda el mapa desde Tiled como TMX (layers en CSV) en esta ruta.
        tmx_path = os.path.join("assets", "Fondo_Hub", "hub.tmx")

        # Esto detecta todos los tilesets 
        self.tmx_map = TiledTMX(tmx_path)

        # Se usa el orden del TMX pero se podría cambiar el orden TODO: Util para sistema de colisiones??¿??¿?¿???
        self.map_layer_order = list(self.tmx_map.layer_names)
        
        self.player = Player(self.juego)       

    def actualizar(self, dt, acciones):
        self.player.update(dt, acciones)

    def dibujar(self, pantalla):
        pantalla.fill((0, 0, 0))
        self.tmx_map.draw(pantalla, only=self.map_layer_order)
        self.player.render(pantalla)