# Example file showing a circle moving on screen
import os,time,pygame

from config.configuracion import Configuracion
#from estados.titulo import Titulo #Cutre
#from estados.titulo2 import Titulo #Version 1
from estados.titulo3 import Titulo #Version 2
#from estados.xD import Titulo #Sin sentido alguno

from personajes.enemigos.enemy_factory import EnemyFactory
from estados.fonts import Fuentes
from objetos.object_factory import ObjectFactory
from personajes.constants import PLAYER_DEATH
from personajes.player import Player
from sistemas.acciones import ActionManager

DEBUG = False
SKIP_HUB = False

class Juego():
    def __init__(self):
        pygame.init()
        self.configuracion=Configuracion()
        self.fonts=Fuentes()
        self.ancho, self.alto = 1024, 544
        self.game_canvas = pygame.Surface((self.ancho, self.alto))
        self.screen = pygame.display.set_mode((self.ancho, self.alto))
        
        self.action_manager = ActionManager()
        self.actions = self.action_manager.actions

        self.debug = DEBUG
        self.skip_hub = SKIP_HUB
        
        # pantalla completa
        if self.configuracion.get("pantalla_completa", False):
            self.screen = pygame.display.set_mode((self.ancho, self.alto), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.ancho, self.alto))
        self.dt, self.prev_time = 0,0
        self.running, self.playing = True, True
        self.clock = pygame.time.Clock()
        self.running = True
        self._death_screen_requested = False
        self.adn = 0
        self.player = Player(self)
        self.enemy_factory= EnemyFactory(self, "personajes/enemigos/enemy_list.json")
        self.object_factory = ObjectFactory("objetos/object_list.json")
        self.state_stack = []
        self.load_assets()
        self.load_states()

    def add_adn(self, amount):
        amount = int(amount)
        if amount <= 0:
            return self.adn
        self.adn += amount
        return self.adn

    def spend_adn(self, amount):
        amount = int(amount)
        if amount <= 0:
            return True
        if self.adn < amount:
            return False
        self.adn -= amount
        return True

    def game_loop(self):
        while self.running:
            self.get_dt()
            self.get_events()
            if not self.running:
                break
            if self._death_screen_requested:
                self.open_death_screen()
                continue
            
            self.action_manager.process_mouse_and_aim(self.game_canvas, self.screen)

            self.update()
            self.render()

    def reset_not_manteinable_keys(self):
        # Mantenido para compatibilidad si algo lo llama, pero el ActionManager ya lo hace internamente
        self.action_manager.reset_not_maintainable_keys()

    def get_events(self):
        events = self.action_manager.get_events()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == PLAYER_DEATH:
                self._death_screen_requested = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PERIOD:
                    self.debug = not self.debug
    def update(self):
        self.state_stack[-1].actualizar(self.dt, self.actions)

    def render(self):
        # Render current state to the canvas, then scale to the screen (como el ejemplo)
        self.state_stack[-1].dibujar(self.game_canvas)
        self.screen.blit(
            pygame.transform.scale(self.game_canvas, self.screen.get_size()),
            (0, 0),
        )
        
        if self.debug:
            self.draw_text(self.screen, f"Mode: {self.action_manager.current_mode}", (255, 0, 0), 120, 20)
            
        pygame.display.flip()

    def get_dt(self):
        self.dt = self.clock.tick(60) / 1000

    def draw_text(self, surface, text, color, x, y):
        font = pygame.font.Font(None, 36)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (int(x), int(y))
        surface.blit(text_surface, text_rect)

    def load_assets(self):
        pass

    def reset_keys(self):
        self.action_manager.reset_keys()

    def load_states(self):
        if self.debug and self.skip_hub:
            from estados.area_experiment import AreaExperiment
            self.state_stack.append(AreaExperiment(self))
        else:
            self.title_screen = Titulo(self)
            self.state_stack.append(self.title_screen)

    def open_death_screen(self):
        self._death_screen_requested = False
        pygame.event.clear(PLAYER_DEATH)
        self.reset_keys()
        from estados.muerte import Muerte
        if self.state_stack and self.actual_state.__class__.__name__ == "Muerte":
            return
        Muerte(self).entrar_estado()

    def start_new_run(self, start_state="menu"):
        pygame.event.clear(PLAYER_DEATH)
        self._death_screen_requested = False
        self.reset_keys()
        self.player = Player(self)
        self.state_stack = []
        if start_state == "hub":
            from estados.hub import Hub
            self.state_stack.append(Hub(self))
        else:
            self.state_stack.append(Titulo(self))

    @property
    def actual_state(self):
        return self.state_stack[-1]

if __name__ == "__main__":
    j = Juego()
    while j.running:
        j.game_loop()
