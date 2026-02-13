import json

from objetos.health_potion import HealthPotion


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
        return None
