from personajes.character import Character


class Player(Character):
    def __init__(self, game):
        super().__init__(
            game=game,
            max_live=100,
            x=100,
            y=100,
            width=64,
            height=64,
            speed=250,
            scale=2,
            anim_fps=10,
            asset_file="assets/Blub/PNG/Slime1/Walk/Slime1_Walk_full.png",
        )
