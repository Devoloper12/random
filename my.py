#!/usr/bin/env python3
"""
Single-File Terminal Proposal Animation (CMD, PowerShell & GitHub curl Ready)
=============================================================================
A zero-dependency, pure-Python cinematic proposal animation built to run:
- Directly from GitHub via `curl -sL <RAW_URL> | python -` (CMD & PowerShell)
- Locally in Windows Command Prompt (cmd.exe), PowerShell 5.1/7+, and Unix
- As a live HTTP chunked stream via `python proposal.py --serve`

Scenes:
  Act 1: Starry night sky + floating hearts + typewriter intro
  Act 2: Velvet ring box opens + sparkling diamond ring rises
  Act 3: Glowing beating heart + "WILL YOU MARRY ME?" + interactive [Y]/[N]
  Act 4: Grand celebration finale with heart fireworks & confetti!
"""

import argparse
import ctypes
import html
import json
import math
import os
import random
import shutil
import signal
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


# ---------------------------------------------------------------------------
# Platform Console & Piped Keyboard Handling
# ---------------------------------------------------------------------------

class WindowsConsoleGuard:
    """Safely enables ANSI VT processing & UTF-8 in Windows CMD/PowerShell and restores on exit."""

    def __init__(self, use_utf8: bool = True):
        self.use_utf8 = use_utf8
        self.is_windows = os.name == "nt"
        self.h_out = None
        self.orig_mode = None
        self.orig_cp = None

    def __enter__(self):
        if self.is_windows:
            try:
                kernel32 = ctypes.windll.kernel32
                h_out = kernel32.GetStdHandle(-11)
                mode = ctypes.c_ulong()
                if kernel32.GetConsoleMode(h_out, ctypes.byref(mode)):
                    self.h_out = h_out
                    self.orig_mode = mode.value
                    kernel32.SetConsoleMode(h_out, mode.value | 0x0004)
                if self.use_utf8:
                    self.orig_cp = kernel32.GetConsoleOutputCP()
                    kernel32.SetConsoleOutputCP(65001)
            except Exception:
                pass

        if self.use_utf8 and hasattr(sys.stdout, "reconfigure"):
            try:
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            sys.stdout.write("\033[?25h\033[0m\n")
            sys.stdout.flush()
        except Exception:
            pass

        if self.is_windows:
            try:
                kernel32 = ctypes.windll.kernel32
                if self.h_out is not None and self.orig_mode is not None:
                    kernel32.SetConsoleMode(self.h_out, self.orig_mode)
                if self.orig_cp:
                    kernel32.SetConsoleOutputCP(self.orig_cp)
            except Exception:
                pass


try:
    import msvcrt

    def setup_keyboard():
        return None

    def restore_keyboard(_state):
        return None

    def check_keypress(_kb_state=None):
        """Works in both CMD and PowerShell, even when stdin is piped from curl."""
        try:
            if not sys.stdout.isatty():
                return None
            if msvcrt.kbhit():
                ch = msvcrt.getch()
                if ch in (b"\x00", b"\xe0"):
                    _ = msvcrt.getch()
                    return None
                return ch.decode("ascii", errors="ignore").lower()
        except Exception:
            return None
        return None

except ImportError:
    import select
    import termios
    import tty

    def setup_keyboard():
        try:
            if sys.stdin.isatty():
                fd = sys.stdin.fileno()
                orig = termios.tcgetattr(fd)
                tty.setcbreak(fd)
                return (fd, orig, None)
            elif sys.stdout.isatty():
                tty_file = open("/dev/tty", "r")
                fd = tty_file.fileno()
                orig = termios.tcgetattr(fd)
                tty.setcbreak(fd)
                return (fd, orig, tty_file)
        except Exception:
            pass
        return None

    def restore_keyboard(state):
        if state is not None:
            fd, orig, tty_file = state
            try:
                termios.tcsetattr(fd, termios.TCSADRAIN, orig)
            except Exception:
                pass
            if tty_file is not None:
                try:
                    tty_file.close()
                except Exception:
                    pass

    def check_keypress(kb_state=None):
        if kb_state is None:
            return None
        _, _, tty_file = kb_state
        stream = tty_file if tty_file is not None else sys.stdin
        try:
            dr, _, _ = select.select([stream], [], [], 0)
            if dr:
                return stream.read(1).lower()
        except Exception:
            pass
        return None


# ---------------------------------------------------------------------------
# Themes & Color Helpers
# ---------------------------------------------------------------------------

THEMES = ["rose", "crimson", "midnight", "sunset", "classic"]

THEME_PALETTES = {
    "rose": {
        "heart": [(130, 18, 70), (215, 45, 115), (255, 115, 175), (255, 225, 242)],
        "diamond": [(165, 235, 255), (235, 250, 255)],
        "band": [(215, 165, 65), (255, 225, 130)],
        "text": [(255, 155, 200), (255, 240, 248)],
        "star": (195, 145, 225),
    },
    "crimson": {
        "heart": [(110, 10, 25), (195, 20, 55), (255, 65, 105), (255, 210, 220)],
        "diamond": [(175, 240, 255), (255, 255, 255)],
        "band": [(215, 170, 55), (255, 225, 120)],
        "text": [(255, 135, 165), (255, 235, 240)],
        "star": (225, 155, 175),
    },
    "midnight": {
        "heart": [(65, 25, 125), (165, 45, 185), (245, 95, 220), (200, 245, 255)],
        "diamond": [(135, 245, 255), (255, 255, 255)],
        "band": [(185, 205, 235), (240, 248, 255)],
        "text": [(175, 225, 255), (255, 180, 240)],
        "star": (145, 185, 255),
    },
    "sunset": {
        "heart": [(145, 25, 25), (230, 75, 55), (255, 155, 90), (255, 240, 195)],
        "diamond": [(200, 245, 255), (255, 255, 255)],
        "band": [(225, 175, 65), (255, 230, 135)],
        "text": [(255, 185, 115), (255, 245, 215)],
        "star": (255, 195, 135),
    },
}


def lerp_rgb(c1, c2, t: float):
    t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


def quant_ansi(rgb, use_16color: bool = False, fallback: str = "\033[95m") -> str:
    if use_16color:
        return fallback
    r = (rgb[0] // 8) * 8
    g = (rgb[1] // 8) * 8
    b = (rgb[2] // 8) * 8
    return f"\033[38;2;{r};{g};{b}m"


def sample_stops(stops, t: float, use_16color: bool = False, fallback: str = "\033[91m") -> str:
    if use_16color:
        if t > 0.8:
            return "\033[97m"
        elif t > 0.5:
            return "\033[95m"
        elif t > 0.25:
            return "\033[91m"
        return "\033[31m"
    v = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
    scaled = v * (len(stops) - 1)
    idx = int(scaled)
    if idx >= len(stops) - 1:
        rgb = stops[-1]
    else:
        rgb = lerp_rgb(stops[idx], stops[idx + 1], scaled - idx)
    return quant_ansi(rgb)


# ---------------------------------------------------------------------------
# Particles: Twinkling Stars, Floating Hearts & Celebration Fireworks
# ---------------------------------------------------------------------------

class Star:
    def __init__(self, w: int, h: int):
        self.x = random.randint(1, max(2, w - 2))
        self.y = random.randint(0, max(1, h - 3))
        self.phase = random.uniform(0.0, math.tau)
        self.speed = random.uniform(1.8, 4.5)
        self.is_heart = random.random() < 0.22


class FireworkSpark:
    def __init__(self, x: float, y: float, vx: float, vy: float, life: float, tint: float, gold: bool):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.max_life = life
        self.life = life
        self.tint = tint
        self.gold = gold


class CelebrationFirework:
    def __init__(self, w: int, h: int):
        self.x = random.uniform(w * 0.18, w * 0.82)
        self.y = float(h - 2)
        self.target_y = random.uniform(h * 0.18, h * 0.44)
        self.vy = -random.uniform(22.0, 31.0)
        self.vx = random.uniform(-2.5, 2.5)
        self.exploded = False
        self.sparks = []
        self.is_heart = random.random() < 0.7

    def explode(self, w: int, h: int):
        self.exploded = True
        scale = min(w * 0.045, h * 0.09)
        if self.is_heart:
            count = 56
            tilt = random.uniform(-0.2, 0.2)
            ct, st = math.cos(tilt), math.sin(tilt)
            for i in range(count):
                t = (i / count) * math.tau
                hx = 16.0 * (math.sin(t) ** 3)
                hy = -(13.0 * math.cos(t) - 5.0 * math.cos(2 * t) - 2.0 * math.cos(3 * t) - math.cos(4 * t))
                rx = (hx * ct - hy * st) * 0.28 * scale * 2.0
                ry = (hx * st + hy * ct) * 0.28 * scale
                jit = random.uniform(0.88, 1.12)
                self.sparks.append(
                    FireworkSpark(self.x, self.y, rx * jit, ry * jit, random.uniform(1.1, 1.7), random.uniform(0.35, 1.0), False)
                )
        else:
            for i in range(42):
                ang = (i / 42.0) * math.tau + random.uniform(-0.08, 0.08)
                spd = random.uniform(8.0, 20.0)
                self.sparks.append(
                    FireworkSpark(self.x, self.y, math.cos(ang) * spd * 1.9, math.sin(ang) * spd, random.uniform(0.9, 1.5), random.uniform(0.5, 1.0), True)
                )

    def update(self, dt: float, w: int, h: int):
        if not self.exploded:
            self.x += self.vx * dt
            self.y += self.vy * dt
            self.vy += 12.0 * dt
            if self.y <= self.target_y or self.vy >= -2.0:
                self.explode(w, h)
        else:
            alive = []
            for sp in self.sparks:
                sp.life -= dt
                if sp.life > 0:
                    sp.vx *= 0.96
                    sp.vy = sp.vy * 0.96 + 7.5 * dt
                    sp.x += sp.vx * dt
                    sp.y += sp.vy * dt
                    alive.append(sp)
            self.sparks = alive

    def done(self) -> bool:
        return self.exploded and not self.sparks


# ---------------------------------------------------------------------------
# Proposal Ring & Heart Art Renderer
# ---------------------------------------------------------------------------

RING_ART = [
    ("   .' \\ | / '.   ", "diamond"),
    ("  /____\\|/____\\  ", "diamond"),
    ("  \\  \\  |  /  /  ", "diamond"),
    ("   \\  \\ | /  /   ", "diamond"),
    ("    \\__\\|/__/    ", "diamond"),
    ("      .-'-.      ", "band"),
    ("    .'     '.    ", "band"),
    ("   /         \\   ", "band"),
    ("   |         |   ", "band"),
    ("   \\         /   ", "band"),
    ("    '._____.'    ", "band"),
]


class ProposalGenerator:
    """Multi-act cinematic proposal animation state machine."""

    def __init__(
        self,
        name: str = "",
        question: str = "WILL YOU MARRY ME?",
        yes_msg: str = "FOREVER & ALWAYS!",
        theme: str = "rose",
        ascii_only: bool = False,
        use_16color: bool = False,
        auto_yes: bool = False,
        loop_stream: bool = False,
        include_hud: bool = True,
        initial_w: int = 78,
        initial_h: int = 22,
    ):
        self.name = name.strip()
        self.question = question
        self.yes_msg = yes_msg
        self.theme_idx = THEMES.index(theme) if theme in THEMES else 0
        self.ascii_only = ascii_only
        self.use_16color = use_16color
        self.auto_yes = auto_yes
        self.loop_stream = loop_stream
        self.include_hud = include_hud

        self.sim_time = 0.0
        self.accepted = False
        self.accept_time = 0.0
        self.no_clicks = 0
        self.no_nudge_until = 0.0

        self.stars = [Star(initial_w, initial_h) for _ in range(36)]
        self.fireworks = []
        self.next_fw = 0.0

    def trigger_yes(self):
        if not self.accepted:
            self.accepted = True
            self.accept_time = self.sim_time
            self.fireworks = []
            self.next_fw = self.sim_time

    def trigger_no(self):
        self.no_clicks += 1
        self.no_nudge_until = self.sim_time + 3.2

    def replay(self):
        self.sim_time = 0.0
        self.accepted = False
        self.accept_time = 0.0
        self.no_clicks = 0
        self.no_nudge_until = 0.0
        self.fireworks = []

    def _draw_text(self, char_buf, col_buf, cur_w: int, canvas_h: int, row: int, text: str, col_fn):
        if not (0 <= row < canvas_h) or not text:
            return
        start_x = max(0, (cur_w - len(text)) // 2)
        row_off = row * cur_w
        for i, ch in enumerate(text):
            tx = start_x + i
            if 0 <= tx < cur_w and ch != " ":
                char_buf[row_off + tx] = ch
                col_buf[row_off + tx] = col_fn(i, len(text))

    def render_frame(self, raw_dt: float, cur_w: int, cur_h: int) -> str:
        self.sim_time += raw_dt

        # In stream loop mode (e.g. curl server), automatically progress & loop
        if self.loop_stream:
            cycle = self.sim_time % 22.0
            if cycle < 11.5 and self.accepted:
                self.accepted = False
                self.fireworks = []
            elif cycle >= 11.5 and not self.accepted:
                self.trigger_yes()
            t = cycle
        else:
            t = self.sim_time
            if self.auto_yes and not self.accepted and t >= 10.5:
                self.trigger_yes()

        cur_theme = THEMES[self.theme_idx]
        eff_16 = self.use_16color or (cur_theme == "classic")
        pal = THEME_PALETTES.get(cur_theme, THEME_PALETTES["rose"])

        canvas_h = max(14, cur_h - (1 if self.include_hud else 0))
        size = cur_w * canvas_h
        char_buf = [" "] * size
        col_buf = [""] * size

        heart_sym = "*" if self.ascii_only else "\u2665"
        bullet_sym = "." if self.ascii_only else "\u2022"
        decor = "<3" if self.ascii_only else "\u2665"

        # 1. Background starry sky
        star_col_dim = quant_ansi(pal["star"], eff_16, "\033[35m")
        star_col_bright = quant_ansi((255, 255, 255), eff_16, "\033[97m")
        for st in self.stars:
            sx = st.x % cur_w
            sy = st.y % max(1, canvas_h - 2)
            tw = 0.5 + 0.5 * math.sin(t * st.speed + st.phase)
            idx = sy * cur_w + sx
            if st.is_heart and tw > 0.65:
                char_buf[idx] = heart_sym
                col_buf[idx] = sample_stops(pal["heart"], 0.75, eff_16, "\033[95m")
            elif tw > 0.78:
                char_buf[idx] = "+"
                col_buf[idx] = star_col_bright
            elif tw > 0.35:
                char_buf[idx] = "."
                col_buf[idx] = star_col_dim

        # -------------------------------------------------------------------
        # Act 4: Grand Celebration Finale ([Y] Pressed)
        # -------------------------------------------------------------------
        if self.accepted:
            if not self.fireworks:
                fw0 = CelebrationFirework(cur_w, canvas_h)
                fw0.x = cur_w * 0.32
                fw0.y = canvas_h * 0.32
                fw0.is_heart = True
                fw0.explode(cur_w, canvas_h)
                fw1 = CelebrationFirework(cur_w, canvas_h)
                fw1.x = cur_w * 0.68
                fw1.y = canvas_h * 0.32
                fw1.is_heart = True
                fw1.explode(cur_w, canvas_h)
                self.fireworks.extend([fw0, fw1])

            if self.sim_time >= self.next_fw and len(self.fireworks) < 6:
                self.fireworks.append(CelebrationFirework(cur_w, canvas_h))
                self.next_fw = self.sim_time + random.uniform(0.35, 0.75)

            for fw in self.fireworks:
                fw.update(raw_dt, cur_w, canvas_h)
            self.fireworks = [fw for fw in self.fireworks if not fw.done()]

            for fw in self.fireworks:
                if not fw.exploded:
                    fx, fy = int(fw.x), int(fw.y)
                    if 0 <= fx < cur_w and 0 <= fy < canvas_h:
                        idx = fy * cur_w + fx
                        char_buf[idx] = "^"
                        col_buf[idx] = star_col_bright
                else:
                    for sp in fw.sparks:
                        sx, sy = int(sp.x), int(sp.y)
                        if 0 <= sx < cur_w and 0 <= sy < canvas_h:
                            lr = sp.life / sp.max_life
                            idx = sy * cur_w + sx
                            char_buf[idx] = "." if lr < 0.25 else (heart_sym if not sp.gold else "*")
                            if sp.gold:
                                col_buf[idx] = sample_stops(pal["band"], lr, eff_16, "\033[93m")
                            else:
                                col_buf[idx] = sample_stops(pal["heart"], min(1.0, sp.tint * (0.35 + 0.65 * lr)), eff_16, "\033[91m")

            # Pulsing celebration heart outline in center
            phase = (t % 1.2) / 1.2
            boost = 0.14 * math.exp(-((phase - 0.15) / 0.06) ** 2)
            cy = canvas_h * 0.44
            cx = cur_w * 0.5
            sy_scale = min(canvas_h * 0.30, cur_w / 5.4) * (1.0 + boost)
            sx_scale = sy_scale * 2.05
            for py in range(canvas_h):
                ny = (cy - py) / sy_scale + 0.1
                for px in range(cur_w):
                    nx = (px - cx) / sx_scale
                    if -1.4 < nx < 1.4 and -1.2 < ny < 1.4:
                        u = nx * nx + ny * ny - 1.0
                        f = u * u * u - nx * nx * (ny ** 3)
                        if -0.20 < f <= 0.0:
                            idx = py * cur_w + px
                            char_buf[idx] = heart_sym if f > -0.09 else "*"
                            col_buf[idx] = sample_stops(pal["heart"], 0.65 + boost * 2.0, eff_16, "\033[91m")

            yes_banner = f" {decor}  SHE SAID YES!  {decor} "
            sub_banner = f" {decor}  {self.yes_msg}  {decor} "
            self._draw_text(
                char_buf, col_buf, cur_w, canvas_h, int(cy) - 1, yes_banner,
                lambda i, n: sample_stops(pal["text"], 0.5 + 0.5 * math.sin(t * 5.0 - i * 0.3), eff_16, "\033[97m"),
            )
            self._draw_text(
                char_buf, col_buf, cur_w, canvas_h, int(cy) + 1, sub_banner,
                lambda i, n: sample_stops(pal["band"], 0.5 + 0.5 * math.cos(t * 4.0 - i * 0.25), eff_16, "\033[93m"),
            )

        # -------------------------------------------------------------------
        # Act 1: Starry Night + Typewriter Intro (0.0s .. 4.2s)
        # -------------------------------------------------------------------
        elif t < 4.2:
            line1 = f"Hey {self.name}..." if self.name else "Hey there..."
            line2 = "I've been meaning to ask you something..."
            shown1 = line1[: max(0, int(t * 14))]
            shown2 = line2[: max(0, int((t - 1.3) * 18))] if t > 1.3 else ""

            mid_y = canvas_h // 2
            self._draw_text(
                char_buf, col_buf, cur_w, canvas_h, mid_y - 1, shown1,
                lambda i, n: sample_stops(pal["text"], 0.65 + 0.35 * math.sin(t * 3.0 - i * 0.2), eff_16, "\033[95m"),
            )
            self._draw_text(
                char_buf, col_buf, cur_w, canvas_h, mid_y + 1, shown2,
                lambda i, n: sample_stops(pal["text"], 0.55 + 0.45 * math.sin(t * 3.5 - i * 0.2), eff_16, "\033[97m"),
            )

        # -------------------------------------------------------------------
        # Act 2 & Act 3: Ring Box -> Rising Sparkling Diamond -> Proposal Heart
        # -------------------------------------------------------------------
        else:
            # Progress of box opening / ring rising (4.2s .. 7.8s)
            rise = min(1.0, max(0.0, (t - 4.2) / 2.6))
            ease = 1.0 - (1.0 - rise) ** 3  # smooth cubic ease-out

            # Once ring has risen (t >= 7.2s), fade in the glowing beating heart frame!
            heart_alpha = min(1.0, max(0.0, (t - 7.0) / 1.5))
            cy = canvas_h * 0.44
            cx = cur_w * 0.5

            if heart_alpha > 0.05:
                phase = (t % 1.35) / 1.35
                boost = 0.10 * math.exp(-((phase - 0.12) / 0.045) ** 2) + 0.18 * math.exp(-((phase - 0.28) / 0.055) ** 2)
                sy_scale = min(canvas_h * 0.37, cur_w / 4.8) * (1.0 + boost)
                sx_scale = sy_scale * 2.08
                for py in range(canvas_h):
                    ny = (cy - py) / sy_scale + 0.12
                    row_off = py * cur_w
                    for px in range(cur_w):
                        nx = (px - cx) / sx_scale
                        if -1.4 < nx < 1.4 and -1.2 < ny < 1.4:
                            u = nx * nx + ny * ny - 1.0
                            f = u * u * u - nx * nx * (ny ** 3)
                            # Draw luminous heart silhouette rim around the ring
                            if -0.26 < f <= 0.0:
                                idx = row_off + px
                                lum = min(1.0, (0.45 + boost * 2.0) * heart_alpha)
                                char_buf[idx] = heart_sym if f > -0.10 else ":"
                                col_buf[idx] = sample_stops(pal["heart"], lum, eff_16, "\033[91m")

            # Draw Velvet Ring Box base at bottom of ring area before heart fully takes over
            if t < 8.2:
                box_y = int(cy) + 5
                box_art = [
                    "   .---------------.   ",
                    "  /  *   RING    *  \\  ",
                    "  |_________________|  ",
                ]
                for bi, bline in enumerate(box_art):
                    self._draw_text(
                        char_buf, col_buf, cur_w, canvas_h, box_y + bi, bline,
                        lambda i, n: sample_stops(pal["heart"], 0.35, eff_16, "\033[31m"),
                    )

            # Draw Sparkling Diamond Ring rising smoothly into center
            ring_top = int(cy - 5 + (1.0 - ease) * 4)
            visible_rows = max(3, int(len(RING_ART) * (0.35 + 0.65 * ease)))
            for ri in range(min(visible_rows, len(RING_ART))):
                rline, kind = RING_ART[ri]
                row_y = ring_top + ri
                if kind == "diamond":
                    self._draw_text(
                        char_buf, col_buf, cur_w, canvas_h, row_y, rline,
                        lambda i, n, r_idx=ri: sample_stops(
                            pal["diamond"],
                            0.45 + 0.55 * abs(math.sin(t * 4.5 + i * 0.4 + r_idx)),
                            eff_16,
                            "\033[96m",
                        ),
                    )
                else:
                    self._draw_text(
                        char_buf, col_buf, cur_w, canvas_h, row_y, rline,
                        lambda i, n, r_idx=ri: sample_stops(
                            pal["band"],
                            0.4 + 0.6 * abs(math.sin(t * 2.5 + i * 0.25 + r_idx * 0.3)),
                            eff_16,
                            "\033[93m",
                        ),
                    )

            # Orbiting diamond glints around the crown
            for g in range(4):
                ang = t * 2.4 + g * (math.pi * 0.5)
                gx = int(cx + math.cos(ang) * 10.5)
                gy = int(ring_top + 1 + math.sin(ang) * 2.2)
                if 0 <= gx < cur_w and 0 <= gy < canvas_h:
                    if math.sin(t * 7.0 + g * 1.7) > 0.1:
                        idx = gy * cur_w + gx
                        char_buf[idx] = "*" if g % 2 == 0 else "+"
                        col_buf[idx] = star_col_bright

            # The Big Proposal Question + Interactive Prompt
            if t >= 7.6:
                q_row = min(canvas_h - 3, int(cy) + 7)
                q_text = f" {decor}  {self.question}  {decor} "
                self._draw_text(
                    char_buf, col_buf, cur_w, canvas_h, q_row, q_text,
                    lambda i, n: sample_stops(pal["text"], 0.5 + 0.5 * math.sin(t * 4.0 - i * 0.3), eff_16, "\033[97m"),
                )

                if not self.loop_stream and not self.auto_yes:
                    if t < self.no_nudge_until:
                        nudges = [
                            "Nice try! Look at that diamond sparkle -> Press [Y]!",
                            "My heart only accepts [Y]! Press [Y] for Yes!",
                            f"Pretty please{', ' + self.name if self.name else ''}? Press [Y]!",
                        ]
                        prompt_text = nudges[(self.no_clicks - 1) % len(nudges)]
                    else:
                        prompt_text = "[Y] Yes!   |   [N] Wait..."
                    self._draw_text(
                        char_buf, col_buf, cur_w, canvas_h, min(canvas_h - 1, q_row + 2), prompt_text,
                        lambda i, n: quant_ansi((255, 225, 140), eff_16, "\033[93m"),
                    )

        # Build atomic frame with run-length ANSI color compression
        out_lines = ["\033[H"]
        for y in range(canvas_h):
            row_off = y * cur_w
            parts = []
            last_col = None
            for x in range(cur_w):
                idx = row_off + x
                ch = char_buf[idx]
                if ch == " ":
                    if last_col is not None:
                        parts.append("\033[0m")
                        last_col = None
                    parts.append(" ")
                else:
                    col = col_buf[idx]
                    if col != last_col:
                        parts.append(col)
                        last_col = col
                    parts.append(ch)
            if last_col is not None:
                parts.append("\033[0m")
            out_lines.append("".join(parts))

        if self.include_hud:
            hud_plain = (
                f" [Y] Yes! | [C] {cur_theme.upper()} | [A] {'ASCII' if self.ascii_only else 'HEART'} | "
                f"[R] Replay | [Q] Quit"
            )
            out_lines.append(f"\033[90m{hud_plain[:cur_w].ljust(cur_w)}\033[0m")

        return "\n".join(out_lines) + "\n"


# ---------------------------------------------------------------------------
# Local Runner & Built-in HTTP Streaming Server (--serve)
# ---------------------------------------------------------------------------

def run_local(args, kb_state):
    gen = ProposalGenerator(
        name=args.name,
        question=args.question,
        yes_msg=args.yes_msg,
        theme=args.theme,
        ascii_only=args.ascii,
        use_16color=args.use_16color,
        auto_yes=args.auto_yes,
        loop_stream=False,
        include_hud=True,
        initial_w=args.width,
        initial_h=args.height,
    )

    sys.stdout.write("\033[?25l\033[2J")
    sys.stdout.flush()

    last_tick = time.perf_counter()
    interval = 1.0 / max(5, args.fps)
    frames_done = 0

    while True:
        cycle_start = time.perf_counter()
        raw_dt = min(0.1, cycle_start - last_tick)
        last_tick = cycle_start

        frames_done += 1
        if args.frames > 0 and frames_done > args.frames:
            break

        key = check_keypress(kb_state)
        if key:
            if key in ("q", "\x03"):
                break
            elif key in ("y", "\r", "\n"):
                gen.trigger_yes()
            elif key == "n" and not gen.accepted:
                gen.trigger_no()
            elif key == "c":
                gen.theme_idx = (gen.theme_idx + 1) % len(THEMES)
            elif key == "a":
                gen.ascii_only = not gen.ascii_only
            elif key == "r":
                gen.replay()

        if not args.no_resize:
            cols, rows = shutil.get_terminal_size((80, 24))
            cur_w = max(48, cols - 1)
            cur_h = max(18, rows - 2)
        else:
            cur_w = max(48, args.width - 1)
            cur_h = max(18, args.height - 2)

        sys.stdout.write(gen.render_frame(raw_dt, cur_w, cur_h))
        sys.stdout.flush()

        elapsed = time.perf_counter() - cycle_start
        sleep_s = interval - elapsed
        if sleep_s > 0:
            time.sleep(sleep_s)


class ThreadingProposalServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class ProposalStreamHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "ProposalLive/1.0"

    def log_message(self, format, *args):
        sys.stderr.write(f"[{self.log_date_time_string()}] {self.address_string()} {format % args}\n")

    def _send_bytes(self, status: int, content_type: str, body: bytes):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()

    def _send_chunk(self, data: bytes):
        if data:
            self.wfile.write(f"{len(data):x}\r\n".encode("ascii") + data + b"\r\n")
            self.wfile.flush()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.strip("/").lower()
        params = parse_qs(parsed.query, keep_blank_values=True)

        if path == "health":
            self._send_bytes(200, "application/json; charset=utf-8", json.dumps({"status": "ok"}).encode("utf-8"))
            return

        host_header = self.headers.get("Host", "localhost:8080")
        qs_suffix = f"?{parsed.query}" if parsed.query else ""

        if path == "ps":
            self._send_bytes(200, "text/plain; charset=utf-8", f'& curl.exe -sN "http://{host_header}/{qs_suffix}"\n'.encode("utf-8"))
            return

        ua = self.headers.get("User-Agent", "").lower()
        raw_override = params.get("raw", ["0"])[0] == "1" or "frames" in params
        if not raw_override and "windowspowershell" in ua:
            hint = (
                f"\n  In PowerShell 5.1, use curl.exe instead of curl:\n"
                f'    curl.exe -sN "http://{host_header}/{qs_suffix}"\n'
                f'    irm "http://{host_header}/ps{qs_suffix}" | iex\n\n'
            ).encode("utf-8")
            self._send_bytes(200, "text/plain; charset=utf-8", hint)
            return

        if not raw_override and "mozilla" in ua and "curl" not in ua and "wget" not in ua:
            safe = html.escape(host_header)
            page = f"<html><body style='background:#120911;color:#ffd9e6;font-family:Consolas,monospace;padding:40px'><h2>Terminal Proposal Animation</h2><p>CMD: <code>curl -sN http://{safe}/</code></p><p>PowerShell: <code>curl.exe -sN http://{safe}/</code></p></body></html>".encode("utf-8")
            self._send_bytes(200, "text/html; charset=utf-8", page)
            return

        name = params.get("name", [""])[0]
        question = params.get("q", params.get("question", ["WILL YOU MARRY ME?"]))[0]
        yes_msg = params.get("yes", ["FOREVER & ALWAYS!"])[0]
        theme = params.get("theme", ["rose"])[0].lower()
        use_utf8 = params.get("utf8", ["0"])[0] in ("1", "true", "yes")
        use_16 = params.get("color", [""])[0] == "16"
        max_frames = int(params.get("frames", ["0"])[0] or 0)
        fps = max(5, min(30, int(params.get("fps", ["20"])[0] or 20)))

        gen = ProposalGenerator(
            name=name,
            question=question,
            yes_msg=yes_msg,
            theme=theme if theme in THEMES else "rose",
            ascii_only=not use_utf8,
            use_16color=use_16,
            loop_stream=True,
            include_hud=False,
            initial_w=78,
            initial_h=22,
        )

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8" if use_utf8 else "text/plain; charset=ascii")
        self.send_header("Transfer-Encoding", "chunked")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("X-Accel-Buffering", "no")
        self.send_header("Connection", "close")
        self.end_headers()

        encoding = "utf-8" if use_utf8 else "ascii"
        interval = 1.0 / fps
        last_tick = time.perf_counter()
        n = 0
        try:
            self._send_chunk(b"\033[2J\033[H")
            while True:
                t0 = time.perf_counter()
                dt = min(0.1, t0 - last_tick)
                last_tick = t0
                n += 1
                if max_frames > 0 and n > max_frames:
                    break
                self._send_chunk(gen.render_frame(dt, 78, 22).encode(encoding, errors="replace"))
                sl = interval - (time.perf_counter() - t0)
                if sl > 0:
                    time.sleep(sl)
            self._send_chunk(b"\033[0m\n")
            self.wfile.write(b"0\r\n\r\n")
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
            pass


def serve_proposal(host: str, port: int):
    httpd = ThreadingProposalServer((host, port), ProposalStreamHandler)
    signal.signal(signal.SIGINT, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    disp = "localhost" if host == "0.0.0.0" else host
    print(f"Proposal curl server listening on http://{disp}:{port}")
    print(f"  CMD        : curl -sN http://{disp}:{port}/")
    print(f"  PowerShell : curl.exe -sN http://{disp}:{port}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        httpd.server_close()


def main():
    parser = argparse.ArgumentParser(
        description="Single-file Terminal Proposal Animation (CMD, PowerShell & GitHub curl ready)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--name", "-n", default="", help="Recipient name for personalized intro")
    parser.add_argument("--question", "-q", default="WILL YOU MARRY ME?", help="Proposal question text")
    parser.add_argument("--yes-msg", default="FOREVER & ALWAYS!", help="Celebration message after YES")
    parser.add_argument("--theme", "-t", choices=THEMES, default="rose", help="Color theme")
    parser.add_argument("--fps", "-f", type=int, default=30, help="Target FPS")
    parser.add_argument("--ascii", action="store_true", help="Force strict 7-bit ASCII characters")
    parser.add_argument("--16color", dest="use_16color", action="store_true", help="Force 16-color ANSI palette")
    parser.add_argument("--auto-yes", action="store_true", help="Automatically trigger celebration finale")
    parser.add_argument("--width", "-w", type=int, default=80, help="Fixed width when --no-resize is used")
    parser.add_argument("--height", type=int, default=24, help="Fixed height when --no-resize is used")
    parser.add_argument("--no-resize", action="store_true", help="Disable terminal auto-resize")
    parser.add_argument("--frames", type=int, default=0, help="Exit after N frames (useful for testing)")
    parser.add_argument("--serve", action="store_true", help="Start curl-streamable HTTP server")
    parser.add_argument("--host", default="0.0.0.0", help="Host interface for --serve")
    parser.add_argument("--port", "-p", type=int, default=int(os.environ.get("PORT", "8080")), help="Port for --serve")

    args = parser.parse_args()
    if args.serve:
        serve_proposal(args.host, args.port)
        return

    kb_state = setup_keyboard()
    try:
        with WindowsConsoleGuard(use_utf8=not args.ascii):
            run_local(args, kb_state)
    except KeyboardInterrupt:
        pass
    finally:
        restore_keyboard(kb_state)
        print("Proposal animation ended cleanly.")


if __name__ == "__main__":
    main()
