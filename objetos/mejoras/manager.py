from objetos.mejoras.catalogo import existe_mejora


class MejorasManager:
    CONFIG_KEY = "mejoras_persistentes"

    def __init__(self, configuracion):
        self.configuracion = configuracion
        self._mejoras = self._normalizar(configuracion.get(self.CONFIG_KEY, []))
        if self._mejoras != configuracion.get(self.CONFIG_KEY, []):
            self._guardar()

    def _normalizar(self, mejoras):
        if not isinstance(mejoras, list):
            return []

        resultado = []
        vistas = set()
        for mejora_id in mejoras:
            if not isinstance(mejora_id, str):
                continue
            if mejora_id in vistas:
                continue
            vistas.add(mejora_id)
            resultado.append(mejora_id)
        return resultado

    def _guardar(self):
        self.configuracion.set(self.CONFIG_KEY, list(self._mejoras))

    def owned_ids(self):
        return tuple(self._mejoras)

    def has(self, mejora_id):
        return mejora_id in self._mejoras

    def unlock(self, mejora_id):
        if not existe_mejora(mejora_id):
            raise ValueError(f"Mejora no registrada: {mejora_id}")
        if self.has(mejora_id):
            return False
        self._mejoras.append(mejora_id)
        self._guardar()
        return True
