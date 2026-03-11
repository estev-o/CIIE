import math
import pygame
from personajes.enemigos.attacks.attack_behavior import AttackBehavior


class RangedAttack(AttackBehavior):
    """
        Comportamiento de ataque para enemigos ranged
    """
    def __init__(self, enemy):
        super().__init__(enemy)

    def execute(self, player, dt, solid_tiles):
        """
        Método que ejecuta ataque para enemigos a distancia
        Dispara en dirección al jugador
        """
        dx = player.rect.centerx - self.enemy.rect.centerx
        dy = player.rect.centery - self.enemy.rect.centery
        dist = math.hypot(dx, dy)

        if dist == 0:
            dist = 0.1

        dir_x = dx / dist
        dir_y = dy / dist

        # Efectuar el disparo
        self.shoot(dir_x, dir_y)

        self.enemy.cooldown_timer = self.enemy.attack_cooldown

    def shoot(self, dir_x, dir_y):
        """
            Carga los disparos enemigos en el estado
        """
        projectile = EnemyProjectile(
            game=self.enemy.game,
            pos=self.enemy.rect.center,
            dir_x=dir_x,
            dir_y=dir_y,
            damage=self.enemy.damage,
            speed=self.enemy.attack_speed
        )

        # Lo añadimos al estado de juego
        self.enemy.game.actual_state.enemy_projectiles.add(projectile)


class EnemyProjectile(pygame.sprite.Sprite):
    """ Clase de Renderizado y Actualización de los disparos enemigos """
    def __init__(self, game, pos, dir_x, dir_y, damage, speed):
        super().__init__()
        self.game = game
        self.damage = damage
        self.speed = speed
        self.dir_x = dir_x
        self.dir_y = dir_y

        self.pos_x = float(pos[0])
        self.pos_y = float(pos[1])

        # Cargamos una imagen y la enrojecemos
        try:
            # Carga la imagen completamente nueva y original
            self.original_image = pygame.image.load("assets/personajes/ataques/azulejo.png").convert_alpha()
        except FileNotFoundError:
            # Fallback por si la ruta falla (para evitar que el juego se cierre)
            print("Error: No se encontró 'assets/ataques/azulejo.png'. Usando sprite por defecto.")
            self.original_image = pygame.Surface((15, 15), pygame.SRCALPHA)
            pygame.draw.circle(self.original_image, (255, 255, 255), (7, 7), 7)

        # Enrojecemos la imagen
        self.original_image.fill((255, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)

        self.image = self.original_image
        self.rect = self.image.get_rect(center=pos)

        self.angle = 0
        self.rotation_speed = 360

    def update(self, dt, solid_tiles=None):
        self.pos_x += self.dir_x * self.speed * dt
        self.pos_y += self.dir_y * self.speed * dt

        self.angle = (self.angle + self.rotation_speed * dt) % 360
        self.image = pygame.transform.rotate(self.original_image, self.angle)

        self.rect = self.image.get_rect(center=(round(self.pos_x), round(self.pos_y)))


        self.check_collisions(solid_tiles)
        #Si sale de la pantalla destruir (por si acaso)
        if not self.game.screen.get_rect().colliderect(self.rect):
            self.kill()

    def check_collisions(self, solid_tiles):
        # Comprueba colisión del disparo con el jugador o una superficie sólida
        player = self.game.actual_state.player
        if pygame.Rect.colliderect(self.rect, player.hitbox):
            # Aplica un daño al jugador
            player.apply_damage(self.damage)
            self.kill()
            return

        if solid_tiles:
            for tile in solid_tiles:
                if self.rect.colliderect(tile.hitbox):
                    self.kill()
                    return