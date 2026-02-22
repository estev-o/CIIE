import pygame
from dialogos.interactuable import Interactuable
from dialogos.sound_bip import sound_bip

font = pygame.font.SysFont("arial", 22)
small_font = pygame.font.SysFont("arial", 18)

# ACTION KEYS
continue_key = "enter"
previous_key = "arrowUp"
next_option = "arrowDown"

class Dialog(Interactuable):
    def __init__(self, structure, rect=(247,320,530,180)):
        self.rect = pygame.Rect(rect)
        self.active = False                     # Estado del dialogo (si se ve en pantalla)
        self.actual_node = None                 # Nodo actual de la estructura
        self.dialog_structure = structure       # Estructura de dialogo

        self.visible_text = ""                  # Codigo visible actual
        self.complete_text = ""                 # Codigo objetivo
        self.timer = 0                          # Acumulador de dt
        self.speed = 40                         # Velocidad del texto
        self.finished = False                   # Si se ha terminado de escribir

        self.are_options_available = False      # Si hay opciones en el nodo actual
        self.selected_option = 0                # Opcion seleccionada
        
        self.cooldown_nav = 0                   # Cooldown_nav preventing ultra-fast scroll
        self.delay_nav = 0.15
        
        self.option_cooldown = 0                # Cooldown before an option can be selected

    def is_active(self):
        return self.active

    def load_dialogs(self, structure):
        """ Ejemplo de estructura:
        structure_dialog = {
            "init": {
                "author": "NPC",
                "text": "Hola viajero. Que deseas?",
                "options": [
                    {"text": "Quien eres?", "next": "quien"},
                    {"text": "Que es este lugar?", "next": "lugar"},
                    {"text": "Obtener recompensa", "next": "recompensa"},
                    {"text": "Salir", "next": None}
                ],
                "f": None
            },
            "quien": {
                "author": "NPC",
                "text": "Soy el guardian del bosque.",
                "next": "init"
                "f": None
            },
            "lugar": {
                "author": "NPC",
                "text": "Este es el reino antiguo de las sombras.",
                "next": "init",
                "f": None
            },
            "recompensa": {
                "author": "NPC",
                "text": "Toma esta recompensa.",
                "next": "init",
                "f": dar_recompensa
            }
        }
        """
        self.dialog_structure = structure

    def interact(self):
        self.start("init")

    def start(self, node="init"):
        self.active = True
        self._load_node(node)

    def _load_node(self, name):
        if name is None:
            self.active = False
            return

        self.actual_node = self.dialog_structure[name]
        self.complete_text = self.actual_node["text"]
        self.visible_text = ""
        self.timer = 0
        self.finished = False
        self.are_options_available = False
        self.selected_option = 0
        self.cooldown_nav = 0
        self.option_cooldown = 0

    def update(self, dt, actions):
        if self.cooldown_nav > 0:
            self.cooldown_nav -= dt
            
        if self.option_cooldown > 0:
            self.option_cooldown -= dt
            
        self.handle_event(actions)

        if not self.active or self.finished:
            return

        self.timer += dt
        char_objective = int(self.timer * self.speed)

        if char_objective > len(self.visible_text):
            next = self.complete_text[len(self.visible_text)]
            self.visible_text += next
            if next != " ":
                sound_bip.play()

        if len(self.visible_text) >= len(self.complete_text):
            self.finished = True
            if "options" in self.actual_node:
                if not self.are_options_available:
                    self.option_cooldown = 0.5  # Set cooldown when options first appear
                self.are_options_available = True

    def continue_writing(self):
        if not self.finished:
            self.visible_text = self.complete_text
            self.finished = True
            if "options" in self.actual_node:
                self.are_options_available = True
                self.option_cooldown = 0.5  # Set cooldown when skipped to options
            return

        if "options" in self.actual_node:
            next = self.actual_node["options"][self.selected_option]["next"]
            if self.actual_node["f"]:
                self.actual_node["f"]()
            self._load_node(next)
        else:
            next = self.actual_node.get("next")
            self._load_node(next)

    def move_option(self, direction):
        if not self.are_options_available:
            return

        self.selected_option += direction
        self.selected_option = max(
            0,
            min(self.selected_option,
                len(self.actual_node["options"]) - 1)
        )

    def draw(self, screen):
        if self.is_active():
            pygame.draw.rect(screen, (0,0,0), self.rect, border_radius=15)
            pygame.draw.rect(screen, (255,255,255), self.rect, 2, border_radius=15)

            author = self.actual_node["author"]
            txt_author = font.render(author + ":", True, (255,255,255))
            screen.blit(txt_author, (self.rect.x+15, self.rect.y+15))

            self._draw_text(
                screen,
                self.visible_text,
                self.rect.x+15,
                self.rect.y+45
            )

            if self.are_options_available:
                self._draw_options(screen)

            elif self.finished:
                indicator = small_font.render("ENTER (continuar)", True, (200,200,200))
                screen.blit(indicator, (self.rect.right - 165, self.rect.y+15))

    def _draw_text(self, screen, text, x, y):
        words = text.split(" ")
        line = ""

        for word in words:
            test_line = line + word + " "
            surface = font.render(test_line, True, (255,255,255))

            if surface.get_width() > self.rect.width - 30:
                screen.blit(font.render(line, True, (255,255,255)), (x,y))
                y += font.get_height()
                line = word + " "
            else:
                line = test_line

        screen.blit(font.render(line, True, (255,255,255)), (x,y))

    def _draw_options(self, screen):
        y = self.rect.bottom - 90
        for i, option in enumerate(self.actual_node["options"]):
            color = (255,255,0) if i == self.selected_option else (200,200,200)
            text = font.render(option["text"], True, color)
            screen.blit(text, (self.rect.x+30, y))
            y += 30

    def handle_event(self, actions):
        if not self.active:
            return

        if continue_key in actions and actions[continue_key]:
            if self.are_options_available and self.option_cooldown > 0:
                pass # Ignore 'enter' if options just appeared and are on cooldown
            else:
                actions[continue_key] = False
                self.continue_writing()
        elif previous_key in actions and actions[previous_key]:
            if self.cooldown_nav <= 0:
                actions[previous_key] = False
                self.move_option(-1)
                self.cooldown_nav = self.delay_nav
        elif next_option in actions and actions[next_option]:
            if self.cooldown_nav <= 0:
                actions[next_option] = False
                self.move_option(1)
                self.cooldown_nav = self.delay_nav