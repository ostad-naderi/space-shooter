# -*- coding: utf-8 -*-
import os
import sys

# ---- MUST be before pygame import ----
os.environ['SDL_AUDIODRIVER'] = 'dummy'  # غیرفعال کردن صدا
os.environ['SDL_VIDEODRIVER'] = 'android'
os.environ['SDL_HINT_ORIENTATIONS'] = 'Portrait'

# ---- Log file ----
LOG_FILE = '/storage/emulated/0/Download/game_log.txt'
try:
    with open(LOG_FILE, 'w') as f:
        f.write("start\n")
except Exception:
    LOG_FILE = None

def log(msg):
    try:
        if LOG_FILE:
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(str(msg) + '\n')
    except Exception:
        pass

log("=== GAME START ===")
log("Python: " + sys.version)

import pygame
log("pygame imported, version: " + str(pygame.version.ver))

# ---- Init ONLY what we need (NO pygame.init!) ----
pygame.display.init()
log("display.init OK")

pygame.font.init()
log("font.init OK")

# Try to set display mode
try:
    screen = pygame.display.set_mode((600, 900))
    log("set_mode OK: " + str(screen.get_size()))
except Exception as e:
    log("set_mode FAILED: " + str(e))
    sys.exit(1)

pygame.display.set_caption("Test")
log("caption OK")

# Font
try:
    font = pygame.font.Font(None, 40)
    log("font OK")
except Exception as e:
    log("font FAILED: " + str(e))
    font = None

text = font.render("TEST OK", True, (255, 255, 255)) if font else None
log("render OK")

log("=== entering main loop ===")
clock = pygame.time.Clock()
frame = 0
color = [255, 0, 0]

while True:
    frame += 1
    if frame % 60 == 0:
        log("frame " + str(frame))

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            sys.exit(0)
        if e.type == pygame.FINGERDOWN or e.type == pygame.MOUSEBUTTONDOWN:
            color = [0, 255, 0] if color[0] == 255 else [255, 0, 0]

    screen.fill(color)
    if text:
        screen.blit(text, (150, 400))
    pygame.display.flip()
    clock.tick(30)
