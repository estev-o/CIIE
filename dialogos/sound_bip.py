import array
import pygame
import math

# Sonido que hace cada caracter
def generate_bip():
        duration = 0.02
        sample_rate = 44100
        volume = 0.3

        n_samples = int(sample_rate * duration)
        buf = array.array("h")
        amplitude = int(32767 * volume)

        for i in range(n_samples):
            t = i / sample_rate
            buf.append(int(math.sin(amplitude)*amplitude))

        return pygame.mixer.Sound(buffer=buf)

sound_bip = generate_bip()