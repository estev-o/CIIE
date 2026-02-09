import pygame
from personajes.constants import RED
from abc import abstractmethod, ABC

class Character(ABC):
    def __init__(
        self,
        game,
        x,
        y,
        width,
        height,
        scale,
        speed,
        anim_fps,
        max_live=None,
        asset_file=None,
    ):
        super().__init__()
        self.game = game
        self.pos_x = x
        self.pos_y = y
        self.speed = speed
        self.frame_w = width
        self.frame_h = height
        self.scale = scale
        self.anim_fps = anim_fps
        self._current_frame = 0
        self._anim_timer = 0.0
        self.facing = "down"
        self._asset_file = asset_file
        self.max_live = max_live
        self._actual_life = max_live

        if asset_file is not None:
            self.load_sprites()
            self._curr_anim_list = self._down_sprites
            self._curr_image = self._curr_anim_list[0]
        else:
            self._curr_image = pygame.Surface((self.frame_w, self.frame_h))
            self._curr_image.fill(RED)

    @property
    def remaining_life(self):
        return self._actual_life

    @property
    def remaining_life_percentage(self):
        return (self._actual_life / self.remaining_life) * 100

    def heal(self, heal_amount):
        if heal_amount > 0:
            self._actual_life = min(self._actual_life + heal_amount, self.max_live)

    def heal_percetage(self, heal_percentage):
        if 0 < heal_percentage <= 100:
            heal = self.max_live * heal_percentage / 100
            self._actual_life = min(self._actual_life + heal, self.max_live)

    @abstractmethod
    def die(self):
        pass

    def apply_damage(self, damage_amount):
        if damage_amount > 0:
            self._actual_life = max(self._actual_life - damage_amount, 0)

            if self.remaining_life <= 0:
                self.die()

    def apply_damage_percentage(self, damage_percentage):
        if 0 < damage_percentage <= 100:
            damage = self.max_live * damage_percentage / 100
            self._actual_life = min(self._actual_life - damage, 0)
            
            if self.remaining_life <= 0:
                self.die()

    def update(self, dt, acciones):
        '''
            Actualiza el estado del personaje
        '''
        pass

    def render(self, pantalla):
        pantalla.blit(self._curr_image, (int(self.pos_x), int(self.pos_y)))

    def animate(self, dt, moving: bool):
        if self.facing == "right":
            self._curr_anim_list = self._right_sprites
        elif self.facing == "left":
            self._curr_anim_list = self._left_sprites
        elif self.facing == "up":
            self._curr_anim_list = self._up_sprites
        else:
            self._curr_anim_list = self._down_sprites

        if not moving:
            self._current_frame = 0
            self._anim_timer = 0.0
            self._curr_image = self._curr_anim_list[0]
            return

        self._anim_timer += dt
        frame_time = 1.0 / max(self.anim_fps, 1)
        while self._anim_timer >= frame_time:
            self._anim_timer -= frame_time
            self._current_frame = (self._current_frame + 1) % len(self._curr_anim_list)

        self._curr_image = self._curr_anim_list[self._current_frame]

    @abstractmethod
    def load_sprites(self):
        '''
            Inicializa las variables:
                self._down_sprites
                self._up_sprites
                self._left_sprites
                self._right_sprites
        '''
        pass

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.pos_x),
            int(self.pos_y),
            self.frame_w * self.scale,
            self.frame_h * self.scale,
        )
