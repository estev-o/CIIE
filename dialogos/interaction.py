import pygame
import math
from dialogos.dialog import font

class Interaction:
    def __init__(
        self,
        sprite,
        text,
        interactuable,
        launch_action,
        distance=120,
        text_controller=None,
        game=None,
        availability_check=None,
    ):
        self.sprite = sprite                    # Sprite con el que interactua
        self.text = text                        # Texto que se muestre sobre el sprite
        self.text_controller = text_controller  # Texto alternativo para mando
        self.game = game                        # Referencia al juego para consultar modo
        self.distance = distance                # Distancia a la que se vuelve visible
        self.visible = False
        self.interactuable = interactuable      # Clase interactuable (Dialogo...)
        self.launch_action = launch_action      # Accion (actions de juego.py) que ejecuta la lanza la clase interactuable
        self.availability_check = availability_check

    def is_launchable(self, actions):
        return self.visible and self.launch_action in actions and actions[self.launch_action]

    def update(self, player, actions):
        if callable(self.availability_check) and not self.availability_check():
            self.visible = False
            return

        if not self.interactuable.is_active():
            dx = player.rect.centerx - self.sprite.rect.centerx
            dy = player.rect.centery - self.sprite.rect.centery
            self.visible = math.hypot(dx, dy) <= self.distance
            
            if self.is_launchable(actions):
                self.interactuable.interact()
                self.visible = False

    def _display_text(self):
        if self.text_controller and self.game:
            mode = self.game.actions.get("current_mode", "keyboard_mouse")
            if mode == "controller":
                return self.text_controller
        return self.text

    def draw(self, screen):
        if self.visible:
            render = font.render(self._display_text(), True, (255,255,255))
            rect = render.get_rect()
            rect.centerx = self.sprite.rect.centerx
            rect.bottom = self.sprite.rect.top - 5
            rect.inflate_ip(12,8)

            pygame.draw.rect(screen,(0,0,0),rect,border_radius=10)
            pygame.draw.rect(screen,(255,255,255),rect,2,border_radius=10)
            screen.blit(render, render.get_rect(center=rect.center))
    
    def is_active(self):
        return self.interactuable.is_active()
