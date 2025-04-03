# utils.py
import pygame
import numpy as np
from constants import *


def draw_text(screen, text, color, x, y):
    text_surface = FONT.render(text, True, color)
    screen.blit(text_surface, (x, y))


def generate_sound(frequency, duration):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)
    sound_array = np.c_[wave, wave].astype(np.float32)
    sound = pygame.sndarray.make_sound((sound_array * 32767).astype(np.int16))
    return sound

def draw_multiline_text(screen, text, x, y, color=BLACK, line_height=30, max_width=700):
    font = pygame.font.Font(None, 28)
    words = text.split(" ")
    lines = []
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        if font.size(test_line)[0] < max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)

    for i, line in enumerate(lines):
        text_surface = font.render(line, True, color)
        screen.blit(text_surface, (x, y + i * line_height))
