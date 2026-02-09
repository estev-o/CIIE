from personajes.character import Character


class Player(Character):
    def __init__(self, game):
        super().__init__(
            game=game,
            max_live=100,
            # la posición la cambiamos porque el spawn cambia según el estado del nivel
            x=0,
            y=0,
            width=64,
            height=64,
            speed=200,
            scale=1.75,
            anim_fps=15,
            hitbox_offset_x=45,
            hitbox_offset_y=45,
            asset_file="assets/Blub/PNG/Slime1/Walk/Slime1_Walk_full.png",
        )
