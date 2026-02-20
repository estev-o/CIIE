import os
import pygame
from assets.tiles import TiledTMX
from estados.estado import Estado
from estados.area_experiment import AreaExperiment
from personajes.blob import Blob
from ui.adn_counter import ADNCounter
from ui.player_health_bar import PlayerHealthBar
DEBUG = True
class Hub(Estado):
    def __init__(self, juego):
        Estado.__init__(self,juego)

        # guarda el mapa desde Tiled como TMX (layers en CSV) en esta ruta.
        tmx_path = os.path.join("assets", "Fondo_Hub", "hub.tmx")

        # Esto detecta todos los tilesets
        self.tmx_map = TiledTMX(tmx_path)
        self.map_layer_order = list(self.tmx_map.layer_names)

        # Cargamos el jugador y su spawn
        self.player = self.juego.player
        # get_objects devuelve una lista de objetos, aunque en este caso solo hay uno, el spawn del jugador
        spawn = self.tmx_map.get_objects(layer="spawn_point")[0]
        r = self.player.get_rect()
        self.player.pos_x = spawn.x - (r.width / 2)
        self.player.pos_y = spawn.y - (r.height / 2)

        # Punto de la puerta del hub, para detectar la colisión con jugador
        door = self.tmx_map.get_objects(layer="puerta")[0]
        self._door_center = door.rect.center

        # Metemos al NPC Blob, el vendedor del hub
        self.blob = Blob(self.juego)
        spawn_blob = self.tmx_map.get_objects(layer="spawn_blob")[0]
        rb = self.blob.get_rect()
        self.blob.pos_x = spawn_blob.x - (rb.width / 2)
        self.blob.pos_y = spawn_blob.y - (rb.height / 2)
        self.blob.rect.topleft = (int(self.blob.pos_x), int(self.blob.pos_y))
        self.player_health_bar = PlayerHealthBar(25, self.juego.alto - 65)
        self.adn_counter = ADNCounter()
        self.adn_counter.set_position(
            self.player_health_bar.x,
            self.player_health_bar.y - self.adn_counter.height - 8,
        )

    def actualizar(self, dt, acciones):
        if acciones.get("esc"):
            self.juego.actions["esc"] = False
            from estados.pausa import Pausa
            Pausa(self.juego).entrar_estado()
            return
        
        tiles = self.tmx_map.get_tiles()
        player_blockers = tiles + [self.blob] #Metemos colisiones de fondo y las colisiones de Blob
        self.player.update(dt, acciones, player_blockers)
        self.blob.update(dt, acciones, tiles)
        self.player_health_bar.update(dt, self.player.remaining_life, self.player.max_live)

        if self.player.body_hitbox.collidepoint(self._door_center):
            AreaExperiment(self.juego).entrar_estado()
            return

    def dibujar(self, pantalla):
        pantalla.fill((0, 0, 0))
        self.tmx_map.draw(pantalla, only=self.map_layer_order)
        self.blob.render(pantalla)
        self.player.render(pantalla)
        self.player_health_bar.draw(pantalla)
        self.adn_counter.draw(pantalla, self.juego.adn)
        if self.juego.debug:
            self.player.debug_draw_hitbox(pantalla, (0,255, 0))
            pygame.draw.circle(pantalla, (255, 0, 255), self._door_center, 5)  # Punto Magenta
