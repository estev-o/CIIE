import json
import os

class Configuracion:
    ARCHIVO_CONFIG = "config.json"

    CONFIG_DEFAULT = {
        "volumen_musica": 70,
        "volumen_efectos": 50,
        "pantalla_completa": False
    }

    def __init__(self):
        self.config = self.cargar()

    def cargar(self):
        if os.path.exists(self.ARCHIVO_CONFIG):
            try:
                with open(self.ARCHIVO_CONFIG, 'r', encoding='utf-8') as f:
                    config_cargada = json.load(f)
                    # Mezclar con default para agregar nuevas opciones
                    config_final = self.CONFIG_DEFAULT.copy()
                    config_final.update(config_cargada)
                    return config_final
            except Exception as e:
                print(f"Error al cargar config: {e}")
                return self.CONFIG_DEFAULT.copy()
        else:
            return self.CONFIG_DEFAULT.copy()

    def guardar(self):
        try:
            with open(self.ARCHIVO_CONFIG, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al guardar config: {e}")
            return False

    def get(self, clave, default=None):
        return self.config.get(clave, default)

    def set(self, clave, valor):
        self.config[clave] = valor
        self.guardar()

    def reset(self):
        self.config = self.CONFIG_DEFAULT.copy()
        self.guardar()
