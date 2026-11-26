#!/usr/bin/env python3
"""
Our Story - Single-File Terminal Animation (CMD, PowerShell & GitHub curl Ready)
================================================================================
A zero-dependency, pure-Python 5-chapter animated love story:
  Chapter 1: College 1st Year (The First Meeting & Teeth Aligner)
  Chapter 2: Endless Conversations -> Best Friends
  Chapter 3: The Hackathon Night (Falling in Love)
  Chapter 4: 3 Days Later (The Car Proposal)
  Chapter 5: The Hug & Commitment Finale (Heart Fireworks)

Runs:
  - Directly from GitHub via `curl -sL <RAW_URL> | python -` (CMD & PowerShell)
  - Locally in Windows Command Prompt (cmd.exe), PowerShell 5.1/7+, and Unix
  - As a live HTTP chunked stream via `python story.py --serve`
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

THEMES = ["romantic", "hackathon", "sunset", "classic"]

PALETTES = {
    "romantic": {
        "heart": [(125, 18, 65), (215, 45, 115), (255, 115, 175), (255, 225, 240)],
        "accent": (140, 235, 255),
        "gold": (255, 215, 120),
        "text": [(255, 165, 205), (255, 245, 250)],
        "dim": (165, 130, 185),
    },
    "hackathon": {
        "heart": [(95, 25, 135), (195, 40, 175), (255, 85, 210), (160, 250, 255)],
        "accent": (105, 255, 175),
        "gold": (255, 220, 130),
        "text": [(155, 235, 255), (255, 195, 245)],
        "dim": (135, 155, 215),
    },
    "sunset": {
        "heart": [(145, 25, 25), (235, 75, 55), (255, 155, 90), (255, 240, 195)],
        "accent": (255, 210, 135),
        "gold": (255, 235, 145),
        "text": [(255, 190, 125), (255, 245, 220)],
        "dim": (205, 150, 135),
    },
}


def lerp_rgb(c1, c2, t: float):
    t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


def quant_ansi(rgb, use_16: bool = False, fallback: str = "\033[95m") -> str:
    if use_16:
        return fallback
    return f"\033[38;2;{(rgb[0] // 8) * 8};{(rgb[1] // 8) * 8};{(rgb[2] // 8) * 8}m"


def sample_stops(stops, t: float, use_16: bool = False, fallback: str = "\033[91m") -> str:
    if use_16:
        if t > 0.8:
            return "\033[97m"
        elif t > 0.5:
            return "\033[95m"
        elif t > 0.25:
            return fallback
        return "\033[31m"
    v = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
    scaled = v * (len(stops) - 1)
    idx = int(scaled)
    rgb = stops[-1] if idx >= len(stops) - 1 else lerp_rgb(stops[idx], stops[idx + 1], scaled - idx)
    return quant_ansi(rgb)


# ---------------------------------------------------------------------------
# Particle Helpers (Stars, Chat/Code Sparks, Finale Fireworks)
# ---------------------------------------------------------------------------

class Star:
    def __init__(self, w: int, h: int):
        self.x = random.randint(1, max(2, w - 2))
        self.y = random.randint(1, max(2, h - 3))
        self.phase = random.uniform(0.0, math.tau)
        self.speed = random.uniform(1.6, 4.0)


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


class HeartFirework:
    def __init__(self, w: int, h: int):
        self.x = random.uniform(w * 0.18, w * 0.82)
        self.y = float(h - 2)
        self.target_y = random.uniform(h * 0.16, h * 0.40)
        self.vy = -random.uniform(22.0, 30.0)
        self.vx = random.uniform(-2.2, 2.2)
        self.exploded = False
        self.sparks = []

    def explode(self, w: int, h: int):
        self.exploded = True
        scale = min(w * 0.042, h * 0.085)
        for i in range(48):
            t = (i / 48.0) * math.tau
            hx = 16.0 * (math.sin(t) ** 3)
            hy = -(13.0 * math.cos(t) - 5.0 * math.cos(2 * t) - 2.0 * math.cos(3 * t) - math.cos(4 * t))
            rx = hx * 0.26 * scale * 2.0
            ry = hy * 0.26 * scale
            jit = random.uniform(0.88, 1.12)
            self.sparks.append(
                FireworkSpark(self.x, self.y, rx * jit, ry * jit, random.uniform(1.1, 1.7), random.uniform(0.4, 1.0), i % 4 == 0)
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
# 5-Chapter Story Animator
# ---------------------------------------------------------------------------

CHAPTER_STARTS = [0.0, 6.5, 12.5, 18.5, 24.5]
TOTAL_LOOP_TIME = 34.0


class StoryGenerator:
    """Renders the 5-chapter love story from college 1st year to commitment."""

    def __init__(
        self,
        his_name: str = "",
        her_name: str = "",
        theme: str = "romantic",
        ascii_only: bool = False,
        use_16color: bool = False,
        include_hud: bool = True,
        loop: bool = True,
        initial_w: int = 78,
        initial_h: int = 22,
    ):
        self.his_name = his_name.strip()
        self.her_name = her_name.strip()
        self.theme_idx = THEMES.index(theme) if theme in THEMES else 0
        self.ascii_only = ascii_only
        self.use_16color = use_16color
        self.include_hud = include_hud
        self.loop = loop

        self.paused = False
        self.speed_mult = 1.0
        self.sim_time = 0.0
        self.stars = [Star(initial_w, initial_h) for _ in range(32)]
        self.fireworks = []
        self.next_fw = 0.0

    def current_chapter(self) -> int:
        t = self.sim_time % TOTAL_LOOP_TIME if self.loop else self.sim_time
        for idx in range(len(CHAPTER_STARTS) - 1, -1, -1):
            if t >= CHAPTER_STARTS[idx]:
                return idx
        return 0

    def jump_chapter(self, delta: int):
        ch = self.current_chapter()
        target = (ch + delta) % len(CHAPTER_STARTS)
        self.sim_time = CHAPTER_STARTS[target]
        self.fireworks = []
        self.next_fw = self.sim_time

    def replay(self):
        self.sim_time = 0.0
        self.fireworks = []
        self.next_fw = 0.0

    def _draw_str(self, char_buf, col_buf, cur_w: int, canvas_h: int, row: int, col_x: int, text: str, ansi: str):
        if not (0 <= row < canvas_h):
            return
        row_off = row * cur_w
        for i, ch in enumerate(text):
            tx = col_x + i
            if 0 <= tx < cur_w and ch != " ":
                char_buf[row_off + tx] = ch
                col_buf[row_off + tx] = ansi

    def _draw_centered(self, char_buf, col_buf, cur_w: int, canvas_h: int, row: int, text: str, col_fn):
        if not (0 <= row < canvas_h) or not text:
            return
        sx = max(0, (cur_w - len(text)) // 2)
        row_off = row * cur_w
        for i, ch in enumerate(text):
            tx = sx + i
            if 0 <= tx < cur_w and ch != " ":
                char_buf[row_off + tx] = ch
                col_buf[row_off + tx] = col_fn(i, len(text))

    def render_frame(self, raw_dt: float, cur_w: int, cur_h: int) -> str:
        if not self.paused:
            self.sim_time += raw_dt * self.speed_mult

        t = (self.sim_time % TOTAL_LOOP_TIME) if self.loop else min(self.sim_time, TOTAL_LOOP_TIME - 0.01)
        if self.loop and t < 0.2 and self.fireworks:
            self.fireworks = []

        cur_theme = THEMES[self.theme_idx]
        eff_16 = self.use_16color or (cur_theme == "classic")
        pal = PALETTES.get(cur_theme, PALETTES["romantic"])

        canvas_h = max(16, cur_h - (1 if self.include_hud else 0))
        size = cur_w * canvas_h
        char_buf = [" "] * size
        col_buf = [""] * size

        heart_sym = "*" if self.ascii_only else "\u2665"
        decor = "<3" if self.ascii_only else "\u2665"

        col_white = quant_ansi((255, 255, 255), eff_16, "\033[97m")
        col_dim = quant_ansi(pal["dim"], eff_16, "\033[35m")
        col_accent = quant_ansi(pal["accent"], eff_16, "\033[96m")
        col_gold = quant_ansi(pal["gold"], eff_16, "\033[93m")
        col_pink = sample_stops(pal["heart"], 0.72, eff_16, "\033[95m")

        # Background stars
        for st in self.stars:
            sx = st.x % cur_w
            sy = st.y % max(2, canvas_h - 3)
            tw = 0.5 + 0.5 * math.sin(t * st.speed + st.phase)
            idx = sy * cur_w + sx
            if tw > 0.78:
                char_buf[idx] = "+"
                col_buf[idx] = col_white
            elif tw > 0.35:
                char_buf[idx] = "."
                col_buf[idx] = col_dim

        cx = cur_w // 2
        cy = canvas_h // 2

        # -------------------------------------------------------------------
        # Scene 1: College 1st Year & The Teeth Aligner (0.0s .. 6.5s)
        # -------------------------------------------------------------------
        if t < CHAPTER_STARTS[1]:
            local_t = t

            # Campus gate silhouette on left
            campus = [
                "   _[COLLEGE]_   ",
                "  | [] [] []  |  ",
                "  |____|_|____|  ",
            ]
            for ri, line in enumerate(campus):
                self._draw_str(char_buf, col_buf, cur_w, canvas_h, cy - 1 + ri, max(1, cx - 32), line, col_dim)

            # Two characters facing each other
            her_x = cx + 4
            his_x = cx - 10
            his_face = "(^_^)" if local_t > 4.8 else "(o_o)"
            her_face = "(^o^)" if local_t > 4.8 else "(?_?)"

            self._draw_str(char_buf, col_buf, cur_w, canvas_h, cy - 1, his_x, his_face, col_accent)
            self._draw_str(char_buf, col_buf, cur_w, canvas_h, cy,     his_x, "/| |\\", col_accent)
            self._draw_str(char_buf, col_buf, cur_w, canvas_h, cy + 1, his_x, " / \\ ", col_accent)

            self._draw_str(char_buf, col_buf, cur_w, canvas_h, cy - 1, her_x, her_face, col_pink)
            self._draw_str(char_buf, col_buf, cur_w, canvas_h, cy,     her_x, "/| |\\", col_pink)
            self._draw_str(char_buf, col_buf, cur_w, canvas_h, cy + 1, her_x, " / \\ ", col_pink)

            if 1.0 <= local_t < 3.6:
                msg = '"Eda, entha nee chirikathe?"'
                self._draw_str(char_buf, col_buf, cur_w, canvas_h, cy - 4, max(2, her_x - 10), msg[: int((local_t - 1.0) * 18)], col_pink)
            elif local_t >= 3.2:
                msg2 = '"Athenik teeth aligner ullondaa..."'
                self._draw_str(char_buf, col_buf, cur_w, canvas_h, cy - 4, max(2, his_x - 12), msg2[: int((local_t - 3.2) * 20)], col_accent)

            if local_t > 4.8:
                self._draw_str(char_buf, col_buf, cur_w, canvas_h, cy - 2, his_x + 2, "*", col_gold)
                self._draw_centered(
                    char_buf, col_buf, cur_w, canvas_h, canvas_h - 3,
                    "First year-il angane nammal parichayapettu...",
                    lambda i, n: sample_stops(pal["text"], 0.6 + 0.4 * math.sin(t * 3 - i * 0.2), eff_16),
                )

        # -------------------------------------------------------------------
        # Scene 2: Endless Conversations -> Best Friends (6.5s .. 12.5s)
        # -------------------------------------------------------------------
        elif t < CHAPTER_STARTS[2]:
            local_t = t - CHAPTER_STARTS[1]

            # Characters closer together now
            his_x = cx - 9
            her_x = cx + 4
            self._draw_str(char_buf, col_buf, cur_w, canvas_h, cy,     his_x, "(^_^)", col_accent)
            self._draw_str(char_buf, col_buf, cur_w, canvas_h, cy + 1, his_x, "/| |\\", col_accent)
            self._draw_str(char_buf, col_buf, cur_w, canvas_h, cy + 2, his_x, " / \\ ", col_accent)

            self._draw_str(char_buf, col_buf, cur_w, canvas_h, cy,     her_x, "(^_^)", col_pink)
            self._draw_str(char_buf, col_buf, cur_w, canvas_h, cy + 1, her_x, "/| |\\", col_pink)
            self._draw_str(char_buf, col_buf, cur_w, canvas_h, cy + 2, her_x, " / \\ ", col_pink)

            # Floating Manglish chat bubbles rising between them
            chats = [
                (0.2, -14, "[ daa evideya? ]"),
                (1.1, 4,   "[ hahaha pwoli! ]"),
                (2.0, -13, "[ pinne entha? ]"),
                (2.9, 3,   "[ miss u da ]"),
                (3.8, -6,  "[ besties! ]"),
            ]
            for start_c, dx, bubble in chats:
                if local_t >= start_c:
                    rise_y = int(cy - 2 - (local_t - start_c) * 1.4)
                    if 2 <= rise_y < cy:
                        col_b = col_pink if dx > 0 else col_accent
                        self._draw_str(char_buf, col_buf, cur_w, canvas_h, rise_y, cx + dx, bubble, col_b)

            self._draw_centered(
                char_buf, col_buf, cur_w, canvas_h, canvas_h - 3,
                f"{decor}  Kuree samsarichu... nammal best friends aayi!  {decor}",
                lambda i, n: sample_stops(pal["text"], 0.55 + 0.45 * math.sin(t * 3.5 - i * 0.25), eff_16),
            )

        # -------------------------------------------------------------------
        # Scene 3: The Hackathon Night -> Falling in Love (12.5s .. 18.5s)
        # -------------------------------------------------------------------
        elif t < CHAPTER_STARTS[3]:
            local_t = t - CHAPTER_STARTS[2]

            # Two glowing laptops + coffee cup
            desk = [
                ("   .-------.     c[_]     .-------.   ", col_accent),
                ("  | { }  01 |            | <3  git |  ", col_white),
                ("  |_________|            |_________|  ", col_accent),
                (" /___________\\          /___________\\ ", col_dim),
            ]
            for ri, (line, c_col) in enumerate(desk):
                self._draw_centered(char_buf, col_buf, cur_w, canvas_h, cy - 1 + ri, line, lambda i, n, col=c_col: col)

            # Rising code sparks & hearts converging above laptops
            tokens = ["{ }", "01", "git", heart_sym, "<3", "++"]
            for k in range(6):
                prog = (local_t * 0.7 + k * 0.35) % 2.4
                ry = int(cy - 2 - prog * 2.3)
                rx = int(cx + math.sin(local_t * 2.5 + k * 1.3) * (8 - prog * 2.2))
                if 2 <= ry < cy - 1 and 1 <= rx < cur_w - 4:
                    tok = tokens[k % len(tokens)]
                    self._draw_str(char_buf, col_buf, cur_w, canvas_h, ry, rx, tok, col_pink if k % 2 == 0 else col_accent)

            if local_t > 2.2:
                pulse = 0.6 + 0.4 * math.sin(local_t * 5.0)
                self._draw_centered(
                    char_buf, col_buf, cur_w, canvas_h, cy - 4,
                    f"{decor}  {decor}  {decor}",
                    lambda i, n, p=pulse: sample_stops(pal["heart"], p, eff_16),
                )

            self._draw_centered(
                char_buf, col_buf, cur_w, canvas_h, canvas_h - 3,
                f"{decor}  Aa hackathon rathri... nammal ishtathil aayi  {decor}",
                lambda i, n: sample_stops(pal["text"], 0.55 + 0.45 * math.sin(t * 4 - i * 0.25), eff_16),
            )

        # -------------------------------------------------------------------
        # Scene 4: 3 Days Later -> Proposal in the Car (18.5s .. 24.5s)
        # -------------------------------------------------------------------
        elif t < CHAPTER_STARTS[4]:
            local_t = t - CHAPTER_STARTS[3]

            # Car gently gliding in from left during first 1.5s
            glide = min(1.0, local_t / 1.4)
            ease = 1.0 - (1.0 - glide) ** 3
            car_x = int((cx - 18) * ease + 2 * (1.0 - ease))

            car_art = [
                ("       ______--------______        ", col_accent),
                ("     //  (^_^)      (^_^)  \\\\      ", col_pink),
                ("  __//______________________\\\\___  ", col_accent),
                (" |    _                    _     | ", col_accent),
                (" '--=(O)------------------(O)=---' ", col_white),
            ]
            for ri, (line, c_col) in enumerate(car_art):
                self._draw_str(char_buf, col_buf, cur_w, canvas_h, cy - 1 + ri, car_x, line, c_col)

            # Warm headlight beams
            beam_len = 7 if math.sin(t * 8) > -0.8 else 5
            self._draw_str(char_buf, col_buf, cur_w, canvas_h, cy + 2, car_x + 35, "=" * beam_len + "*", col_gold)

            # Floating proposal line above the car
            if local_t > 1.6:
                float_y = cy - 4 - int(0.5 + 0.5 * math.sin(local_t * 3.0))
                self._draw_centered(
                    char_buf, col_buf, cur_w, canvas_h, float_y,
                    f"{decor}  Ninte koode jeevikkanam... Will you be mine?  {decor}",
                    lambda i, n: sample_stops(pal["heart"], 0.65 + 0.35 * math.sin(t * 5 - i * 0.3), eff_16),
                )

            self._draw_centered(
                char_buf, col_buf, cur_w, canvas_h, canvas_h - 3,
                "3 divasam kazhinju, ente car-il vechu njan propose cheythu...",
                lambda i, n: sample_stops(pal["text"], 0.6 + 0.4 * math.sin(t * 3.5 - i * 0.2), eff_16),
            )

        # -------------------------------------------------------------------
        # Scene 5: The Hug & Committed Forever Finale (24.5s .. 34.0s)
        # -------------------------------------------------------------------
        else:
            local_t = t - CHAPTER_STARTS[4]

            if not self.fireworks:
                fw0 = HeartFirework(cur_w, canvas_h)
                fw0.x = cur_w * 0.28
                fw0.y = canvas_h * 0.30
                fw0.explode(cur_w, canvas_h)
                fw1 = HeartFirework(cur_w, canvas_h)
                fw1.x = cur_w * 0.72
                fw1.y = canvas_h * 0.30
                fw1.explode(cur_w, canvas_h)
                self.fireworks.extend([fw0, fw1])

            if not self.paused:
                if self.sim_time >= self.next_fw and len(self.fireworks) < 5:
                    self.fireworks.append(HeartFirework(cur_w, canvas_h))
                    self.next_fw = self.sim_time + random.uniform(0.45, 0.90)
                for fw in self.fireworks:
                    fw.update(raw_dt * self.speed_mult, cur_w, canvas_h)
                self.fireworks = [fw for fw in self.fireworks if not fw.done()]

            for fw in self.fireworks:
                if not fw.exploded:
                    fx, fy = int(fw.x), int(fw.y)
                    if 0 <= fx < cur_w and 0 <= fy < canvas_h:
                        idx = fy * cur_w + fx
                        char_buf[idx] = "^"
                        col_buf[idx] = col_white
                else:
                    for sp in fw.sparks:
                        sx, sy = int(sp.x), int(sp.y)
                        if 0 <= sx < cur_w and 0 <= sy < canvas_h:
                            lr = sp.life / sp.max_life
                            idx = sy * cur_w + sx
                            char_buf[idx] = "." if lr < 0.25 else (heart_sym if not sp.gold else "*")
                            col_buf[idx] = col_gold if sp.gold else sample_stops(pal["heart"], min(1.0, sp.tint * (0.35 + 0.65 * lr)), eff_16)

            # Pulsing heart frame around the hugging couple
            phase = (local_t % 1.2) / 1.2
            boost = 0.14 * math.exp(-((phase - 0.15) / 0.06) ** 2)
            sy_s = min(canvas_h * 0.34, cur_w / 5.2) * (1.0 + boost)
            sx_s = sy_s * 2.05
            for py in range(canvas_h):
                ny = (cy - py) / sy_s + 0.12
                row_off = py * cur_w
                for px in range(cur_w):
                    nx = (px - cx) / sx_s
                    if -1.4 < nx < 1.4 and -1.2 < ny < 1.4:
                        u = nx * nx + ny * ny - 1.0
                        f = u * u * u - nx * nx * (ny ** 3)
                        if -0.22 < f <= 0.0:
                            idx = row_off + px
                            char_buf[idx] = heart_sym if f > -0.10 else "*"
                            col_buf[idx] = sample_stops(pal["heart"], 0.6 + boost * 2.0, eff_16)

            # Hugging couple in the center of the heart
            self._draw_centered(char_buf, col_buf, cur_w, canvas_h, cy - 1, "(>^_^)(^_^<)", lambda i, n: col_pink if i >= 6 else col_accent)
            self._draw_centered(char_buf, col_buf, cur_w, canvas_h, cy,     " /|    |\\ ", lambda i, n: col_pink if i >= 5 else col_accent)

            pair = f"{self.his_name} & {self.her_name} committed aayi!" if (self.his_name and self.her_name) else "nammal committed aayi!"
            self._draw_centered(
                char_buf, col_buf, cur_w, canvas_h, canvas_h - 3,
                f"{decor}  Aval enne kettipidichu... {pair}  {decor}",
                lambda i, n: sample_stops(pal["text"], 0.55 + 0.45 * math.sin(t * 4.5 - i * 0.25), eff_16),
            )

        # Assemble atomic ANSI frame with run-length color compression
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
                f" [SPC] {'PAUSE' if self.paused else 'PLAY'} | "
                f"[C] {cur_theme.upper()} | [A] {'ASCII' if self.ascii_only else 'HEART'} | [R] Replay | [Q] Quit"
            )
            out_lines.append(f"\033[90m{hud_plain[:cur_w].ljust(cur_w)}\033[0m")

        return "\n".join(out_lines) + "\n"


# ---------------------------------------------------------------------------
# Local Runner & Built-in HTTP Streaming Server (--serve)
# ---------------------------------------------------------------------------

def run_local(args, kb_state):
    gen = StoryGenerator(
        his_name=args.his_name,
        her_name=args.her_name,
        theme=args.theme,
        ascii_only=args.ascii,
        use_16color=args.use_16color,
        include_hud=True,
        loop=True,
        initial_w=args.width,
        initial_h=args.height,
    )
    if args.chapter:
        gen.sim_time = CHAPTER_STARTS[max(0, min(4, args.chapter - 1))]

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
            elif key == " ":
                gen.paused = not gen.paused
            elif key == "n":
                gen.jump_chapter(1)
            elif key == "b":
                gen.jump_chapter(-1)
            elif key == "r":
                gen.replay()
            elif key == "c":
                gen.theme_idx = (gen.theme_idx + 1) % len(THEMES)
            elif key == "a":
                gen.ascii_only = not gen.ascii_only
            elif key in ("+", "="):
                gen.speed_mult = min(3.0, gen.speed_mult + 0.25)
            elif key in ("-", "_"):
                gen.speed_mult = max(0.25, gen.speed_mult - 0.25)

        if not args.no_resize:
            cols, rows = shutil.get_terminal_size((80, 24))
            cur_w = max(52, cols - 1)
            cur_h = max(18, rows - 2)
        else:
            cur_w = max(52, args.width - 1)
            cur_h = max(18, args.height - 2)

        sys.stdout.write(gen.render_frame(raw_dt, cur_w, cur_h))
        sys.stdout.flush()

        sleep_s = interval - (time.perf_counter() - cycle_start)
        if sleep_s > 0:
            time.sleep(sleep_s)


class ThreadingStoryServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class StoryStreamHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "OurStoryLive/1.0"

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
            page = f"<html><body style='background:#120911;color:#ffd9e6;font-family:Consolas,monospace;padding:40px'><h2>Our Story - Terminal Animation</h2><p>CMD: <code>curl -sN http://{safe}/</code></p><p>PowerShell: <code>curl.exe -sN http://{safe}/</code></p></body></html>".encode("utf-8")
            self._send_bytes(200, "text/html; charset=utf-8", page)
            return

        his_name = params.get("his", [""])[0]
        her_name = params.get("her", [""])[0]
        theme = params.get("theme", ["romantic"])[0].lower()
        use_utf8 = params.get("utf8", ["0"])[0] in ("1", "true", "yes")
        use_16 = params.get("color", [""])[0] == "16"
        max_frames = int(params.get("frames", ["0"])[0] or 0)
        fps = max(5, min(30, int(params.get("fps", ["20"])[0] or 20)))

        gen = StoryGenerator(
            his_name=his_name,
            her_name=her_name,
            theme=theme if theme in THEMES else "romantic",
            ascii_only=not use_utf8,
            use_16color=use_16,
            include_hud=False,
            loop=True,
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


def serve_story(host: str, port: int):
    httpd = ThreadingStoryServer((host, port), StoryStreamHandler)
    signal.signal(signal.SIGINT, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    disp = "localhost" if host == "0.0.0.0" else host
    print(f"Our Story curl server listening on http://{disp}:{port}")
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
        description="5-Chapter Love Story Terminal Animation (CMD, PowerShell & GitHub curl ready)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--his-name", default="", help="Optional first name for the finale banner")
    parser.add_argument("--her-name", default="", help="Optional partner name for the finale banner")
    parser.add_argument("--theme", "-t", choices=THEMES, default="romantic", help="Color theme")
    parser.add_argument("--chapter", type=int, default=0, help="Start directly at chapter 1-5")
    parser.add_argument("--fps", "-f", type=int, default=30, help="Target FPS")
    parser.add_argument("--ascii", action="store_true", help="Force strict 7-bit ASCII characters")
    parser.add_argument("--16color", dest="use_16color", action="store_true", help="Force 16-color ANSI palette")
    parser.add_argument("--width", "-w", type=int, default=80, help="Fixed width when --no-resize is used")
    parser.add_argument("--height", type=int, default=24, help="Fixed height when --no-resize is used")
    parser.add_argument("--no-resize", action="store_true", help="Disable terminal auto-resize")
    parser.add_argument("--frames", type=int, default=0, help="Exit after N frames (useful for testing)")
    parser.add_argument("--serve", action="store_true", help="Start curl-streamable HTTP server")
    parser.add_argument("--host", default="0.0.0.0", help="Host interface for --serve")
    parser.add_argument("--port", "-p", type=int, default=int(os.environ.get("PORT", "8080")), help="Port for --serve")

    args = parser.parse_args()
    if args.serve:
        serve_story(args.host, args.port)
        return

    kb_state = setup_keyboard()
    try:
        with WindowsConsoleGuard(use_utf8=not args.ascii):
            run_local(args, kb_state)
    except KeyboardInterrupt:
        pass
    finally:
        restore_keyboard(kb_state)
        print("Story animation ended cleanly.")


if __name__ == "__main__":
    main()
