import json

from objetos.health_potion import HealthPotion
from objetos.adn import ADN


class ObjectFactory:
    def __init__(self, filepath):
        with open(filepath, "r", encoding="utf-8") as file:
            self.object_data = json.load(file)

    def create_object(self, object_id, x, y):
        config = self.object_data.get(object_id)
        if config is None:
            return None

        object_type = config.get("type")
        if object_type == "health_potion":
            return HealthPotion(
                x=x,
                y=y,
                heal_amount=config.get("heal_amount", 25),
                sprite_path=config.get("sprite_path", "assets/objects/potion.png"),
            )
        if object_type == "adn":
            return ADN(
                x=x,
                y=y,
                amount=config.get("amount", 1),
                sprite_path=config.get("sprite_path", "assets/UI/ADN/ADN.png"),
            )
        return None
