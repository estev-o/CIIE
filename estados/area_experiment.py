import pygame, os
from estados.estado import Estado
from assets.tiles import TiledTMX
import random
from personajes.player import Player

class AreaExperiment(Estado):
    def __init__(self, juego):
        Estado.__init__(self,juego)
        # Elige aleatoriamente entre dos mapas de experimentación
        distintas_areas = ["area_exp1.tmx", "area_exp2.tmx"]
        tmx_elegido = random.choice(distintas_areas)
        tmx_path = os.path.join("assets", "area_experimentacion", tmx_elegido)
        
        self.tmx_map = TiledTMX(tmx_path)
        self.map_layer_order = list(self.tmx_map.layer_names)


        self.player = Player(self.juego)       

    def actualizar(self, dt, acciones):
        self.player.update(dt, acciones)

    def dibujar(self, pantalla):
        pantalla.fill((0, 0, 0))
        self.tmx_map.draw(pantalla, only=self.map_layer_order)
        self.player.render(pantalla)