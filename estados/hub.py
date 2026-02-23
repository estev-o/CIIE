import os
import random
import pygame
from assets.tiles import TiledTMX
from estados.estado import Estado
from estados.area_experiment import AreaExperiment
from personajes.blob import Blob
from objetos.mejoras.catalogo import listar_mejoras
from ui.adn_counter import ADNCounter
from ui.player_health_bar import PlayerHealthBar
from dialogos.interaction import Interaction
from estados.pausa import Pausa


DEBUG = False
class Hub(Estado):
    SHOP_SELECTION_LAYERS = ("seleccion_tienda1", "seleccion_tienda2", "seleccion_tienda3")

    def __init__(self, juego):
        Estado.__init__(self,juego)

        # guarda el mapa desde Tiled como TMX (layers en CSV) en esta ruta.
        tmx_path = os.path.join("assets", "Fondo_Hub", "hub.tmx")

        # Esto detecta todos los tilesets
        self.tmx_map = TiledTMX(tmx_path)
        self.map_layer_order = [
            name for name in self.tmx_map.layer_names if name not in self.SHOP_SELECTION_LAYERS
        ]

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

        self.mejoras_tienda = self._generar_mejoras_tienda()
        if hasattr(self.blob, "dialog") and hasattr(self.blob.dialog, "set_shop_items"):
            self.blob.dialog.game = self.juego
            self.blob.dialog.set_shop_items(self.mejoras_tienda)

        # Se añade interaccion de Blob
        self.append_interaction(
            Interaction(self.blob, "Hablar [E]", self.blob.dialog, "interact")
        )

    def _generar_mejoras_tienda(self):
        spawns = self.tmx_map.get_objects(layer="spawn_mejoras")
        pool = listar_mejoras()
        if not spawns or not pool:
            return []

        if len(pool) >= len(spawns):
            seleccion = random.sample(pool, len(spawns))
        else:
            seleccion = [random.choice(pool) for _ in spawns]

        cache_imagenes = {}
        mejoras_tienda = []
        for slot_index, (spawn, mejora) in enumerate(zip(spawns, seleccion)):
            asset_path = mejora.get("asset_path")
            if not asset_path:
                continue

            image = cache_imagenes.get(asset_path)
            if image is None:
                image = pygame.image.load(asset_path).convert_alpha()
                cache_imagenes[asset_path] = image

            rect = image.get_rect(center=(int(spawn.x), int(spawn.y)))
            mejoras_tienda.append({
                "slot_index": slot_index,
                "mejora_id": mejora.get("id"),
                "mejora": mejora,
                "image": image,
                "rect": rect,
            })

        return mejoras_tienda

    def _selected_shop_layer(self):
        dialog = getattr(self.blob, "dialog", None)
        if dialog is None or not dialog.is_active():
            return None

        actual_node = getattr(dialog, "actual_node", None) or {}
        if not actual_node.get("carousel_options"):
            return None

        options = actual_node.get("options") or []
        selected_index = getattr(dialog, "selected_option", 0)
        if selected_index < 0 or selected_index >= len(options):
            return None

        selected_option = options[selected_index]
        shop_item = selected_option.get("shop_item")
        if not isinstance(shop_item, dict):
            return None

        slot_index = int(shop_item.get("slot_index", -1))
        if slot_index < 0 or slot_index >= len(self.SHOP_SELECTION_LAYERS):
            return None

        return self.SHOP_SELECTION_LAYERS[slot_index]

    def actualizar(self, dt, acciones):

        if self.juego.debug:
            self.juego.adn = 100

        if acciones.get("toggle_pause"):
            self.juego.actions["toggle_pause"] = False
            Pausa(self.juego).entrar_estado()
            return

        tiles = self.tmx_map.get_tiles()
        player_blockers = tiles + [self.blob] #Metemos colisiones de fondo y las colisiones de Blob

        conditional_actions = {} # Para bloquear los movimientos del usuario si hay un dialogo o algo que interactua con el usuario
        if self.is_interaction_active():
            conditional_actions = {k:False for k in acciones}
            conditional_actions["aim_axis"] = (0.0, 0.0)
            conditional_actions["mouse_pos"] = (0, 0)
            conditional_actions["current_mode"] = acciones.get("current_mode", "keyboard_mouse")
        else:
            conditional_actions = acciones

        self.player.update(dt, conditional_actions, player_blockers) 
        self.blob.update(dt, acciones, tiles)
        self.player_health_bar.update(dt, self.player.remaining_life, self.player.max_live)
        self.update_interactions(self.player, conditional_actions)
        if self.player.body_hitbox.collidepoint(self._door_center):
            AreaExperiment(self.juego).entrar_estado()
            return

    def dibujar(self, pantalla):
        pantalla.fill((0, 0, 0))
        self.tmx_map.draw(pantalla, only=self.map_layer_order)
        selected_layer = self._selected_shop_layer()
        self.player.render(pantalla)
        self.player_health_bar.draw(pantalla)
        self.blob.render(pantalla)
        self.adn_counter.draw(pantalla, self.juego.adn)
        self.draw_interactions(pantalla)
        if selected_layer:
            self.tmx_map.draw(pantalla, only=[selected_layer])
        for item in self.mejoras_tienda:
            if item.get("vendida"):
                continue
            pantalla.blit(item["image"], item["rect"])
        if self.juego.debug:
            self.player.debug_draw_hitbox(pantalla, (0,255, 0))
            pygame.draw.circle(pantalla, (255, 0, 255), self._door_center, 5)  # Punto Magenta
