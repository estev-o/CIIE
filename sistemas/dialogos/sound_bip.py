import array
import pygame
import math

# Sonido que hace cada caracter
def generate_bip(freq=450, volume=0.1, duration=0.018):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = array.array("h")
    amplitude = int(32767 * volume)

    for i in range(n_samples):
        t = i / sample_rate

        sample = math.sin(2 * math.pi * freq * t)

        fade_start = int(n_samples * 0.7)
        if i >= fade_start:
            factor = 1.0 - (i - fade_start) / (n_samples - fade_start)
            sample *= factor

        buf.append(int(sample * amplitude))

    return pygame.mixer.Sound(buffer=buf)

sound_bip = generate_bip()