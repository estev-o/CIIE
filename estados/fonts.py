import pygame

"""Clase para centralizar las fuentes y sus tamaños"""

class Fuentes:
    def __init__(self):
        self.xs = pygame.font.Font("assets/fonts/Snowbell-Wp4g9.ttf", 9)
        self.dialog= pygame.font.Font("assets/fonts/Snowbell-Wp4g9.ttf", 13)
        self.small = pygame.font.Font("assets/fonts/Snowbell-Wp4g9.ttf", 16)
        self.medium = pygame.font.Font("assets/fonts/Snowbell-Wp4g9.ttf", 24)
        self.big = pygame.font.Font("assets/fonts/Snowbell-Wp4g9.ttf", 64)
        self.level_title = pygame.font.Font("assets/fonts/Snowbell-Wp4g9.ttf", 42)
