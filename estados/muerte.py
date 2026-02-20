import pygame

from estados.estado import Estado


class Muerte(Estado):
    def __init__(self, juego):
        super().__init__(juego)
        button_w = 340
        button_h = 56
        center_x = self.juego.ancho // 2
        first_y = (self.juego.alto // 2) + 30
        self.menu_rect = pygame.Rect(center_x - (button_w // 2), first_y, button_w, button_h)
        self.hub_rect = pygame.Rect(center_x - (button_w // 2), first_y + button_h + 18, button_w, button_h)
        self._click_was_down = False

    def actualizar(self, dt, acciones):
        click_down = bool(acciones.get("attack1"))
        mouse_pos = acciones.get("mouse_pos", (0, 0))

        if click_down and not self._click_was_down:
            if self.menu_rect.collidepoint(mouse_pos):
                self.juego.start_new_run(start_state="menu")
                return
            if self.hub_rect.collidepoint(mouse_pos):
                self.juego.start_new_run(start_state="hub")
                return

        self._click_was_down = click_down

    def dibujar(self, pantalla):
        pantalla.fill((24, 6, 6))

        title_font = pygame.font.Font(None, 88)
        body_font = pygame.font.Font(None, 34)
        button_font = pygame.font.Font(None, 42)

        title = title_font.render("HAS MUERTO", True, (255, 240, 240))
        title_rect = title.get_rect(center=(self.juego.ancho // 2, (self.juego.alto // 2) - 90))
        pantalla.blit(title, title_rect)

        info = body_font.render(f"ADN acumulado: {self.juego.adn}", True, (220, 220, 220))
        info_rect = info.get_rect(center=(self.juego.ancho // 2, (self.juego.alto // 2) - 30))
        pantalla.blit(info, info_rect)

        mouse_pos = self.juego.actions.get("mouse_pos", (-1, -1))
        menu_hover = self.menu_rect.collidepoint(mouse_pos)
        hub_hover = self.hub_rect.collidepoint(mouse_pos)

        pygame.draw.rect(pantalla, (210, 210, 210) if menu_hover else (175, 175, 175), self.menu_rect, border_radius=10)
        pygame.draw.rect(pantalla, (210, 210, 210) if hub_hover else (175, 175, 175), self.hub_rect, border_radius=10)

        menu_text = button_font.render("Volver al menu", True, (20, 20, 20))
        hub_text = button_font.render("Ir al hub", True, (20, 20, 20))
        pantalla.blit(menu_text, menu_text.get_rect(center=self.menu_rect.center))
        pantalla.blit(hub_text, hub_text.get_rect(center=self.hub_rect.center))
