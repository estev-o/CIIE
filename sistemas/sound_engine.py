import pygame
from config.configuracion import Configuracion

class SoundEngine:
    def __init__(self, configuracion: Configuracion):
        pygame.mixer.init()
        self.config = configuracion
        self.music_volume = (self.config.get("volumen_musica", 70) / 100) ** 2
        self.sfx_volume = (self.config.get("volumen_efectos", 50) / 100) ** 2
        self.current_music = None

        self.channels = {
            "attack":      pygame.mixer.Channel(0),
            "enemy_death": pygame.mixer.Channel(1),
            "movement":    pygame.mixer.Channel(2),
            "world":       pygame.mixer.Channel(3),
        }

        self.sfx_channel = {
            "attack":       "attack",
            "dead":         "enemy_death",
            "movement":     "movement",
            "door":         "world",
        }

        self.music = {
            "menu": "assets/sounds/Menu theme.mp3",
            "main": "assets/sounds/Main theme.mp3",
            "dead": "assets/sounds/Dead theme.mp3",
        }

        self.sfx = {
            "movement":    pygame.mixer.Sound("assets/sounds/movement.mp3"),
            "door":        pygame.mixer.Sound("assets/sounds/door.wav"),
            "menu_select": pygame.mixer.Sound("assets/sounds/menu_select.mp3"),
            "menu_confirm":pygame.mixer.Sound("assets/sounds/menu_accept.mp3"),
            "dead":        pygame.mixer.Sound("assets/sounds/deadsfx.wav"),
            "attack":      pygame.mixer.Sound("assets/sounds/attack.wav"),
            "collect":     pygame.mixer.Sound("assets/sounds/collect.mp3"),
            "damage":      pygame.mixer.Sound("assets/sounds/damage.wav"),
        }

        for sound in self.sfx.values():
            sound.set_volume(self.sfx_volume)

    def play(self, name):
        if name not in self.sfx:
            return
        channel_name = self.sfx_channel.get(name)
        if channel_name:
            channel = self.channels[channel_name]
            if not channel.get_busy():
                channel.play(self.sfx[name])
        else:
            self.sfx[name].play()

    def play_music(self, name, fade_ms=500):
        if name in self.music:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(self.music[name])
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1, fade_ms=fade_ms)

    def play_music_if_changed(self, name, fade_ms=500):
        if name == self.current_music:
            return
        self.current_music = name
        self.play_music(name, fade_ms)

    def set_sfx_volume(self, v):
        self.sfx_volume = (v / 100) ** 2
        self.config.set("volumen_efectos", v)
        for sound in self.sfx.values():
            sound.set_volume(self.sfx_volume)

    def set_music_volume(self, v):
        self.music_volume = (v / 100) ** 2
        self.config.set("volumen_musica", v)
        pygame.mixer.music.set_volume(self.music_volume)