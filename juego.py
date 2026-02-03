# Example file showing a circle moving on screen
import pygame

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()
running = True
dt = 0

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
TAMANO_JUGADOR = 40
VELOCIDAD = 300
ATAQUE_RADIO = 25
# Direccion en la que el jugador "mira" (por defecto hacia la derecha)
mirando_dir = pygame.Vector2(1, 0)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("purple")

    pygame.draw.circle(screen, "red", player_pos, TAMANO_JUGADOR)

    keys = pygame.key.get_pressed()
    move_dir = pygame.Vector2(0, 0)
    if keys[pygame.K_w]:
        move_dir.y -= 1
    if keys[pygame.K_s]:
        move_dir.y += 1
    if keys[pygame.K_a]:
        move_dir.x -= 1
    if keys[pygame.K_d]:
        move_dir.x += 1

    if move_dir.length_squared() > 0:
        move_dir = move_dir.normalize()
        player_pos += move_dir * VELOCIDAD * dt
        mirando_dir = move_dir

    # Que el jugador no se salga de la pantalla
    player_pos.x = max(TAMANO_JUGADOR, min(screen.get_width() - TAMANO_JUGADOR, player_pos.x))
    player_pos.y = max(TAMANO_JUGADOR, min(screen.get_height() - TAMANO_JUGADOR, player_pos.y))

    #Al pulsar espacio, el jugador ataca (ahora se muestra el hitbox solo)
    if keys[pygame.K_SPACE]:
        # Hitbox del ataque hacia la direccion en la que mira
        ataque_pos = player_pos + mirando_dir * (TAMANO_JUGADOR + ATAQUE_RADIO)
        pygame.draw.circle(screen, "yellow", ataque_pos, ATAQUE_RADIO, 5)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()