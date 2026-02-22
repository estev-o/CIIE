import pygame
from dialogos.interactuable import Interactuable
from dialogos.sound_bip import sound_bip

font = pygame.font.SysFont("arial", 22)
small_font = pygame.font.SysFont("arial", 18)

# ACTION KEYS
continue_key = "enter"
previous_key = "arrowUp"
next_option = "arrowDown"
previous_key_alt = "arrowLeft"
next_option_alt = "arrowRight"

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
        
        self.shop_items = []

    def is_active(self):
        return self.active

    def load_dialogs(self, structure):
        self.dialog_structure = structure

    def interact(self):
        if self.shop_items:
            self.set_shop_items(self.shop_items)
        self.start("init")

    def set_shop_items(self, shop_items):
        self.shop_items = list(shop_items or [])

        target_shop_node = "tienda_lista" if "tienda_lista" in self.dialog_structure else "tienda"
        if target_shop_node not in self.dialog_structure:
            return

        options = []
        for item in self.shop_items:
            if item.get("vendida"):
                continue
            mejora = item.get("mejora", {})
            nombre = mejora.get("nombre", "Mejora")
            coste = int(mejora.get("coste_adn", 0))
            descripcion = mejora.get("descripcion", "")
            mejora_id = mejora.get("id")
            comprada = False
            if mejora_id and hasattr(getattr(self, "game", None), "has_mejora"):
                comprada = self.game.has_mejora(mejora_id)

            options.append(
                {
                    "text": nombre,
                    "nombre": nombre,
                    "next": "tienda_compra_pendiente",
                    "descripcion": descripcion,
                    "coste_adn": coste,
                    "estado": "Ya comprada" if comprada else "",
                    "mejora_id": mejora_id,
                    "apply": mejora.get("apply"),
                    "shop_item": item,
                }
            )

        if not options:
            options.append({"text": "Ahora mismo no tengo stock", "next": "init"})
        self.dialog_structure[target_shop_node]["options"] = options
        self.dialog_structure[target_shop_node]["f"] = self._resolve_shop_purchase

    def _set_shop_result_text(self, text):
        if "tienda_compra_pendiente" in self.dialog_structure:
            self.dialog_structure["tienda_compra_pendiente"]["text"] = str(text)

    def _resolve_shop_purchase(self):
        if not self.actual_node:
            return

        options = self.actual_node.get("options") or []
        if not options:
            self._set_shop_result_text("Ahora mismo no tengo nada que venderte.")
            return

        option = options[self.selected_option]
        mejora_id = option.get("mejora_id")
        nombre = option.get("nombre") or option.get("text") or "esa mejora"
        coste = int(option.get("coste_adn") or 0)

        if not mejora_id:
            self._set_shop_result_text("Ahora mismo no tengo stock.")
            return

        game = getattr(self, "game", None)
        if game is None:
            self._set_shop_result_text("No puedo venderte nada ahora mismo.")
            return

        if hasattr(game, "has_mejora") and game.has_mejora(mejora_id):
            self._set_shop_result_text(f"Esa mejora ya la tienes: {nombre}.")
            return

        if not hasattr(game, "spend_adn") or not game.spend_adn(coste):
            self._set_shop_result_text(f"No tienes ADN suficiente para {nombre}.")
            return

        try:
            unlocked = game.desbloquear_mejora(mejora_id) if hasattr(game, "desbloquear_mejora") else False
        except Exception:
            if hasattr(game, "add_adn"):
                game.add_adn(coste)
            self._set_shop_result_text("Algo salio mal con la compra. Vuelve a intentarlo.")
            return

        if not unlocked:
            if hasattr(game, "add_adn"):
                game.add_adn(coste)
            self._set_shop_result_text(f"Esa mejora ya la tenias: {nombre}.")
            return

        aplicar = option.get("apply")
        if callable(aplicar) and hasattr(game, "player"):
            aplicar(game.player)

        shop_item = option.get("shop_item")
        if isinstance(shop_item, dict):
            shop_item["vendida"] = True

        self._set_shop_result_text(f"Hecho. Te vendo {nombre} por {coste} ADN.")
        self.set_shop_items(self.shop_items)

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

            text_to_draw = self._get_display_text()
            self._draw_text(
                screen,
                text_to_draw,
                self.rect.x+15,
                self.rect.y+45
            )

            if self.are_options_available:
                self._draw_options(screen)
                self._draw_selected_option_info(screen)
                hint = self.actual_node.get("options_hint")
                if hint:
                    indicator = small_font.render(hint, True, (200,200,200))
                    screen.blit(
                        indicator,
                        (self.rect.right - indicator.get_width() - 15, self.rect.y + 15),
                    )

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

    def _get_display_text(self):
        if not self.actual_node:
            return self.visible_text
        if not self.actual_node.get("selected_option_name_in_text"):
            return self.visible_text
        if not self.are_options_available:
            return self.visible_text
        options = self.actual_node.get("options") or []
        if not options:
            return self.visible_text
        option = options[self.selected_option]
        return str(option.get("nombre") or option.get("text") or "")

    def _draw_options(self, screen):
        if self.actual_node.get("carousel_options"):
            if not self.actual_node.get("options"):
                return
            pager = small_font.render(
                f"{self.selected_option + 1}/{len(self.actual_node['options'])}",
                True,
                (200,200,200),
            )
            y = self.rect.bottom - 45
            screen.blit(pager, (self.rect.right - pager.get_width() - 15, y))
            return

        step = int(self.actual_node.get("options_step", 30))
        text_font = small_font if self.actual_node.get("small_options") else font
        if "options_y" in self.actual_node:
            y = int(self.actual_node.get("options_y", self.rect.bottom - 90))
        else:
            # Ajuste automatico para que las opciones no se salgan del cuadro
            # cuando haya mas entradas (ej. menu de Blob con una opcion extra).
            margin_bottom = 12
            y = self.rect.bottom - margin_bottom - (len(self.actual_node["options"]) * step)
            y = max(y, self.rect.y + 70)
        for i, option in enumerate(self.actual_node["options"]):
            color = (255,255,0) if i == self.selected_option else (200,200,200)
            text = text_font.render(option["text"], True, color)
            screen.blit(text, (self.rect.x+30, y))
            y += step

    def _draw_selected_option_info(self, screen):
        if not self.actual_node.get("show_selected_option_info"):
            return
        if not self.actual_node.get("options"):
            return

        option = self.actual_node["options"][self.selected_option]
        descripcion = option.get("descripcion", "")
        coste = option.get("coste_adn")
        estado = option.get("estado", "")

        base_x = self.rect.x + 15
        line_y = self.rect.y + 88

        if coste is not None:
            coste_render = small_font.render(f"Coste: {coste} ADN", True, (180,220,255))
            screen.blit(coste_render, (base_x, line_y))
            line_y += 18

        if estado:
            estado_render = small_font.render(estado, True, (220,220,180))
            screen.blit(estado_render, (base_x, line_y))
            line_y += 18

        if descripcion:
            self._draw_text_wrapped(
                screen,
                descripcion,
                base_x,
                line_y,
                max_width=self.rect.width - 30,
                text_font=small_font,
                color=(220,220,220),
            )

    def _draw_text_wrapped(self, screen, text, x, y, max_width, text_font, color):
        words = str(text).split(" ")
        line = ""
        for word in words:
            test_line = line + word + " "
            surface = text_font.render(test_line, True, color)
            if surface.get_width() > max_width and line:
                screen.blit(text_font.render(line, True, color), (x, y))
                y += text_font.get_height()
                line = word + " "
            else:
                line = test_line
        if line:
            screen.blit(text_font.render(line, True, color), (x, y))

    def handle_event(self, actions):
        if not self.active:
            return

        if continue_key in actions and actions[continue_key]:
            if self.are_options_available and self.option_cooldown > 0:
                pass # Ignore 'enter' if options just appeared and are on cooldown
            else:
                actions[continue_key] = False
                self.continue_writing()
        elif (previous_key in actions and actions[previous_key]) or (
            previous_key_alt in actions and actions[previous_key_alt]):
            if self.cooldown_nav <= 0:
                actions[previous_key] = False
                actions[previous_key_alt] = False
                self.move_option(-1)
                self.cooldown_nav = self.delay_nav
        elif (next_option in actions and actions[next_option]) or (
            next_option_alt in actions and actions[next_option_alt]):
            if self.cooldown_nav <= 0:
                actions[next_option] = False
                actions[next_option_alt] = False
                self.move_option(1)
                self.cooldown_nav = self.delay_nav