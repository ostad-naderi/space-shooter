# -*- coding: utf-8 -*-
import sys
import os
import traceback

# ============ LOG SETUP (برای دیدن خطا) ============
LOG_FILE = None
try:
    LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'game_log.txt')
except Exception:
    try:
        LOG_FILE = '/sdcard/game_log.txt'
    except Exception:
        LOG_FILE = None

def log(msg):
    try:
        if LOG_FILE:
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(str(msg) + '\n')
    except Exception:
        pass
    print(msg)

log("=" * 40)
log("GAME START")

# ============ IMPORT PYGAME ============
try:
    import pygame
    log("pygame imported OK")
except Exception as e:
    log("pygame import FAILED: " + str(e))
    sys.exit(1)

import random

# ============ INIT ============
try:
    pygame.init()
    log("pygame.init OK")
except Exception as e:
    log("pygame.init FAILED: " + str(e))

try:
    pygame.font.init()
    log("font.init OK")
except Exception as e:
    log("font.init FAILED: " + str(e))


# ============ FONT LOADER (very safe) ============
def safe_font(size):
    """Try to load any font that works."""
    # 1) Bundled pygame default (safest)
    try:
        f = pygame.font.Font(None, size)
        log("font: pygame default OK for size " + str(size))
        return f
    except Exception as e:
        log("font default failed: " + str(e))

    # 2) Try file in same dir
    try:
        base = os.path.dirname(os.path.abspath(__file__))
        for name in ['Roboto-Bold.ttf', 'DejaVuSans.ttf', 'Vazir.ttf']:
            p = os.path.join(base, name)
            if os.path.exists(p):
                try:
                    f = pygame.font.Font(p, size)
                    log("font loaded: " + name)
                    return f
                except Exception as e:
                    log("font file failed " + name + ": " + str(e))
    except Exception:
        pass

    # 3) SysFont as last resort
    try:
        f = pygame.font.SysFont("arial", size)
        log("SysFont OK")
        return f
    except Exception as e:
        log("SysFont failed: " + str(e))

    return None


# ============ DISPLAY ============
WIDTH, HEIGHT = 720, 1280

try:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    log("set_mode OK: " + str(screen.get_size()))
    WIDTH, HEIGHT = screen.get_size()
except Exception as e:
    log("set_mode FAILED: " + str(e))
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        WIDTH, HEIGHT = screen.get_size()
        log("set_mode fallback OK")
    except Exception as e2:
        log("set_mode fallback FAILED: " + str(e2))
        sys.exit(1)

try:
    pygame.display.set_caption("Space Shooter")
except Exception:
    pass

clock = pygame.time.Clock()

SCALE = max(1.0, HEIGHT / 900.0)
def s(v):
    return max(1, int(v * SCALE))


# ============ FONTS ============
F_SMALL = safe_font(s(20))
F_MID   = safe_font(s(26))
F_EMPH  = safe_font(s(42))
F_TITLE = safe_font(s(60))
F_HUD   = safe_font(s(18))

if F_MID is None:
    log("FATAL: no font available")
    sys.exit(1)


# ============ COLORS ============
BLACK = (5, 8, 25)
DARK_BLUE = (10, 15, 45)
WHITE = (255, 255, 255)
BLUE = (40, 180, 255)
LIGHT_BLUE = (120, 220, 255)
RED = (255, 60, 70)
YELLOW = (255, 220, 40)
NEON = (255, 255, 0)
ORANGE = (255, 130, 30)
GREEN = (50, 230, 120)
PURPLE = (180, 80, 255)
GRAY = (80, 90, 120)
SHADOW = (110, 0, 0)


# ============ GAME OBJECTS ============
stars = []
for i in range(50):
    stars.append([
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT),
        random.randint(1, 2),
        random.uniform(0.5, 1.5)
    ])

PW, PH = s(55), s(45)
PSPEED = s(7)
BW, BH = s(6), s(18)
BSPEED = s(11)
EW, EH = s(55), s(45)

player = pygame.Rect(WIDTH // 2 - PW // 2, HEIGHT - s(200), PW, PH)
bullets = []
enemies = []
explosions = []

score = 0
lives = 3
missed = 0
level = 1
game_started = False
game_over = False
enemy_timer = 0
shoot_timer = 0

LEVELS = {
    1: (s(4),  32),
    2: (s(5),  26),
    3: (s(7),  20),
    4: (s(9),  15),
    5: (s(12), 10),
}

BS = s(105)
BM = s(25)

btn_left  = pygame.Rect(BM, HEIGHT - BS - BM, BS, BS)
btn_right = pygame.Rect(BM * 2 + BS, HEIGHT - BS - BM, BS, BS)
btn_shoot = pygame.Rect(WIDTH - BS - BM, HEIGHT - BS - BM, BS, BS)
btn_start   = pygame.Rect(WIDTH // 2 - s(150), int(HEIGHT * 0.68), s(300), s(80))
btn_restart = pygame.Rect(WIDTH // 2 - s(150), int(HEIGHT * 0.82), s(300), s(70))

active_touches = {}


# ============ DRAWING ============
def txt(text, font, color, x, y, center=True):
    if font is None:
        return
    try:
        img = font.render(str(text), True, color)
        r = img.get_rect()
        if center:
            r.center = (x, y)
        else:
            r.topleft = (x, y)
        screen.blit(img, r)
    except Exception as e:
        log("txt error: " + str(e))


def txt_shadow(text, font, color, x, y, center=True):
    off = s(3)
    txt(text, font, SHADOW, x + off, y + off, center)
    txt(text, font, color, x, y, center)


def draw_stars():
    for st in stars:
        try:
            pygame.draw.circle(screen, WHITE, (int(st[0]), int(st[1])), st[2])
        except Exception:
            pass


def move_stars():
    for st in stars:
        st[1] += st[3]
        if st[1] > HEIGHT:
            st[1] = 0
            st[0] = random.randint(0, WIDTH)


def draw_player():
    cx = player.centerx
    pygame.draw.polygon(screen, BLUE, [(cx, player.top),
                                       (player.left, player.bottom),
                                       (player.right, player.bottom)])
    pygame.draw.circle(screen, LIGHT_BLUE, (cx, player.top + s(18)), s(8))
    pygame.draw.polygon(screen, PURPLE,
        [(player.left, player.bottom),
         (player.left - s(10), player.bottom + s(5)),
         (player.left + s(10), player.bottom - s(15))])
    pygame.draw.polygon(screen, PURPLE,
        [(player.right, player.bottom),
         (player.right + s(10), player.bottom + s(5)),
         (player.right - s(10), player.bottom - s(15))])
    fh = random.randint(s(10), s(22))
    pygame.draw.polygon(screen, ORANGE, [(cx - s(8), player.bottom),
                                         (cx + s(8), player.bottom),
                                         (cx, player.bottom + fh)])


def draw_enemy(r):
    pygame.draw.rect(screen, RED, r, border_radius=s(12))
    pygame.draw.circle(screen, WHITE, (r.x + s(16), r.y + s(16)), s(7))
    pygame.draw.circle(screen, WHITE, (r.x + s(39), r.y + s(16)), s(7))
    pygame.draw.circle(screen, BLACK, (r.x + s(16), r.y + s(16)), s(3))
    pygame.draw.circle(screen, BLACK, (r.x + s(39), r.y + s(16)), s(3))


def draw_bullet(r):
    pygame.draw.rect(screen, YELLOW, r, border_radius=s(3))


def draw_hud():
    hh = int(HEIGHT * 0.065)
    pygame.draw.rect(screen, DARK_BLUE, (0, 0, WIDTH, hh))
    pygame.draw.line(screen, PURPLE, (0, hh), (WIDTH, hh), s(2))
    cy = hh // 2
    txt("SCORE " + str(score), F_HUD, WHITE, s(18), cy, False)
    txt("LEVEL " + str(level), F_HUD, YELLOW, WIDTH // 2, cy)
    # lives hearts
    lw = F_HUD.size("LIVES")[0]
    hw = s(16)
    n = max(lives, 0)
    total = lw + s(10) + n * (hw * 2 + s(4))
    sx = WIDTH - s(15) - total
    txt("LIVES", F_HUD, WHITE, sx, cy, False)
    hx = sx + lw + s(10)
    for i in range(n):
        r = s(6)
        pygame.draw.circle(screen, RED, (hx + r, cy - s(2)), r)
        pygame.draw.circle(screen, RED, (hx + r * 3, cy - s(2)), r)
        pygame.draw.polygon(screen, RED, [
            (hx, cy + s(1)),
            (hx + r * 4, cy + s(1)),
            (hx + r * 2, cy + r + s(4))
        ])
        hx += hw * 2 + s(4)


def draw_buttons():
    pygame.draw.rect(screen, GRAY, btn_left, border_radius=s(18))
    txt("<<", F_TITLE, WHITE, btn_left.centerx, btn_left.centery)
    pygame.draw.rect(screen, GRAY, btn_right, border_radius=s(18))
    txt(">>", F_TITLE, WHITE, btn_right.centerx, btn_right.centery)
    pygame.draw.rect(screen, RED, btn_shoot, border_radius=s(18))
    txt("FIRE", F_MID, WHITE, btn_shoot.centerx, btn_shoot.centery)


def shoot():
    global shoot_timer
    if shoot_timer <= 0:
        bullets.append(pygame.Rect(player.centerx - BW // 2,
                                   player.top - BH, BW, BH))
        shoot_timer = 8


def reset_game():
    global score, lives, missed, level, game_over, enemy_timer, shoot_timer
    score = 0; lives = 3; missed = 0; level = 1
    game_over = False; enemy_timer = 0; shoot_timer = 0
    bullets.clear(); enemies.clear(); explosions.clear()
    player.x = WIDTH // 2 - PW // 2
    player.y = HEIGHT - s(200)


def press_at(x, y):
    global game_started
    if not game_started:
        if btn_start.collidepoint(x, y):
            game_started = True
    elif game_over:
        if btn_restart.collidepoint(x, y):
            reset_game(); game_started = True


def touch_action(x, y):
    if btn_left.collidepoint(x, y):  return "left"
    if btn_right.collidepoint(x, y): return "right"
    if btn_shoot.collidepoint(x, y): return "shoot"
    return None


# ============ MAIN LOOP ============
log("entering main loop")
running = True
frame = 0

try:
    while running:
        frame += 1
        if frame % 300 == 0:
            log("frame " + str(frame))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RETURN and not game_started:
                    game_started = True
                elif event.key == pygame.K_SPACE and game_started and not game_over:
                    shoot()
                elif event.key == pygame.K_r and game_over:
                    reset_game(); game_started = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                press_at(event.pos[0], event.pos[1])
            elif hasattr(pygame, 'FINGERDOWN') and event.type == pygame.FINGERDOWN:
                x = int(event.x * WIDTH); y = int(event.y * HEIGHT)
                press_at(x, y)
                active_touches[event.finger_id] = touch_action(x, y)
            elif hasattr(pygame, 'FINGERUP') and event.type == pygame.FINGERUP:
                active_touches.pop(event.finger_id, None)

        move_stars()

        # ---- START SCREEN ----
        if not game_started:
            screen.fill(BLACK)
            draw_stars()
            txt("Amouzesh Barnameh Nevisi", F_MID, LIGHT_BLUE,
                WIDTH // 2, int(HEIGHT * 0.08))
            txt_shadow("OSTAD NADERI", F_EMPH, NEON,
                       WIDTH // 2, int(HEIGHT * 0.13))
            txt("SPACE", F_TITLE, BLUE, WIDTH // 2, int(HEIGHT * 0.25))
            txt("SHOOTER", F_TITLE, PURPLE, WIDTH // 2, int(HEIGHT * 0.33))
            txt("Salam be bazi-e sefine-ye", F_MID, WHITE,
                WIDTH // 2, int(HEIGHT * 0.44))
            txt_shadow("Ostad Naderi", F_EMPH, NEON,
                       WIDTH // 2, int(HEIGHT * 0.50))
            txt("khosh oomadi", F_MID, WHITE, WIDTH // 2, int(HEIGHT * 0.56))
            txt("Baraye shoroo-e bazi", F_MID, LIGHT_BLUE,
                WIDTH // 2, int(HEIGHT * 0.61))
            txt("dokmeye paeen ro bezan", F_MID, LIGHT_BLUE,
                WIDTH // 2, int(HEIGHT * 0.65))
            pygame.draw.rect(screen, BLUE, btn_start, border_radius=s(15))
            txt("SHOROO-E BAZI", F_MID, WHITE,
                btn_start.centerx, btn_start.centery)
            pygame.display.flip()
            clock.tick(60)
            continue

        # ---- PLAYING ----
        if not game_over:
            spd, dly = LEVELS[level]

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:  player.x -= PSPEED
            if keys[pygame.K_RIGHT]: player.x += PSPEED

            if "left" in active_touches.values():  player.x -= PSPEED
            if "right" in active_touches.values(): player.x += PSPEED
            if "shoot" in active_touches.values(): shoot()

            hh = int(HEIGHT * 0.065)
            if player.left < 0: player.left = 0
            if player.right > WIDTH: player.right = WIDTH
            if player.top < hh + s(5): player.top = hh + s(5)
            if player.bottom > HEIGHT - BS - BM - s(15):
                player.bottom = HEIGHT - BS - BM - s(15)

            if shoot_timer > 0: shoot_timer -= 1

            enemy_timer += 1
            if enemy_timer >= dly:
                x_max = WIDTH - EW - s(10)
                if x_max > s(10):
                    enemies.append(pygame.Rect(
                        random.randint(s(10), x_max), -s(50), EW, EH))
                enemy_timer = 0

            for b in bullets: b.y -= BSPEED
            bullets = [b for b in bullets if b.bottom > hh]
            for e in enemies: e.y += spd

            if bullets and enemies:
                nb = []
                for b in bullets:
                    hit = -1
                    for i in range(len(enemies)):
                        if b.colliderect(enemies[i]):
                            hit = i; break
                    if hit >= 0:
                        e = enemies.pop(hit)
                        score += 1
                        explosions.append([e.centerx, e.centery, s(5), 10])
                    else:
                        nb.append(b)
                bullets = nb

            ne = []
            for e in enemies:
                if e.colliderect(player):
                    explosions.append([e.centerx, e.centery, s(5), 10])
                    lives -= 1
                elif e.top >= HEIGHT:
                    missed += 1; lives -= 1
                else:
                    ne.append(e)
            enemies = ne

            if lives <= 0: game_over = True

            if score >= 40: level = 5
            elif score >= 30: level = 4
            elif score >= 20: level = 3
            elif score >= 10: level = 2

            screen.fill(BLACK)
            draw_stars()
            draw_player()
            for b in bullets: draw_bullet(b)
            for e in enemies: draw_enemy(e)
            for exp in explosions:
                r = max(1, int(exp[2]))
                pygame.draw.circle(screen, ORANGE, (exp[0], exp[1]), r)
                pygame.draw.circle(screen, YELLOW, (exp[0], exp[1]),
                                   max(s(2), r // 2))

            i = len(explosions) - 1
            while i >= 0:
                explosions[i][2] += s(2)
                explosions[i][3] -= 1
                if explosions[i][3] <= 0: explosions.pop(i)
                i -= 1

            draw_hud()
            draw_buttons()

        # ---- GAME OVER ----
        else:
            screen.fill(BLACK)
            draw_stars()
            bw_ = int(WIDTH * 0.92); bh_ = int(HEIGHT * 0.72)
            bx = (WIDTH - bw_) // 2; by = (HEIGHT - bh_) // 2
            pygame.draw.rect(screen, DARK_BLUE, (bx, by, bw_, bh_),
                             border_radius=s(20))
            txt("GAME OVER", F_TITLE, RED, WIDTH // 2, by + s(60))
            txt("Entezar-e", F_MID, ORANGE, WIDTH // 2, by + s(135))
            txt_shadow("Ostad Naderi", F_EMPH, NEON,
                       WIDTH // 2, by + s(185))
            txt("azat bishtar bood,", F_MID, ORANGE,
                WIDTH // 2, by + s(235))
            txt("dobareh talash kon!", F_MID, ORANGE,
                WIDTH // 2, by + s(270))
            txt("Score: " + str(score) + "  Level: " + str(level),
                F_HUD, WHITE, WIDTH // 2, by + s(320))
            pygame.draw.rect(screen, GREEN, btn_restart, border_radius=s(15))
            txt("SHOROO-E DOBAREH", F_MID, BLACK,
                btn_restart.centerx, btn_restart.centery)

        pygame.display.flip()
        clock.tick(60)

except Exception as e:
    log("MAIN LOOP CRASH: " + str(e))
    log(traceback.format_exc())

log("GAME END")
# هیچ sys.exit() ای اینجا نیست
