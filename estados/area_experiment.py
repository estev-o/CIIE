import os
from estados.estado import Estado
from assets.tiles import TiledTMX
import random
import pygame

from ui.health_bar import HealthBarManager
from ui.player_health_bar import PlayerHealthBar
from ui.adn_counter import ADNCounter
from personajes.enemigos.chest import Chest
from estados.area_administrativa import AreaAdministrativa
from dialogos.interaction import Interaction

NIVEL_FORZADO = "area_exp3.tmx"  # Para pruebas, fuerza a entrar a esta área de experimentación específica


class AreaExperiment(Estado):
    niveles = ["area_exp1.tmx", "area_exp2.tmx","area_exp3.tmx", "area_exp4.tmx", "area_exp5.tmx", "area_exp6.tmx"]
    distintas_areas = niveles.copy()
    areas_visitadas = []
    areas_to_continue = 3

    def __init__(self, juego, reset= False):
        Estado.__init__(self,juego)

        imagen_original = pygame.image.load("assets/UI/cursor/crosshair.png").convert_alpha()
        self.cursor_img = pygame.transform.scale(imagen_original, (30, 30))

        if reset:
            AreaExperiment.distintas_areas = AreaExperiment.niveles.copy()
            AreaExperiment.areas_visitadas.clear()

        if len(AreaExperiment.distintas_areas) == 0:
            AreaExperiment.distintas_areas, AreaExperiment.areas_visitadas = AreaExperiment.areas_visitadas, AreaExperiment.distintas_areas

        # Elige aleatoriamente entre los mapas de experimentación
        tmx_elegido = random.choice(AreaExperiment.distintas_areas)

        # Eliminar el nivel elegido de las areas para no tenerlo en cuenta para el siguiente nivel
        AreaExperiment.distintas_areas.remove(tmx_elegido)
        AreaExperiment.areas_visitadas.append(tmx_elegido)

        tmx_path = os.path.join("assets", "area_experimentacion", tmx_elegido)

        # CODIGO DEBUG, BORRAR
        if juego.debug:
            tmx_path = os.path.join("assets", "area_experimentacion", NIVEL_FORZADO)

        self.tmx_map = TiledTMX(tmx_path)
        self.map_layer_order = list(self.tmx_map.layer_names)
        self._door_open = False
        self.iniciar_texto_nivel(f"ÁREA EXPERIMANTACION ({len(AreaExperiment.areas_visitadas)}/{self.areas_to_continue})", 3000)

        self.player = self.juego.player


        r = self.player.get_rect()
        spawn = self.tmx_map.get_objects(layer="spawn_point")[0]
        self.player.pos_x = spawn.x - (r.width / 2)
        self.player.pos_y = spawn.y - (r.height / 2)


        enemy_names = ["mock_explosive", "mock_ranger", "mock_melee"]
        enemy_probabilities = [10, 50, 40]
        
        # Enemies
        spawns = list(self.tmx_map.get_objects(layer="spawn_enemies"))
        select_number = int((len(AreaExperiment.areas_visitadas) / AreaExperiment.areas_to_continue) * len(spawns))
        
        positions = random.sample(spawns, select_number)
        enemy_types = random.choices(enemy_names, weights=enemy_probabilities, k=select_number)
        for i in range(select_number):
            enemy = juego.enemy_factory.create_enemy(enemy_types[i], positions[i].x, positions[i].y)
            self.append_enemy(enemy)

        # contamos los enemigos de el área
        self.total_enemies = len(self.enemies)
        self.enemies_alive = self.total_enemies

        # Punto medio de la puerta, para detectar la colisión con jugador
        door = self.tmx_map.get_objects(layer="puerta")[0]
        self._door_center = door.rect.center

        # Spawns de cofres definidos en Tiled (object layer: spawn_cofre).
        chest_spawns = list(self.tmx_map.get_objects(layer="spawn_cofre"))
        random.shuffle(chest_spawns)
        chest_count = random.randint(0, min(3, len(chest_spawns)))
        for spawn_chest in chest_spawns[:chest_count]:
            raw_rarity = spawn_chest.properties.get("rarity")
            rarity = int(raw_rarity) if raw_rarity is not None else random.randint(1, 7)
            chest = juego.enemy_factory.create_enemy("chest", spawn_chest.x, spawn_chest.y, rarity=rarity)
            if chest is not None:
                self.append_enemy(chest)
                self.append_interaction(
                    Interaction(
                        chest,
                        "Abrir [E]",
                        chest,
                        "interact",
                        distance=50,
                        text_controller="Abrir [A]",
                        game=self.juego,
                        availability_check=lambda c=chest: (not c.locked and not c.opened and not c.opening),
                    )
                )
        
        # Initializar health bar manager
        self.health_bar_manager = HealthBarManager(self.enemies)
        
        # Player Health Bar
        self.player_health_bar = PlayerHealthBar(25, self.juego.alto - 65)
        self.adn_counter = ADNCounter()
        self.adn_counter.set_position(
            self.player_health_bar.x,
            self.player_health_bar.y - self.adn_counter.height - 8,
        )

    def actualizar(self, dt, acciones):
        if acciones.get("toggle_pause"):
            self.juego.actions["toggle_pause"] = False
            from estados.pausa import Pausa
            Pausa(self.juego).entrar_estado()
            return
            
        if getattr(self, "_nivel_activo", False):
            return

        solid_tiles = self.tmx_map.get_tiles()
        self.player.update(dt, acciones, solid_tiles)
        for enemy in self.enemies:
            enemy.ai_behavior(self.player, dt, solid_tiles)
        self.objects.update(self.player, dt)
        self.update_interactions(self.player, acciones)
        
        self.health_bar_manager.update()
        self.player_health_bar.update(dt, self.player.remaining_life, self.player.max_live)

        self.enemy_projectiles.update(dt, solid_tiles)
        # Los cofres no cuentan como enemigos vivos para abrir la puerta.
        self.enemies_alive = sum(1 for enemy in self.enemies if enemy.__class__.__name__ != "Chest")

        if self.enemies_alive == 0 and not self._door_open:
            self._door_open = True
            self.juego.sound_engine.play("door")  # sonido puerta
            # Abrir puerta: ocultar el layer de puerta cerrada.
            self.map_layer_order = [name for name in self.map_layer_order if name != "puerta_cerrada"]

            
            # Desbloquear cofres
            for enemy in self.enemies:
                if isinstance(enemy, Chest):
                    enemy.unlock()

        if self.enemies_alive == 0:
            if self.player.body_hitbox.collidepoint(self._door_center):
                if self.juego.debug and self.juego.skip_to_boss:
                    from estados.boss_final import BossFinal
                    BossFinal(self.juego).entrar_estado()
                elif len(AreaExperiment.areas_visitadas) == AreaExperiment.areas_to_continue:
                    AreaAdministrativa(self.juego, reset=True).entrar_estado()
                else:
                    AreaExperiment(self.juego).entrar_estado()

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
        self.dibujar_texto_nivel(pantalla);
        self.draw_interactions(pantalla)

        if self.juego.debug:
            font = pygame.font.Font(None, 28)
            text = font.render(f"VIDA = {int(self.player.remaining_life)}", True, (255, 255, 255))
            text_rect = text.get_rect(topright=(pantalla.get_width() - 12, 10))
            pantalla.blit(text, text_rect)
            self.player.debug_draw_hitbox(pantalla, (0, 255 ,0))
            self.player.attack_launcher1.debug_draw_hitbox(pantalla, (255, 255 ,0))
            for enemy in self.enemies:
                enemy.debug_draw_hitbox(pantalla, (0, 255 ,255))
            for projectile in self.enemy_projectiles:
                pygame.draw.rect(pantalla, (255, 0, 0), projectile.rect, 1)
