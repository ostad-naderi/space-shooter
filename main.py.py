# -*- coding: utf-8 -*-
import pygame, random, sys, os

pygame.init()

# ---------- دستگاه ----------
IS_ANDROID = ('ANDROID_ARGUMENT' in os.environ or
              'ANDROID_ROOT' in os.environ or
              os.path.exists('/system/build.prop'))

if IS_ANDROID:
    try:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    except pygame.error:
        info = pygame.display.Info()
        screen = pygame.display.set_mode(
            (info.current_w or 720, info.current_h or 1280),
            pygame.FULLSCREEN)
    WIDTH, HEIGHT = screen.get_size()
    SCALE = max(1.0, HEIGHT / 900.0)
else:
    WIDTH, HEIGHT = 900, 650
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    SCALE = 1.0

def s(v):
    return max(1, int(v * SCALE))

pygame.display.set_caption("Space Shooter - Ostad Naderi")
clock = pygame.time.Clock()

# ---------- Colors ----------
BLACK = (5, 8, 25)
DARK_BLUE = (10, 15, 45)
WHITE = (255, 255, 255)
BLUE = (40, 180, 255)
LIGHT_BLUE = (120, 220, 255)
RED = (255, 60, 70)
DARK_RED = (170, 30, 40)
YELLOW = (255, 220, 40)
NEON = (255, 255, 0)
ORANGE = (255, 130, 30)
GREEN = (50, 230, 120)
PURPLE = (180, 80, 255)
GRAY = (80, 90, 120)
SHADOW = (110, 0, 0)

# ---------- Font TTF ----------
def find_ttf():
    for p in [
        "/system/fonts/Roboto-Bold.ttf",
        "/system/fonts/Roboto-Regular.ttf",
        "/system/fonts/DroidSans-Bold.ttf",
        "/system/fonts/DroidSans.ttf",
        "/system/fonts/NotoSans-Bold.ttf",
        "/system/fonts/NotoSans-Regular.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/Library/Fonts/Arial.ttf",
    ]:
        if os.path.exists(p):
            return p
    return None

FONT_PATH = find_ttf()

def F(size):
    if FONT_PATH:
        try:
            return pygame.font.Font(FONT_PATH, size)
        except Exception:
            pass
    return pygame.font.Font(None, size)

# ---------- Fonts ----------
F_MID   = F(s(26))
F_EMPH  = F(s(42))
F_TITLE = F(s(70))

# داخل بازی
F_HUD       = F(s(18))
F_HUD_SMALL = F(s(16))
F_BTN       = F(s(26))
F_BTN_ARROW = F(s(52))

# ---------- Stars ----------
stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT),
          random.randint(1, s(2)), random.uniform(0.5, 1.8) * SCALE]
         for _ in range(50)]

# ---------- Sizes ----------
PW, PH = s(55), s(45)
PSPEED = s(7)
BW, BH = s(6), s(18)
BSPEED = s(11)
EW, EH = s(55), s(45)

# ---------- State ----------
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

# ---------- سطوح ----------
LEVELS = {
    1: (s(4),  32),
    2: (s(5),  26),
    3: (s(7),  20),
    4: (s(9),  15),
    5: (s(12), 10),
}

# ---------- Buttons ----------
BS = s(105)
BM = s(25)

btn_left  = pygame.Rect(BM, HEIGHT - BS - BM, BS, BS)
btn_right = pygame.Rect(BM * 2 + BS, HEIGHT - BS - BM, BS, BS)
btn_shoot = pygame.Rect(WIDTH - BS - BM, HEIGHT - BS - BM, BS, BS)
btn_start   = pygame.Rect(WIDTH // 2 - s(150), int(HEIGHT * 0.68),
                          s(300), s(80))
btn_restart = pygame.Rect(WIDTH // 2 - s(150), int(HEIGHT * 0.82),
                          s(300), s(70))

active_touches = {}


def txt(t, f, c, x, y, center=True):
    img = f.render(t, True, c)
    r = img.get_rect()
    if center:
        r.center = (x, y)
    else:
        r.topleft = (x, y)
    screen.blit(img, r)


def txt_shadow(t, f, c, x, y, center=True, off=None):
    if off is None:
        off = s(3)
    txt(t, f, SHADOW, x + off, y + off, center)
    txt(t, f, c, x, y, center)


def draw_stars():
    for st in stars:
        pygame.draw.circle(screen, WHITE, (int(st[0]), int(st[1])), st[2])


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
    pygame.draw.line(screen, DARK_RED, (r.x + s(17), r.y + s(32)),
                     (r.x + s(38), r.y + s(32)), s(3))


def draw_bullet(r):
    pygame.draw.rect(screen, YELLOW, r, border_radius=s(3))


def draw_hud():
    """نوار بالا - متناسب و کوچک"""
    hh = int(HEIGHT * 0.065)
    pygame.draw.rect(screen, DARK_BLUE, (0, 0, WIDTH, hh))
    pygame.draw.line(screen, PURPLE, (0, hh), (WIDTH, hh), s(2))

    cy = hh // 2

    # SCORE - چپ‌چین (center=False) تا از لبه بیرون نزنه
    txt(f"SCORE {score}", F_HUD, WHITE, s(18), cy, center=False)

    # LEVEL - وسط
    txt(f"LEVEL {level}", F_HUD, YELLOW, WIDTH // 2, cy)

    # LIVES - راست
    lives_label_w = F_HUD.size("LIVES")[0]
    heart_w = s(16)
    gap = s(4)
    n = max(lives, 0)

    total_hearts = n * (heart_w * 2 + gap) if n > 0 else 0
    total_w = lives_label_w + s(10) + total_hearts
    start_x = WIDTH - s(15) - total_w

    txt("LIVES", F_HUD, WHITE, start_x, cy, center=False)
    hx = start_x + lives_label_w + s(10)

    for i in range(n):
        hcy = cy
        r = s(6)
        pygame.draw.circle(screen, RED, (hx + r, hcy - s(2)), r)
        pygame.draw.circle(screen, RED, (hx + r * 3, hcy - s(2)), r)
        pygame.draw.polygon(screen, RED, [
            (hx, hcy + s(1)),
            (hx + r * 4, hcy + s(1)),
            (hx + r * 2, hcy + r + s(4))
        ])
        hx += heart_w * 2 + gap


def draw_buttons():
    pygame.draw.rect(screen, GRAY, btn_left, border_radius=s(18))
    txt("<<", F_BTN_ARROW, WHITE, btn_left.centerx, btn_left.centery)
    pygame.draw.rect(screen, GRAY, btn_right, border_radius=s(18))
    txt(">>", F_BTN_ARROW, WHITE, btn_right.centerx, btn_right.centery)
    pygame.draw.rect(screen, RED, btn_shoot, border_radius=s(18))
    txt("FIRE", F_BTN, WHITE, btn_shoot.centerx, btn_shoot.centery)


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


# ================= MAIN =================
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: running = False
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

    # ---------- START ----------
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
        txt("SHOROO-E BAZI", F_BTN, WHITE,
            btn_start.centerx, btn_start.centery)
        pygame.display.flip()
        clock.tick(60)
        continue

    # ---------- PLAYING ----------
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

        # spawn دشمن
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

        # برخورد تیر با دشمن
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

        # برخورد دشمن با بازیکن / فرار به پایین
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

        # سطح‌بندی
        if score >= 40: level = 5
        elif score >= 30: level = 4
        elif score >= 20: level = 3
        elif score >= 10: level = 2

        # Draw
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

    # ---------- GAME OVER ----------
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
        txt(f"Score: {score}   Level: {level}   Missed: {missed}",
            F_HUD, WHITE, WIDTH // 2, by + s(320))
        pygame.draw.rect(screen, GREEN, btn_restart, border_radius=s(15))
        txt("SHOROO-E DOBAREH", F_BTN, BLACK,
            btn_restart.centerx, btn_restart.centery)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()