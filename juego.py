# Example file showing a circle moving on screen
import os,time,pygame

from estados.titulo import Titulo
from personajes.enemigos.enemy_factory import EnemyFactory
from objetos.object_factory import ObjectFactory

class Juego():
    def __init__(self):
        pygame.init()
        self.ancho, self.alto = 1024, 544
        self.game_canvas = pygame.Surface((self.ancho, self.alto))
        self.screen = pygame.display.set_mode((self.ancho, self.alto))
        self.actions = {"left":False, "right":False, "up":False, "down":False, "attack1":False,"enter":False, "toggle_pause":False}
        self.debug=False
        self.dt, self.prev_time = 0,0
        self.running, self.playing = True, True
        self.clock = pygame.time.Clock()
        self.running = True
        self.enemy_factory= EnemyFactory(self, "personajes/enemigos/enemy_list.json")
        self.object_factory = ObjectFactory("objetos/object_list.json")
        self.state_stack = []
        self.load_assets()
        self.load_states()

    def game_loop(self):
        while self.running:
            self.get_dt()
            self.get_events()
            self.update()
            self.render()

    def get_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.actions["left"] = True
                if event.key == pygame.K_d:
                    self.actions["right"] = True
                if event.key == pygame.K_w:
                    self.actions["up"] = True
                if event.key == pygame.K_s:
                    self.actions["down"] = True
                if event.key == pygame.K_SPACE:
                    self.actions["attack1"] = True
                if event.key == pygame.K_RETURN:
                    self.actions["enter"] = True
                if event.key == pygame.K_ESCAPE:
                    self.actions["toggle_pause"] = True
                if event.key == pygame.K_PERIOD:
                    self.debug = not self.debug
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    self.actions["left"] = False
                if event.key == pygame.K_d:
                    self.actions["right"] = False
                if event.key == pygame.K_w:
                    self.actions["up"] = False
                if event.key == pygame.K_s:
                    self.actions["down"] = False
                if event.key == pygame.K_SPACE:
                    self.actions["attack1"] = False
                if event.key == pygame.K_RETURN:
                    self.actions["enter"] = False
    def update(self):
        self.state_stack[-1].actualizar(self.dt, self.actions)

    def render(self):
        # Render current state to the canvas, then scale to the screen (como el ejemplo)
        self.state_stack[-1].dibujar(self.game_canvas)
        self.screen.blit(
            pygame.transform.scale(self.game_canvas, self.screen.get_size()),
            (0, 0),
        )
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
        for k in self.actions:
            self.actions[k] = False

    def load_states(self):
        self.title_screen = Titulo(self)
        self.state_stack.append(self.title_screen)

    @property
    def actual_state(self):
        return self.state_stack[-1]

if __name__ == "__main__":
    j = Juego()
    while j.running:
        j.game_loop()
