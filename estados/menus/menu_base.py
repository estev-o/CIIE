import pygame
from estados.estado import Estado

class Menu(Estado):
    """Clase base para menús con lista de botones navegables."""

    def __init__(self, juego):
        Estado.__init__(self, juego)

        # Cargar sprite cursor personalizado
        imagen_original = pygame.image.load("assets/UI/cursor/cursor.png").convert_alpha()
        self.cursor_img = pygame.transform.scale(imagen_original, (30, 30))

        # Lista de botones del menú (se define en cada subclase)
        self.botones = []

        #Indice de botón seleccionado
        self.indice_seleccionado = 0

        # Control  navegación con cooldown
        self.cooldown_nav = 0
        self.delay_nav = 0.15

        # Estado previo del ratón para detectar clicks
        self.mouse_pressed_prev = pygame.mouse.get_pressed()[0]
        self._last_mouse_pos = None

    def actualizar(self, dt, acciones):
        # Reducir cooldown de navegación
        if self.cooldown_nav > 0:
            self.cooldown_nav -= dt

        #Navegación circular teclado/mando
        if self.cooldown_nav <= 0:
            if acciones.get("arrowUp"):
                self.cambiar_seleccion(-1)
                self.cooldown_nav = self.delay_nav
            elif acciones.get("arrowDown"):
                self.cambiar_seleccion(1)
                self.cooldown_nav = self.delay_nav
            elif acciones.get("back"):
                self.on_back()

        #Activar opciones botones
        if acciones.get("enter") or acciones.get("interact"):
            self.botones[self.indice_seleccionado].activar()
            self.juego.sound_engine.play("menu_accept")
            self.juego.reset_keys() # Evitar inputs duplicados
            return

        # Obtener el modo actual
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

        #Procesar hovering ratón sobre botones
        if current_mode == "keyboard_mouse" and mouse_moved:
            for i, boton in enumerate(self.botones):
                if boton.verificar_hover(pos_mouse_escalado):
                    if i != self.indice_seleccionado:
                        self.botones[self.indice_seleccionado].seleccionado = False
                        self.indice_seleccionado = i
                        self.botones[self.indice_seleccionado].seleccionado = True
                        self.juego.sound_engine.play("menu_select")

        #Procesar click ratón sobre botones
        if current_mode == "keyboard_mouse" and mouse_pressed and not self.mouse_pressed_prev:
            for i, boton in enumerate(self.botones):
                if boton.verificar_click(pos_mouse_escalado):
                    self.indice_seleccionado = i
                    boton.activar()
                    self.juego.sound_engine.play("menu_accept")
                    self.juego.reset_keys()
                    return

        self.mouse_pressed_prev = mouse_pressed

        #Actualizar animación botones
        for boton in self.botones:
            boton.actualizar(dt)

    # Cambiar selección circular botones con teclado o mando
    def cambiar_seleccion(self, direccion):
        self.botones[self.indice_seleccionado].seleccionado = False
        self.indice_seleccionado = (self.indice_seleccionado + direccion) % len(self.botones)
        self.botones[self.indice_seleccionado].seleccionado = True
        self.juego.sound_engine.play("menu_select")

    # Acción al pulsar back/ESC
    def on_back(self):
        self.juego.running = False

    def dibujar(self, pantalla):
        pass