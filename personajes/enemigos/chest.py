import pygame

from personajes.enemigos.enemy import Enemy


class Chest(Enemy):
    def __init__(self, *args, rarity=1, drop_pool_by_rarity=None, **kwargs):
        self.rarity = int(rarity)
        if drop_pool_by_rarity:
            table = drop_pool_by_rarity.get(self.rarity)
            if table is None:
                table = drop_pool_by_rarity.get(str(self.rarity))
            if table is not None:
                kwargs["drop_table"] = table
        super().__init__(*args, **kwargs)
        self.locked = True
        self.opening = False
        self.opened = False
        self._drop_done = False
        self._open_frame = 0
        self._open_timer = 0.0

    def load_sprites(self):
        sheet = pygame.image.load(self._asset_file).convert_alpha()
        cols = sheet.get_width() // self.frame_w
        rows = sheet.get_height() // self.frame_h

        col = self.rarity - 1  # rareza 1..7 -> columna 0..6
        col = max(0, min(col, cols - 1))

        self._open_frames = []
        for row in range(rows):
            rect = pygame.Rect(col * self.frame_w, row * self.frame_h, self.frame_w, self.frame_h)
            frame = sheet.subsurface(rect).copy()
            if self.scale != 1:
                frame = pygame.transform.scale(frame, (int(self.frame_w * self.scale), int(self.frame_h * self.scale)))
            self._open_frames.append(frame)
        self._down_sprites = self._up_sprites = self._left_sprites = self._right_sprites = self._open_frames

    def apply_damage(self, damage_amount):
        # Chests are invincible
        pass

    def unlock(self):
        self.locked = False

    def interact(self):
        if self.locked or self.opened or self.opening:
            return
        self.die()

    def die(self):
        if self.opened or self.opening:
            return
        self.opening = True
        self._open_frame = 0
        self._open_timer = 0.0
        self.image = self._open_frames[0]

    def ai_behavior(self, player, dt, solid_tiles):
        if not self.opening:
            return
        self._open_timer += dt
        frame_time = 1.0 / max(self.anim_fps, 1)
        while self._open_timer >= frame_time and self._open_frame < len(self._open_frames) - 1:
            self._open_timer -= frame_time
            self._open_frame += 1
            self.image = self._open_frames[self._open_frame]
        if self._open_frame >= len(self._open_frames) - 1:
            self.opening = False
            self.opened = True
            if not self._drop_done:
                self.drop()
                self._drop_done = True
