from estados.estado import Estado
from estados.componentes import Boton
from objetos.mejoras.catalogo import obtener_mejora
import pygame


class Pausa(Estado):
    """Menú de pausa con opciones"""

    def __init__(self, juego):
        Estado.__init__(self, juego)

        font = self.juego.fonts

        #botones
        centro_x = juego.ancho // 2
        centro_y = juego.alto // 2

        self.botones = [
            Boton(centro_x - 150, centro_y - 30, 300, 55, "Continuar", font.medium),
            Boton(centro_x - 150, centro_y + 40, 300, 55, "Configuración", font.medium),
            Boton(centro_x - 150, centro_y + 110, 300, 55, "Menú Principal", font.medium)
        ]

        self.indice_seleccionado = 0
        self.botones[self.indice_seleccionado].seleccionado = True

        self.cooldown_nav = 0
        self.delay_nav = 0.15

        self.mouse_pressed_prev = False
        self.pos_mouse_escalado = (0, 0)
        self.hover_mejora_index = None

        self.sidebar_rect = pygame.Rect(self.juego.ancho - 250, centro_y - 150, 220, 400)
        self.upgrade_icon_size = 46
        self.upgrade_items = self._crear_items_mejoras()

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

    def actualizar(self, dt, acciones):
        # Actualizar cooldown
        if self.cooldown_nav > 0:
            self.cooldown_nav -= dt

        if acciones.get("back") or acciones.get("toggle_pause"):
            if acciones.get("back"):
                self.juego.actions["back"] = False
            if acciones.get("toggle_pause"):
                self.juego.actions["toggle_pause"] = False
            self.salir_estado()
            return

        # teclado / mando
        if self.cooldown_nav <= 0:
            if acciones.get("arrowUp"):
                self.cambiar_seleccion(-1)
                self.cooldown_nav = self.delay_nav
            elif acciones.get("arrowDown"):
                self.cambiar_seleccion(1)
                self.cooldown_nav = self.delay_nav

        if acciones.get("enter") or acciones.get("attack1"):
            self.activar_opcion()
            self.juego.reset_keys()

        # Mouse
        pos_mouse = pygame.mouse.get_pos()
        escala_x = self.juego.ancho / self.juego.screen.get_width()
        escala_y = self.juego.alto / self.juego.screen.get_height()
        pos_mouse_escalado = (int(pos_mouse[0] * escala_x), int(pos_mouse[1] * escala_y))
        self.pos_mouse_escalado = pos_mouse_escalado

        mouse_pressed = pygame.mouse.get_pressed()[0]

        for i, boton in enumerate(self.botones):
            if boton.verificar_hover(pos_mouse_escalado):
                if i != self.indice_seleccionado:
                    self.botones[self.indice_seleccionado].seleccionado = False
                    self.indice_seleccionado = i
                    self.botones[self.indice_seleccionado].seleccionado = True

        self.hover_mejora_index = None
        for i, item in enumerate(self.upgrade_items):
            if item["rect"].collidepoint(pos_mouse_escalado):
                self.hover_mejora_index = i
                break

        if mouse_pressed and not self.mouse_pressed_prev:
            for i, boton in enumerate(self.botones):
                if boton.verificar_click(pos_mouse_escalado):
                    self.indice_seleccionado = i
                    self.activar_opcion()
                    break

        self.mouse_pressed_prev = mouse_pressed

        for boton in self.botones:
            boton.actualizar(dt)

    def cambiar_seleccion(self, direccion):
        self.botones[self.indice_seleccionado].seleccionado = False
        self.indice_seleccionado = (self.indice_seleccionado + direccion) % len(self.botones)
        self.botones[self.indice_seleccionado].seleccionado = True

    def activar_opcion(self):
        if self.indice_seleccionado == 0:  # Continuar
            self.salir_estado()

        elif self.indice_seleccionado == 1:  # Configuración
            from estados.menu_configuracion import MenuConfiguracion
            MenuConfiguracion(self.juego).entrar_estado()

        elif self.indice_seleccionado == 2:  # Menú Principal
            while len(self.juego.state_stack) > 1:
                self.juego.state_stack.pop()

            from estados.menu_principal import MenuPrincipal
            MenuPrincipal(self.juego).entrar_estado()

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

        # Instrucciones
        info = self.juego.fonts.small.render(
            "ESC: Continuar | ENTER: Seleccionar",
            True, (180, 180, 200)
        )
        info_rect = info.get_rect(center=(centro_x, self.juego.alto - 40))
        pantalla.blit(info, info_rect)

        self._dibujar_barra_mejoras(pantalla)

    def _dibujar_barra_mejoras(self, pantalla):
        pygame.draw.rect(pantalla, (24, 24, 40), self.sidebar_rect, border_radius=12)
        pygame.draw.rect(pantalla, (90, 110, 160), self.sidebar_rect, 2, border_radius=12)

        titulo = self.juego.fonts.medium.render("Mejoras", True, (255, 255, 255))
        pantalla.blit(titulo, (self.sidebar_rect.x + 14, self.sidebar_rect.y + 10))

        if not self.upgrade_items:
            txt = self.juego.fonts.small.render("Ninguna", True, (190, 190, 210))
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
                fallback = self.juego.fonts.small.render("?", True, (255, 255, 255))
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

        name_surf = self.juego.fonts.medium.render(nombre, True, (255, 255, 255))
        pantalla.blit(name_surf, (rect.x + 12, rect.y + 8))

        text_y = rect.y + 34
        for line in lineas:
            line_surf = self.juego.fonts.small.render(line, True, (220, 220, 230))
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
