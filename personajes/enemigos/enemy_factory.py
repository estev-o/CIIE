import json
import os

from personajes.enemigos.enemy import Enemy


class EnemyFactory:
    def __init__(self, game, filepath):
        self.game = game
        self.enemy_data = {}
        self.load_data(filepath)

    def load_data(self, filepath: object) -> None:
        """Carga el JSON en memoria"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"No se encontró el archivo: {filepath}")

        with open(filepath, 'r') as file:
            self.enemy_data = json.load(file)
            print(f"Enemigos cargados: {list(self.enemy_data.keys())}")

    def create_enemy(self, enemy_name, x, y):
        """
        Crea una instancia de Enemy basada en el tipo (string)
        y la posición dada.
        """
        if enemy_name not in self.enemy_data:
            print(f"ERROR: El enemigo '{enemy_name}' no existe en el JSON.")
            return None

        config = self.enemy_data[enemy_name]

        # Creamos el enemigo desempaquetando la configuración (**config)
        new_enemy = Enemy(
            game=self.game,
            x=x,
            y=y,
            **config
        )
        new_enemy.load_sprites()

        return new_enemy