import pygame
from estados.menus.menu_base import Menu
from estados.menus.componentes import Boton
from estados.menus.menu_configuracion import MenuConfiguracion
from objetos.mejoras.catalogo import obtener_mejora


class Pausa(Menu):
    """Estado que implementa el menú principal de pausa y muestra mejoras activas."""
    def __init__(self, juego):
        Menu.__init__(self, juego)

        # Obtener gestor de fuentes del juego
        font = self.juego.fonts

        centro_x = juego.ancho // 2
        centro_y = juego.alto // 2

        # Crear botones usando componentes.py
        self.botones = [
            Boton(centro_x - 150, centro_y - 30, 300, 55, "Continuar", font.medium,
                  lambda: self.salir_estado()),
            Boton(centro_x - 150, centro_y + 40, 300, 55, "Configuración", font.medium,
                  lambda: MenuConfiguracion(self.juego).entrar_estado()),
            Boton(centro_x - 150, centro_y + 110, 300, 55, "Menú Principal", font.medium,
                  lambda:self.juego.fade_to(_ir_a_menu))
        ]

        #Función auxiliar que limpia pila estados y vuelve al menú principal
        def _ir_a_menu():
            while len(self.juego.state_stack) > 1:
                self.juego.state_stack.pop()
            from estados.menus.menu_principal import MenuPrincipal
            MenuPrincipal(self.juego).entrar_estado()

        self.botones[self.indice_seleccionado].seleccionado = True

        # Estado previo del ratón para detectar clicks
        self.pos_mouse_escalado = (0, 0)
        self.hover_mejora_index = None

        self.sidebar_rect = pygame.Rect(self.juego.ancho - 250, centro_y - 150, 220, 400)
        self.upgrade_icon_size = 46
        self.upgrade_items = self._crear_items_mejoras()

    def actualizar(self, dt, acciones):
        # Reducir cooldown de navegación
        if self.cooldown_nav > 0:
            self.cooldown_nav -= dt

        # Navegación circular teclado/mando
        if acciones.get("back") or acciones.get("toggle_pause"):
            if acciones.get("back"):
                self.juego.actions["back"] = False
            if acciones.get("toggle_pause"):
                self.juego.actions["toggle_pause"] = False
            self.salir_estado()
            return

        if self.cooldown_nav <= 0:
            if acciones.get("arrowUp"):
                self.cambiar_seleccion(-1)
                self.cooldown_nav = self.delay_nav
            elif acciones.get("arrowDown"):
                self.cambiar_seleccion(1)
                self.cooldown_nav = self.delay_nav

        # Activar opciones botones
        if acciones.get("enter") or acciones.get("interact"):
            self.juego.sound_engine.play("menu_accept")
            self.botones[self.indice_seleccionado].activar()
            self.juego.reset_keys()
            return

        # Obtener modo actual
        current_mode = acciones.get("current_mode", "keyboard_mouse")

        # Obtener posición del ratón ya escalada
        pos_mouse_escalado = acciones.get("mouse_pos", (0, 0))

        # Leer estado actual click izquierdo
        mouse_pressed = pygame.mouse.get_pressed()[0]

        # Detectar si el ratón se ha movido
        mouse_moved = (self._last_mouse_pos is not None
                       and pos_mouse_escalado != self._last_mouse_pos)

        # Guardar pos actual para comparar en el siguiente frame
        self._last_mouse_pos = pos_mouse_escalado
        self.pos_mouse_escalado = pos_mouse_escalado

        # Procesar hovering ratón sobre botones y mejoras
        if current_mode == "keyboard_mouse" and mouse_moved:
            for i, boton in enumerate(self.botones):
                if boton.verificar_hover(pos_mouse_escalado):
                    if i != self.indice_seleccionado:
                        self.botones[self.indice_seleccionado].seleccionado = False
                        self.indice_seleccionado = i
                        self.botones[self.indice_seleccionado].seleccionado = True
                        self.juego.sound_engine.play("menu_select")

            self.hover_mejora_index = None
            for i, item in enumerate(self.upgrade_items):
                if item["rect"].collidepoint(pos_mouse_escalado):
                    self.hover_mejora_index = i
                    break

        # Procesar click ratón sobre botones
        if current_mode == "keyboard_mouse" and mouse_pressed and not self.mouse_pressed_prev:
            for i, boton in enumerate(self.botones):
                if boton.verificar_click(pos_mouse_escalado):
                    self.indice_seleccionado = i
                    self.juego.sound_engine.play("menu_accept")
                    boton.activar()
                    self.juego.reset_keys()
                    return

        self.mouse_pressed_prev = mouse_pressed

        for boton in self.botones:
            boton.actualizar(dt)

    def cambiar_seleccion(self, direccion):
        self.botones[self.indice_seleccionado].seleccionado = False
        self.indice_seleccionado = (self.indice_seleccionado + direccion) % len(self.botones)
        self.botones[self.indice_seleccionado].seleccionado = True
        self.juego.sound_engine.play("menu_select")

    def dibujar(self, pantalla):
        # Dibujar estado anterior (el juego)
        self.estado_prev.dibujar(pantalla)

        # Overlay semi-transparente
        overlay = pygame.Surface((self.juego.ancho, self.juego.alto))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        pantalla.blit(overlay, (0, 0))

        # Marco decorativo
        centro_x = self.juego.ancho // 2
        centro_y = self.juego.alto // 2
        marco = pygame.Rect(centro_x - 250, centro_y - 150, 500, 400)
        pygame.draw.rect(pantalla, (30, 30, 50), marco, border_radius=15)
        pygame.draw.rect(pantalla, (100, 120, 180), marco, 3, border_radius=15)

        # Título "PAUSA"
        titulo = self.juego.fonts.big.render("PAUSA", True, (255, 255, 255))
        titulo_rect = titulo.get_rect(center=(centro_x, centro_y - 100))

        sombra = self.juego.fonts.big.render("PAUSA", True, (50, 50, 70))
        sombra_rect = sombra.get_rect(center=(centro_x + 3, centro_y - 97))
        pantalla.blit(sombra, sombra_rect)
        pantalla.blit(titulo, titulo_rect)

        # Dibujar botones
        for boton in self.botones:
            boton.dibujar(pantalla)

        # Instrucciones (cambian según el modo de entrada)
        current_mode = self.juego.actions.get("current_mode", "keyboard_mouse")
        if current_mode == "controller":
            info_text = "B: Atrás | A: Seleccionar"
        else:
            info_text = "ESC: Atrás | ENTER: Seleccionar"
        info = self.juego.fonts.small.render(info_text, False, (180, 180, 200))
        info_rect = info.get_rect(center=(centro_x, self.juego.alto - 40))
        pantalla.blit(info, info_rect)

        self._dibujar_barra_mejoras(pantalla)

    def _crear_items_mejoras(self):
        items = []
        owned_ids = ()
        if hasattr(self.juego, "mejoras"):
            owned_ids = self.juego.mejoras.owned_ids()

        pad_x = 16
        pad_y = 46
        gap = 10
        cols = 3

        for i, mejora_id in enumerate(owned_ids):
            mejora = obtener_mejora(mejora_id)
            if not mejora:
                continue

            image = None
            asset_path = mejora.get("asset_path")
            if asset_path:
                try:
                    image = pygame.image.load(asset_path).convert_alpha()
                    image = pygame.transform.scale(image, (self.upgrade_icon_size, self.upgrade_icon_size))
                except Exception:
                    image = None

            col = i % cols
            row = i // cols
            x = self.sidebar_rect.x + pad_x + col * (self.upgrade_icon_size + gap)
            y = self.sidebar_rect.y + pad_y + row * (self.upgrade_icon_size + gap)
            rect = pygame.Rect(x, y, self.upgrade_icon_size, self.upgrade_icon_size)

            items.append({
                "id": mejora_id,
                "mejora": mejora,
                "image": image,
                "rect": rect,
            })

        return items

    def _dibujar_barra_mejoras(self, pantalla):
        pygame.draw.rect(pantalla, (24, 24, 40), self.sidebar_rect, border_radius=12)
        pygame.draw.rect(pantalla, (90, 110, 160), self.sidebar_rect, 2, border_radius=12)

        titulo = self.juego.fonts.medium.render("Mejoras", False, (255, 255, 255))
        pantalla.blit(titulo, (self.sidebar_rect.x + 14, self.sidebar_rect.y + 10))

        if not self.upgrade_items:
            txt = self.juego.fonts.small.render("Ninguna", False, (190, 190, 210))
            pantalla.blit(txt, (self.sidebar_rect.x + 14, self.sidebar_rect.y + 50))
            return

        for i, item in enumerate(self.upgrade_items):
            rect = item["rect"]
            is_hover = (i == self.hover_mejora_index)
            fill = (65, 85, 130) if is_hover else (42, 42, 60)
            border = (255, 255, 255) if is_hover else (130, 140, 180)
            pygame.draw.rect(pantalla, fill, rect, border_radius=8)
            pygame.draw.rect(pantalla, border, rect, 2, border_radius=8)

            if item["image"] is not None:
                img_rect = item["image"].get_rect(center=rect.center)
                pantalla.blit(item["image"], img_rect)
            else:
                fallback = self.juego.fonts.small.render("?", False, (255, 255, 255))
                pantalla.blit(fallback, fallback.get_rect(center=rect.center))

        if self.hover_mejora_index is not None:
            self._dibujar_tooltip_mejora(pantalla, self.upgrade_items[self.hover_mejora_index])

    def _dibujar_tooltip_mejora(self, pantalla, item):
        mejora = item.get("mejora", {})
        nombre = mejora.get("nombre", item.get("id", "Mejora"))
        descripcion = mejora.get("descripcion", "")

        lineas = self._wrap_text(descripcion, self.juego.fonts.small, 250)
        width = 280
        height = 46 + (len(lineas) * 18)

        x = self.pos_mouse_escalado[0] + 16
        y = self.pos_mouse_escalado[1] + 12
        if x + width > self.juego.ancho - 8:
            x = self.pos_mouse_escalado[0] - width - 16
        if y + height > self.juego.alto - 8:
            y = self.pos_mouse_escalado[1] - height - 12

        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(pantalla, (10, 10, 18), rect, border_radius=10)
        pygame.draw.rect(pantalla, (180, 200, 255), rect, 2, border_radius=10)

        name_surf = self.juego.fonts.medium.render(nombre, False, (255, 255, 255))
        pantalla.blit(name_surf, (rect.x + 12, rect.y + 8))

        text_y = rect.y + 34
        for line in lineas:
            line_surf = self.juego.fonts.small.render(line, False, (220, 220, 230))
            pantalla.blit(line_surf, (rect.x + 12, text_y))
            text_y += 18

    def _wrap_text(self, text, font, max_width):
        words = str(text).split(" ")
        lines = []
        line = ""
        for word in words:
            candidate = (line + " " + word).strip()
            if line and font.render(candidate, False, (255, 255, 255)).get_width() > max_width:
                lines.append(line)
                line = word
            else:
                line = candidate
        if line:
            lines.append(line)
        return lines