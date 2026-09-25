# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, Ellipse, Triangle, Line
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
import random



class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.score = 0
        self.lives = 3
        self.level = 1
        self.missed = 0
        self.game_started = False
        self.game_over = False
        self.enemy_timer = 0
        self.shoot_timer = 0
        self.stars = []
        self.bullets = []
        self.enemies = []
        self.explosions = []

        # Buttons state
        self.btn_left = [0, 0, 0, 0]
        self.btn_right = [0, 0, 0, 0]
        self.btn_shoot = [0, 0, 0, 0]
        self.btn_start = [0, 0, 0, 0]
        self.btn_restart = [0, 0, 0, 0]

        self.active_touches = {}
        self.player = None

        self._init_stars()
        self.bind(pos=self._on_layout, size=self._on_layout)
        Clock.schedule_interval(self.update, 1 / 60.0)

    def _init_stars(self):
        w, h = max(self.width, dp(360)), max(self.height, dp(640))
        self.stars = [[random.random() * w, random.random() * h,
                       random.uniform(1, 3), random.uniform(0.5, 2)]
                      for _ in range(60)]

    def _on_layout(self, *args):
        w, h = self.size
        if w < 100 or h < 100:
            return
        player_h = dp(45)
        player_y = max(dp(90), h - dp(220))
        self.player = [w / 2 - dp(28), player_y, dp(55), player_h]
        bs = dp(100)
        bm = dp(25)
        self.btn_left = [bm, bm, bs, bs]
        self.btn_right = [bm * 2 + bs, bm, bs, bs]
        self.btn_shoot = [w - bs - bm, bm, bs, bs]
        self.btn_start = [w / 2 - dp(150), h * 0.65, dp(300), dp(80)]
        self.btn_restart = [w / 2 - dp(150), h * 0.80, dp(300), dp(75)]

    def update(self, dt):
        w, h = self.width, self.height
        if w < 100 or h < 100 or self.player is None:
            return

        # Move stars
        for st in self.stars:
            st[1] += st[3]
            if st[1] > h:
                st[1] = 0
                st[0] = random.random() * w

        if not self.game_started:
            self.draw_all()
            return

        if self.game_over:
            self.draw_all()
            return

        # Player movement
        speed = dp(7)
        if "left" in self.active_touches.values():
            self.player[0] -= speed
        if "right" in self.active_touches.values():
            self.player[0] += speed
        if "shoot" in self.active_touches.values():
            self.shoot()

        # Boundaries
        if self.player[0] < 0:
            self.player[0] = 0
        if self.player[0] + self.player[2] > w:
            self.player[0] = w - self.player[2]

        # Shoot timer
        if self.shoot_timer > 0:
            self.shoot_timer -= 1

        # Level
        if self.score >= 40:
            self.level = 5
        elif self.score >= 30:
            self.level = 4
        elif self.score >= 20:
            self.level = 3
        elif self.score >= 10:
            self.level = 2

        speeds = {1: (dp(4), 32), 2: (dp(5), 26), 3: (dp(7), 20),
                  4: (dp(9), 15), 5: (dp(12), 10)}
        spd, dly = speeds[self.level]

        # Spawn enemies
        self.enemy_timer += 1
        if self.enemy_timer >= dly:
            ew, eh = dp(55), dp(45)
            if w > ew + dp(20):
                x = random.randint(int(dp(10)), int(w - ew - dp(10)))
                self.enemies.append([x, -dp(50), ew, eh])
            self.enemy_timer = 0

        # Move bullets
        bs = dp(11)
        new_bullets = []
        for b in self.bullets:
            b[1] -= bs
            if b[1] + b[3] > 0:
                new_bullets.append(b)
        self.bullets = new_bullets

        # Move enemies
        for e in self.enemies:
            e[1] += spd

        # Bullet vs Enemy
        remaining_bullets = []
        for b in self.bullets:
            hit_idx = -1
            for i in range(len(self.enemies)):
                e = self.enemies[i]
                if (b[0] < e[0] + e[2] and b[0] + b[2] > e[0] and
                        b[1] < e[1] + e[3] and b[1] + b[3] > e[1]):
                    hit_idx = i
                    break
            if hit_idx >= 0:
                e = self.enemies.pop(hit_idx)
                self.score += 1
                self.explosions.append([e[0] + e[2] / 2, e[1] + e[3] / 2, dp(5), 10])
            else:
                remaining_bullets.append(b)
        self.bullets = remaining_bullets

        # Enemy vs Player / Missed
        remaining_enemies = []
        for e in self.enemies:
            if (e[0] < self.player[0] + self.player[2] and
                    e[0] + e[2] > self.player[0] and
                    e[1] < self.player[1] + self.player[3] and
                    e[1] + e[3] > self.player[1]):
                self.explosions.append([e[0] + e[2] / 2, e[1] + e[3] / 2, dp(5), 10])
                self.lives -= 1
            elif e[1] > h:
                self.missed += 1
                self.lives -= 1
            else:
                remaining_enemies.append(e)
        self.enemies = remaining_enemies

        if self.lives <= 0:
            self.game_over = True

        # Update explosions
        i = len(self.explosions) - 1
        while i >= 0:
            self.explosions[i][2] += dp(2)
            self.explosions[i][3] -= 1
            if self.explosions[i][3] <= 0:
                self.explosions.pop(i)
            i -= 1

        self.draw_all()

    def shoot(self):
        if self.shoot_timer <= 0:
            bw, bh = dp(6), dp(18)
            self.bullets.append([
                self.player[0] + self.player[2] / 2 - bw / 2,
                self.player[1] - bh, bw, bh
            ])
            self.shoot_timer = 8

    def draw_all(self):
        self.canvas.clear()
        w, h = self.width, self.height

        with self.canvas:
            Color(0.02, 0.03, 0.1, 1)
            Rectangle(pos=(0, 0), size=(w, h))

            # Stars
            Color(1, 1, 1, 1)
            for st in self.stars:
                Ellipse(pos=(st[0], st[1]), size=(st[2], st[2]))

            # Start Screen
            if not self.game_started:
                self._draw_start_screen(w, h)
                return

            # Playing / Game Over
            if not self.game_over:
                # Player
                self._draw_player()

                # Bullets
                Color(1, 0.86, 0.16, 1)
                for b in self.bullets:
                    Rectangle(pos=(b[0], b[1]), size=(b[2], b[3]))

                # Enemies
                for e in self.enemies:
                    self._draw_enemy(e)

                # Explosions
                for exp in self.explosions:
                    r = max(2, int(exp[2]))
                    Color(1, 0.5, 0.1, 1)
                    Ellipse(pos=(exp[0] - r, exp[1] - r), size=(r * 2, r * 2))
                    Color(1, 0.86, 0.16, 1)
                    r2 = max(1, r // 2)
                    Ellipse(pos=(exp[0] - r2, exp[1] - r2),
                            size=(r2 * 2, r2 * 2))

                self._draw_hud(w, h)
                self._draw_buttons(w, h)
            else:
                self._draw_game_over(w, h)

    def _draw_player(self):
        p = self.player
        cx = p[0] + p[2] / 2
        # Body
        Color(0.16, 0.71, 1, 1)
        Triangle(points=[cx, p[1] + p[3],
                         p[0], p[1],
                         p[0] + p[2], p[1]])
        # Cockpit
        Color(0.47, 0.86, 1, 1)
        Ellipse(pos=(cx - dp(8), p[1] + p[3] - dp(28)),
                size=(dp(16), dp(16)))
        # Flame
        Color(1, 0.5, 0.1, 1)
        Triangle(points=[cx - dp(8), p[1],
                         cx + dp(8), p[1],
                         cx, p[1] - dp(15)])

    def _draw_enemy(self, e):
        Color(1, 0.24, 0.27, 1)
        Rectangle(pos=(e[0], e[1]), size=(e[2], e[3]))
        # Eyes
        Color(1, 1, 1, 1)
        Ellipse(pos=(e[0] + dp(11), e[1] + dp(11)), size=(dp(12), dp(12)))
        Ellipse(pos=(e[0] + dp(32), e[1] + dp(11)), size=(dp(12), dp(12)))
        Color(0, 0, 0, 1)
        Ellipse(pos=(e[0] + dp(14), e[1] + dp(14)), size=(dp(6), dp(6)))
        Ellipse(pos=(e[0] + dp(35), e[1] + dp(14)), size=(dp(6), dp(6)))

    def _draw_hud(self, w, h):
        hh = dp(60)
        Color(0.04, 0.06, 0.18, 1)
        Rectangle(pos=(0, h - hh), size=(w, hh))
        Color(0.71, 0.31, 1, 1)
        Line(points=[0, h - hh, w, h - hh], width=dp(2))

    def _draw_buttons(self, w, h):
        # Left
        Color(0.31, 0.35, 0.47, 1)
        Rectangle(pos=(self.btn_left[0], self.btn_left[1]),
                  size=(self.btn_left[2], self.btn_left[3]))
        # Right
        Rectangle(pos=(self.btn_right[0], self.btn_right[1]),
                  size=(self.btn_right[2], self.btn_right[3]))
        # Shoot
        Color(1, 0.24, 0.27, 1)
        Rectangle(pos=(self.btn_shoot[0], self.btn_shoot[1]),
                  size=(self.btn_shoot[2], self.btn_shoot[3]))
        # Start button
        Color(0.16, 0.71, 1, 1)
        Rectangle(pos=(self.btn_start[0], self.btn_start[1]),
                  size=(self.btn_start[2], self.btn_start[3]))

    def _draw_start_screen(self, w, h):
        # Start button
        Color(0.16, 0.71, 1, 1)
        Rectangle(pos=(self.btn_start[0], self.btn_start[1]),
                  size=(self.btn_start[2], self.btn_start[3]))
        # Restart button
        Color(0.2, 0.9, 0.47, 1)
        Rectangle(pos=(self.btn_restart[0], self.btn_restart[1]),
                  size=(self.btn_restart[2], self.btn_restart[3]))

    def _draw_game_over(self, w, h):
        Color(0.04, 0.06, 0.18, 1)
        Rectangle(pos=(w * 0.05, h * 0.15), size=(w * 0.9, h * 0.7))
        Color(0.2, 0.9, 0.47, 1)
        Rectangle(pos=(self.btn_restart[0], self.btn_restart[1]),
                  size=(self.btn_restart[2], self.btn_restart[3]))

    def on_touch_down(self, touch):
        x, y = touch.x, touch.y
        if not self.game_started:
            if self._in_rect(x, y, self.btn_start):
                self.game_started = True
                return True
        elif self.game_over:
            if self._in_rect(x, y, self.btn_restart):
                self.reset_game()
                self.game_started = True
                return True
        else:
            if self._in_rect(x, y, self.btn_left):
                self.active_touches[touch.uid] = "left"
            elif self._in_rect(x, y, self.btn_right):
                self.active_touches[touch.uid] = "right"
            elif self._in_rect(x, y, self.btn_shoot):
                self.active_touches[touch.uid] = "shoot"
        return True

    def on_touch_up(self, touch):
        self.active_touches.pop(touch.uid, None)

    def _in_rect(self, x, y, r):
        return r[0] <= x <= r[0] + r[2] and r[1] <= y <= r[1] + r[3]

    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.missed = 0
        self.level = 1
        self.game_over = False
        self.enemy_timer = 0
        self.shoot_timer = 0
        self.bullets = []
        self.enemies = []
        self.explosions = []
        if self.player:
            self.player[0] = self.width / 2 - self.player[2] / 2
            self.player[1] = max(dp(90), self.height - dp(220))


class GameRoot(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game = GameWidget(size_hint=(1, 1), pos_hint={'x': 0, 'y': 0})
        self.add_widget(self.game)

        # Text labels (فارسی با فونت پیش‌فرض Kivy)
        self.title_label = Label(
            text='[b]سفینه نادری[/b]',
            markup=True,
            font_size=dp(28),
            color=(1, 1, 0, 1),
            size_hint=(1, None),
            height=dp(40),
            pos_hint={'x': 0, 'top': 1})

        self.subtitle = Label(
            text='Amouzesh Barnameh Nevisi - Ostad Naderi',
            font_size=dp(14),
            color=(0.5, 0.86, 1, 1),
            size_hint=(1, None),
            height=dp(30),
            pos_hint={'x': 0, 'top': 0.95})

        self.welcome = Label(
            text='سلام به بازی سفینه استاد نادری خوش اومدی',
            font_size=dp(16),
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=dp(30),
            pos_hint={'x': 0, 'top': 0.42})

        self.instruction = Label(
            text='برای شروع بازی دکمه پایین رو بزن',
            font_size=dp(15),
            color=(0.5, 0.86, 1, 1),
            size_hint=(1, None),
            height=dp(28),
            pos_hint={'x': 0, 'top': 0.38})

        self.start_btn = Button(
            text='شروع بازی',
            font_size=dp(20),
            background_color=(0.16, 0.71, 1, 1),
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(dp(300), dp(80)),
            pos_hint={'center_x': 0.5, 'y': 0.10})

        self.gameover_label = Label(
            text='[b]GAME OVER[/b]',
            markup=True,
            font_size=dp(36),
            color=(1, 0.24, 0.27, 1),
            size_hint=(1, None),
            height=dp(60),
            pos_hint={'x': 0, 'top': 0.80},
            opacity=0)

        self.msg_label = Label(
            text='انتظار استاد نادری ازت بیشتر بود\nدوباره تلاش کن',
            font_size=dp(18),
            color=(1, 0.51, 0.11, 1),
            size_hint=(1, None),
            height=dp(70),
            pos_hint={'x': 0, 'top': 0.72},
            opacity=0)

        self.restart_btn = Button(
            text='شروع دوباره',
            font_size=dp(18),
            background_color=(0.2, 0.9, 0.47, 1),
            color=(0, 0, 0, 1),
            size_hint=(None, None),
            size=(dp(300), dp(75)),
            pos_hint={'center_x': 0.5, 'y': 0.15},
            opacity=0)

        self.add_widget(self.subtitle)
        self.add_widget(self.title_label)
        self.add_widget(self.welcome)
        self.add_widget(self.instruction)
        self.add_widget(self.start_btn)
        self.add_widget(self.gameover_label)
        self.add_widget(self.msg_label)
        self.add_widget(self.restart_btn)

        self.start_btn.bind(on_release=self.start_game)
        self.restart_btn.bind(on_release=self.restart_game)

        # Score display
        self.score_label = Label(
            text='',
            font_size=dp(16),
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(dp(300), dp(30)),
            pos_hint={'x': 0.02, 'top': 0.995},
            halign='left')
        self.score_label.bind(size=self._update_score_text)
        self.add_widget(self.score_label)

        Clock.schedule_interval(self._update_status, 0.1)

    def _update_score_text(self, *args):
        self.score_label.text_size = self.score_label.size

    def _update_status(self, dt):
        g = self.game
        if g.game_started and not g.game_over:
            self.score_label.text = f'SCORE: {g.score}   LEVEL: {g.level}   LIVES: {g.lives}'
            self.score_label.opacity = 1
            # Hide start screen items
            self.welcome.opacity = 0
            self.instruction.opacity = 0
            self.title_label.opacity = 0
            self.subtitle.opacity = 0
            self.start_btn.opacity = 0
            self.gameover_label.opacity = 0
            self.msg_label.opacity = 0
            self.restart_btn.opacity = 0
        elif g.game_over:
            self.score_label.opacity = 0
            self.gameover_label.opacity = 1
            self.msg_label.opacity = 1
            self.restart_btn.opacity = 1
            self.start_btn.opacity = 0
            self.welcome.opacity = 0
            self.instruction.opacity = 0
            self.title_label.opacity = 0
            self.subtitle.opacity = 0
        else:
            self.score_label.opacity = 0
            self.welcome.opacity = 1
            self.instruction.opacity = 1
            self.title_label.opacity = 1
            self.subtitle.opacity = 1
            self.start_btn.opacity = 1
            self.gameover_label.opacity = 0
            self.msg_label.opacity = 0
            self.restart_btn.opacity = 0

    def start_game(self, *args):
        self.game.game_started = True
        self.game.game_over = False

    def restart_game(self, *args):
        self.game.reset_game()
        self.game.game_started = True


class SpaceShooterApp(App):
    def build(self):
        return GameRoot()


if __name__ == '__main__':
    SpaceShooterApp().run()
