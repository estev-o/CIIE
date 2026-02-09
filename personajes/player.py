from personajes.character import Character
from personajes.constants import PLAYER_DEATH
import pygame
from personajes.ataques.azulejo import Azulejo
from personajes.ataques.attack_launcher import AttackLauncher

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

        self.attack_launcher1 = AttackLauncher(Azulejo)
    
    
    def die(self):
        pygame.event.post(PLAYER_DEATH)

    def attack(self):
        if self.attack_launcher1.is_ready:
            attack = self.attack_launcher1.get_attack(
                self.game, 
                self.pos_x+(self.frame_w/2),
                self.pos_y+(self.frame_h/2), 
                self.facing
                )
            self.game.state_stack[-1].attacks.append(attack)

    def update(self, dt, acciones,tiles):
        direction_x = acciones["right"] - acciones["left"]
        direction_y = acciones["down"] - acciones["up"]

        if direction_x > 0:
            self.facing = "right"
        elif direction_x < 0:
            self.facing = "left"
        elif direction_y > 0:
            self.facing = "down"
        elif direction_y < 0:
            self.facing = "up"

        if acciones["attack1"]:
            self.attack()

        dx = direction_x * self.speed * dt
        dy = direction_y * self.speed * dt

        if dx:
            self.pos_x += dx
            self.checkCollisionsx(tiles, dx)
        if dy:
            self.pos_y += dy
            self.checkCollisionsy(tiles, dy)

        if self._asset_file is not None:
            moving = bool(direction_x or direction_y)
            self.animate(dt, moving)

    def load_sprites(self):
        sheet = pygame.image.load(self._asset_file).convert_alpha()

        cols = sheet.get_width() // self.frame_w
        rows = sheet.get_height() // self.frame_h

        def slice_row(row_index: int):
            frames = []
            for col in range(cols):
                rect = pygame.Rect(
                    col * self.frame_w,
                    row_index * self.frame_h,
                    self.frame_w,
                    self.frame_h,
                )
                frame = sheet.subsurface(rect).copy()
                if self.scale != 1:
                    frame = pygame.transform.scale(
                        frame,
                        (self.frame_w * self.scale, self.frame_h * self.scale),
                    )
                frames.append(frame)
            return frames

        self._down_sprites = slice_row(0)
        self._up_sprites = slice_row(1) if rows >= 2 else list(self._down_sprites)
        self._left_sprites = (
            slice_row(2)
            if rows >= 3
            else [pygame.transform.flip(f, True, False) for f in self._down_sprites]
        )
        self._right_sprites = (
            slice_row(3)
            if rows >= 4
            else [pygame.transform.flip(f, True, False) for f in self._left_sprites]
        )

    def get_hits(self, tiles):
        hits = []
        for tile in tiles:
            if self.body_hitbox.colliderect(tile.hitbox):
                hits.append(tile)
        return hits
    
    def checkCollisionsx(self, tiles, dx: float):
        if dx == 0:
            return
        collisions = self.get_hits(tiles)
        for tile in collisions:
            if dx > 0:
                self.pos_x = tile.hitbox.left - self.hitbox.width - self.body_hitbox_offset_x
            elif dx < 0:
                self.pos_x = tile.hitbox.right - self.body_hitbox_offset_x

    def checkCollisionsy(self, tiles, dy: float):
        if dy == 0:
            return
        collisions = self.get_hits(tiles)
        for tile in collisions:
            if dy > 0:
                self.pos_y = tile.hitbox.top - self.hitbox.height - self.body_hitbox_offset_y
            elif dy < 0:
                self.pos_y = tile.hitbox.bottom - self.body_hitbox_offset_y