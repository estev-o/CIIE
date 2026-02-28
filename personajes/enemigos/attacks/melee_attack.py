import math

from personajes.enemigos.attacks.attack_behavior import AttackBehavior


class MeleeAttack(AttackBehavior):
    def __init__(self, enemy):
        super().__init__(enemy)
        self.is_lunging = False
        self.lunge_dir_x = 0
        self.lunge_dir_y = 0
        self.distance_traveled = 0
        self.target_distance = 0

    def execute(self, player, dt, solid_tiles=None):
        # Si no está en medio de un ataque, comprobamos cooldown y rango
        if not self.is_lunging:

            # Distancia al jugador
            dx = player.rect.centerx - self.enemy.rect.centerx
            dy = player.rect.centery - self.enemy.rect.centery
            dist = math.hypot(dx, dy)

            self.is_lunging = True
            self.target_distance = dist+30  # Posición cuando empieza el salto más un poco de margen de error
            self.distance_traveled = 0

            # Calculamos la dirección para el abalanzamiento
            if dist > 0:
                self.lunge_dir_x = dx / dist
                self.lunge_dir_y = dy / dist
            else:
                self.lunge_dir_x, self.lunge_dir_y = 0, 0


        # Si ya está abalanzándose
        else:
            move_x = self.lunge_dir_x * self.enemy.attack_speed * dt
            move_y = self.lunge_dir_y * self.enemy.attack_speed * dt

            self.enemy.pos_x += move_x
            self.enemy.pos_y += move_y

            # Manejamos las colisiones para no atravesarlas
            if solid_tiles is not None:
                self.enemy.pos_x -= move_x
                self.enemy.pos_y -= move_y
                self.enemy.move_and_collide(move_x, move_y, solid_tiles)

            self.enemy.rect.topleft = (int(self.enemy.pos_x), int(self.enemy.pos_y))

            # Acumulamos la distancia que ya ha recorrido en este ataque
            self.distance_traveled += math.hypot(move_x, move_y)

            # Comprobamos si se ha recorrido el salto
            if self.distance_traveled >= self.target_distance:
                self._end_lunge()


    def _end_lunge(self):
        self.is_lunging = False
        self.enemy.cooldown_timer = self.enemy.attack_cooldown



