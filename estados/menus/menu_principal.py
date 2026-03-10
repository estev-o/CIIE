from estados.estado import Estado
from estados.menus.componentes import Boton
import pygame
from estados.menus.menu_configuracion import MenuConfiguracion

class MenuPrincipal(Estado):
    """Estado que implementa el menú principal del juego."""
    def __init__(self, juego):
        Estado.__init__(self, juego)

        #Cargar sprite cursor personalizado
        imagen_original = pygame.image.load("assets/UI/cursor/cursor.png").convert_alpha()
        self.cursor_img = pygame.transform.scale(imagen_original, (30, 30))

        # Iniciar música del menú si no está ya reproduciéndose
        juego.sound_engine.play_music_if_changed("menu",3000)

        #Obtener gestor de fuentes del juego
        font = self.juego.fonts

        # Crear botones usando componentes.py
        centro_x = juego.ancho // 2
        self.botones = [
            Boton(centro_x - 150, 200, 300, 60, "Jugar", font.medium,
                  lambda: self.juego.fade_to(lambda: self.juego.start_new_run("hub"))),
            Boton(centro_x - 150, 280, 300, 60, "Configuración", font.medium,
                  lambda: MenuConfiguracion(self.juego).entrar_estado()),
            Boton(centro_x - 150, 360, 300, 60, "Salir", font.medium,
                  lambda: setattr(self.juego, "running", False))
        ]

        #Indice de botón seleccionado
        self.indice_seleccionado = 0
        self.botones[self.indice_seleccionado].seleccionado = True

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
                self.juego.running = False

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


    def dibujar(self, pantalla):
        # Fondo degradado
        for y in range(pantalla.get_height()):
            ratio = y / pantalla.get_height()
            color = (
                int(15 + ratio * 25),
                int(15 + ratio * 35),
                int(40 + ratio * 60)
            )
            pygame.draw.line(pantalla, color, (0, y), (pantalla.get_width(), y))

        # ---- TITULO ----
        titulo = self.juego.fonts.big.render("BINDING OF BLUB", False, (255, 255, 255))
        titulo_rect = titulo.get_rect(center=(self.juego.ancho // 2, 100))

        sombra = self.juego.fonts.big.render("BINDING OF BLUB", False, (50, 50, 80))
        sombra_rect = sombra.get_rect(center=(self.juego.ancho // 2 + 4, 104))
        pantalla.blit(sombra, sombra_rect)
        pantalla.blit(titulo, titulo_rect)

        for boton in self.botones:
            boton.dibujar(pantalla)

        # ---- INFO ----
        current_mode = self.juego.actions.get("current_mode", "keyboard_mouse")
        if current_mode == "controller":
            info_text = "A: Seleccionar  |  B: Salir"
        else:
            info_text = "ENTER: Seleccionar  |  ESC: Salir"
        info = self.juego.fonts.small.render(
            info_text,
            False, (150, 150, 180)
        )
        info_rect = info.get_rect(center=(self.juego.ancho // 2, self.juego.alto - 25))
        pantalla.blit(info, info_rect)
