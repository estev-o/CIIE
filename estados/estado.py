class Estado():
    def __init__(self, juego):
        self.juego = juego
        self.estado_prev= None

    def actualizar(self, dt, acciones):
        pass

    def dibujar(self, pantalla):
        pass

    def entrar_estado(self):
        if len(self.juego.state_stack) > 1:
            self.estado_prev = self.juego.state_stack[-1]
        self.juego.state_stack.append(self)

    def salir_estado(self):
        self.juego.state_stack.pop()
