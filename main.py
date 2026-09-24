# -*- coding: utf-8 -*-
import os
import sys
import traceback

# ---- Write log to Downloads (user-accessible) ----
LOG_PATHS = [
    '/storage/emulated/0/Download/game_log.txt',
    '/sdcard/Download/game_log.txt',
    '/storage/emulated/0/game_log.txt',
    '/sdcard/game_log.txt',
    '/tmp/game_log.txt',
]

LOG_FILE = None
for p in LOG_PATHS:
    try:
        with open(p, 'w') as f:
            f.write("start\n")
        LOG_FILE = p
        break
    except Exception:
        continue

def log(msg):
    try:
        if LOG_FILE:
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(str(msg) + '\n')
    except Exception:
        pass

log("=== GAME START ===")
log("Python: " + sys.version)
log("Log file: " + str(LOG_FILE))

# ---- Import pygame ----
try:
    import pygame
    log("pygame OK version: " + str(pygame.version.ver))
except Exception as e:
    log("pygame IMPORT FAILED: " + str(e))
    log(traceback.format_exc())
    sys.exit(1)

try:
    pygame.init()
    log("pygame.init OK")
except Exception as e:
    log("pygame.init FAILED: " + str(e))
    log(traceback.format_exc())

try:
    pygame.font.init()
    log("font.init OK")
except Exception as e:
    log("font.init FAILED: " + str(e))

try:
    screen = pygame.display.set_mode((600, 900))
    log("set_mode OK: " + str(screen.get_size()))
except Exception as e:
    log("set_mode FAILED: " + str(e))
    log(traceback.format_exc())
    sys.exit(1)

try:
    pygame.display.set_caption("Test")
    log("caption OK")
except Exception as e:
    log("caption FAILED: " + str(e))

try:
    font = pygame.font.SysFont("arial", 40)
    log("SysFont OK")
except Exception as e:
    log("SysFont FAILED: " + str(e))
    try:
        font = pygame.font.Font(None, 40)
        log("default font OK")
    except Exception as e2:
        log("default font FAILED too: " + str(e2))
        font = None

try:
    text = font.render("TEST OK", True, (255, 255, 255)) if font else None
    log("render OK")
except Exception as e:
    log("render FAILED: " + str(e))

log("=== entering main loop ===")

clock = pygame.time.Clock()
frame = 0
try:
    while True:
        frame += 1
        if frame % 60 == 0:
            log("frame " + str(frame))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                log("QUIT event")
                sys.exit(0)

        screen.fill((0, 0, 100))
        if text:
            screen.blit(text, (100, 400))
        pygame.display.flip()
        clock.tick(30)

except Exception as e:
    log("MAIN LOOP CRASH: " + str(e))
    log(traceback.format_exc())
