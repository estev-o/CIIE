import pygame
from config.configuracion import Configuracion

class SoundEngine:
    def __init__(self, configuracion: Configuracion):
        pygame.mixer.init()
        self.config = configuracion
        self.music_volume = (self.config.get("volumen_musica", 70) / 100) ** 2
        self.sfx_volume = (self.config.get("volumen_efectos", 50) / 100) ** 2
        self.current_music = None

        self.music = {
            "menu":   "assets/sounds/Menu theme.mp3",
            "main": "assets/sounds/Main theme.mp3",
            "dead": "assets/sounds/dead.mp3",
        }

        self.sfx = {
            "movement": pygame.mixer.Sound("assets/sounds/movement.mp3"),
            "door": pygame.mixer.Sound("assets/sounds/door.mp3"),
        }

        for sound in self.sfx.values():
            sound.set_volume(self.sfx_volume)

    def play(self, name):
        if name in self.sfx:
            self.sfx[name].play()

    def play_music(self, name, fade_ms=500):
        if name in self.music:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(self.music[name])
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1, fade_ms=fade_ms)

    def play_music_if_changed(self, name,fade_ms=500):
        if name == self.current_music:
            return
        self.current_music = name
        self.play_music(name,fade_ms)

    def set_sfx_volume(self, v):
        self.sfx_volume = (v / 100) ** 2
        self.config.set("volumen_efectos", v)
        for sound in self.sfx.values():
            sound.set_volume(self.sfx_volume)

    def set_music_volume(self, v):
        self.music_volume = (v / 100) ** 2
        self.config.set("volumen_musica", v)
        pygame.mixer.music.set_volume(self.music_volume)