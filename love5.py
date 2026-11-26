#!/usr/bin/env python3
"""
Terminal Love Animation (Windows CMD & PowerShell Compatible)
=============================================================
A pure-Python, zero-dependency terminal animation designed to run smoothly
in Windows Command Prompt (cmd.exe), Windows PowerShell 5.1, PowerShell 7,
Windows Terminal, and Unix terminals.

Features:
- 3 switchable animation modes:
  1. 'beat'      : Lub-dub pulsing heart with 3D pillow shading, expanding aura & floating hearts
  2. '3d'        : Real-time volumetric 3D spinning & beating heart with z-buffer lighting
  3. 'fireworks' : Parametric heart-shaped fireworks & rising love sparks
- Automatic Windows Virtual Terminal (ANSI) activation & console state restoration
- Safe CP437 / UTF-8 / Pure-ASCII character modes (never crashes on legacy cmd.exe encoding)
- Run-length ANSI color batching & 1-col margin to prevent cmd.exe scroll jitter
- Non-blocking real-time keyboard controls across both CMD and PowerShell
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
# Platform Console & Keyboard Handling (Windows CMD/PowerShell + Unix)
# ---------------------------------------------------------------------------

class WindowsConsoleGuard:
    """Safely enables ANSI VT processing & UTF-8 in Windows CMD/PowerShell and restores on exit."""

    def __init__(self, use_utf8: bool = True):
        self.use_utf8 = use_utf8
        self.is_windows = os.name == "nt"
        self.h_out = None
        self.orig_mode = None
        self.orig_cp = None
        self.vt_enabled = False

    def __enter__(self):
        if self.is_windows:
            try:
                kernel32 = ctypes.windll.kernel32
                STD_OUTPUT_HANDLE = -11
                ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
                h_out = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
                mode = ctypes.c_ulong()
                if kernel32.GetConsoleMode(h_out, ctypes.byref(mode)):
                    self.h_out = h_out
                    self.orig_mode = mode.value
                    new_mode = mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING
                    if kernel32.SetConsoleMode(h_out, new_mode):
                        self.vt_enabled = True
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

    def check_keypress():
        """Non-blocking key poll for Windows CMD and PowerShell (even when stdin is piped from curl)."""
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

    def check_keypress():
        """Non-blocking key poll for Unix terminals."""
        return None


def check_keypress_with_state(kb_state):
    """Unified keyboard poll supporting piped curl | python - on both Windows and Unix."""
    if os.name == "nt":
        return check_keypress()
    if kb_state is None:
        return None
    fd, _, tty_file = kb_state
    stream = tty_file if tty_file is not None else sys.stdin
    try:
        dr, _, _ = select.select([stream], [], [], 0)
        if dr:
            ch = stream.read(1)
            return ch.lower()
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Color Themes (TrueColor RGB + 16-Color ANSI Fallback)
# ---------------------------------------------------------------------------

THEMES = ["crimson", "rose", "sunset", "cyberlove", "pastel", "classic"]
MODES = ["beat", "3d", "fireworks"]

# Each TrueColor theme defines gradient stops:
# (deep_shadow, mid_body, bright_fill, specular_highlight, aura_glow, text_primary, text_accent)
THEME_STOPS = {
    "crimson": {
        "stops": [(110, 8, 28), (200, 20, 60), (255, 65, 110), (255, 215, 225)],
        "aura": (165, 30, 75),
        "text": (255, 180, 205),
        "accent": (255, 95, 140),
    },
    "rose": {
        "stops": [(140, 25, 85), (225, 55, 130), (255, 125, 185), (255, 235, 248)],
        "aura": (195, 70, 145),
        "text": (255, 210, 235),
        "accent": (255, 120, 185),
    },
    "sunset": {
        "stops": [(145, 22, 22), (235, 70, 50), (255, 155, 95), (255, 240, 200)],
        "aura": (210, 85, 55),
        "text": (255, 220, 175),
        "accent": (255, 135, 85),
    },
    "cyberlove": {
        "stops": [(75, 15, 135), (195, 25, 165), (255, 70, 210), (140, 250, 255)],
        "aura": (130, 45, 215),
        "text": (190, 245, 255),
        "accent": (255, 85, 210),
    },
    "pastel": {
        "stops": [(135, 90, 165), (225, 125, 180), (255, 175, 210), (255, 245, 250)],
        "aura": (175, 125, 205),
        "text": (255, 235, 245),
        "accent": (235, 165, 255),
    },
}


def lerp_rgb(c1, c2, t: float):
    t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


def sample_theme_rgb(theme_name: str, val: float, use_16color: bool = False):
    """Sample a 4-stop gradient in [0.0, 1.0] quantized to multiples of 8 for fast ANSI batching."""
    if use_16color or theme_name == "classic":
        if val > 0.82:
            return "\033[97m"
        elif val > 0.52:
            return "\033[95m"
        elif val > 0.25:
            return "\033[91m"
        return "\033[31m"

    stops = THEME_STOPS[theme_name]["stops"]
    v = 0.0 if val < 0.0 else (1.0 if val > 1.0 else val)
    scaled = v * (len(stops) - 1)
    idx = int(scaled)
    if idx >= len(stops) - 1:
        r, g, b = stops[-1]
    else:
        r, g, b = lerp_rgb(stops[idx], stops[idx + 1], scaled - idx)

    # Quantize to step of 8 to maximize run-length ANSI color compression in CMD
    r = (r // 8) * 8
    g = (g // 8) * 8
    b = (b // 8) * 8
    return f"\033[38;2;{r};{g};{b}m"


def rgb_ansi(rgb, use_16color: bool = False, fallback: str = "\033[91m") -> str:
    if use_16color:
        return fallback
    r, g, b = (rgb[0] // 8) * 8, (rgb[1] // 8) * 8, (rgb[2] // 8) * 8
    return f"\033[38;2;{r};{g};{b}m"


# ---------------------------------------------------------------------------
# Heartbeat Wave & Particle System
# ---------------------------------------------------------------------------

def heartbeat_pulse(t: float, period: float = 1.35):
    """
    Realistic double-thump 'lub-DUB' heartbeat signal.
    Returns (scale_boost in [0, ~0.22], ring_progress in [0, 1], ring_alpha in [0, 1]).
    """
    phase = (t % period) / period
    lub = 0.11 * math.exp(-((phase - 0.12) / 0.042) ** 2)
    dub = 0.21 * math.exp(-((phase - 0.28) / 0.052) ** 2)
    boost = lub + dub

    # Expanding shockwave launched on the main DUB beat
    ring_p = (phase - 0.25) % 1.0
    ring_alpha = max(0.0, 1.0 - ring_p * 1.35)
    return boost, ring_p, ring_alpha


class FloatingSpark:
    """Gentle rising mini-heart / sparkle particle."""

    def __init__(self, w: int, h: int, random_y: bool = False):
        self.reset(w, h, random_y=random_y)

    def reset(self, w: int, h: int, random_y: bool = False):
        self.x = random.uniform(2.0, max(3.0, w - 3.0))
        self.y = random.uniform(1.0, max(2.0, h - 2.0)) if random_y else float(h - 2)
        self.vy = -random.uniform(3.5, 8.5)
        self.vx = random.uniform(-1.2, 1.2)
        self.phase = random.uniform(0.0, math.tau)
        self.kind = random.choices(["heart", "spark", "dot"], weights=[0.45, 0.35, 0.20])[0]
        self.tint = random.uniform(0.35, 0.95)

    def update(self, dt: float, w: int, h: int):
        self.phase += dt * 3.0
        self.x += (self.vx + math.sin(self.phase) * 1.4) * dt
        self.y += self.vy * dt
        if self.y < 1.0 or self.x < 1.0 or self.x >= w - 1:
            self.reset(w, h, random_y=False)


class FireworkSpark:
    """Individual spark from a heart-shaped firework burst."""

    def __init__(self, x: float, y: float, vx: float, vy: float, life: float, tint: float, glyph_idx: int):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.max_life = life
        self.life = life
        self.tint = tint
        self.glyph_idx = glyph_idx


class HeartFirework:
    """Rocket that ascends and bursts into a parametric heart silhouette."""

    def __init__(self, w: int, h: int):
        self.x = random.uniform(w * 0.22, w * 0.78)
        self.y = float(h - 2)
        self.target_y = random.uniform(h * 0.22, h * 0.45)
        self.vy = -random.uniform(22.0, 32.0)
        self.vx = random.uniform(-3.0, 3.0)
        self.exploded = False
        self.sparks = []
        self.hue_shift = random.uniform(0.15, 0.95)

    def update(self, dt: float, w: int, h: int):
        if not self.exploded:
            self.x += self.vx * dt
            self.y += self.vy * dt
            self.vy += 12.0 * dt
            if self.y <= self.target_y or self.vy >= -2.0:
                self._explode(w, h)
        else:
            alive = []
            for sp in self.sparks:
                sp.life -= dt
                if sp.life > 0:
                    sp.vx *= 0.965
                    sp.vy = sp.vy * 0.965 + 7.5 * dt
                    sp.x += sp.vx * dt
                    sp.y += sp.vy * dt
                    alive.append(sp)
            self.sparks = alive

    def _explode(self, w: int, h: int):
        self.exploded = True
        scale = min(w * 0.045, h * 0.09)
        count = 64
        tilt = random.uniform(-0.22, 0.22)
        cos_t, sin_t = math.cos(tilt), math.sin(tilt)

        for i in range(count):
            t = (i / count) * math.tau
            # Parametric heart curve
            hx = 16.0 * (math.sin(t) ** 3)
            hy = -(13.0 * math.cos(t) - 5.0 * math.cos(2 * t) - 2.0 * math.cos(3 * t) - math.cos(4 * t))
            # Apply slight tilt and aspect ratio (~2.0)
            rx = (hx * cos_t - hy * sin_t) * 0.30 * scale * 2.0
            ry = (hx * sin_t + hy * cos_t) * 0.30 * scale

            jitter = random.uniform(0.88, 1.12)
            life = random.uniform(1.1, 1.8)
            self.sparks.append(
                FireworkSpark(
                    x=self.x,
                    y=self.y,
                    vx=rx * jitter,
                    vy=ry * jitter,
                    life=life,
                    tint=min(1.0, max(0.1, self.hue_shift + random.uniform(-0.18, 0.25))),
                    glyph_idx=i % 3,
                )
            )
        # Inner core twinkle sparks
        for _ in range(18):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(2.0, 9.0)
            self.sparks.append(
                FireworkSpark(
                    x=self.x,
                    y=self.y,
                    vx=math.cos(ang) * spd * 1.9,
                    vy=math.sin(ang) * spd,
                    life=random.uniform(0.7, 1.3),
                    tint=random.uniform(0.75, 1.0),
                    glyph_idx=0,
                )
            )

    def is_done(self) -> bool:
        return self.exploded and len(self.sparks) == 0


# ---------------------------------------------------------------------------
# 3D Volumetric Heart Surface Precomputation (Taubin Surface)
# ---------------------------------------------------------------------------

def build_3d_heart_cloud():
    """
    Generate evenly distributed points + exact analytical surface normals on Taubin's 3D heart:
    F(x, y, z) = (x^2 + 9/4 y^2 + z^2 - 1)^3 - x^2 z^3 - 9/80 y^2 z^3 = 0
    where x=width, y=thickness, z=vertical up.
    """
    pts = []
    seen_buckets = set()

    def add_point(x: float, y: float, z: float):
        # Spatial hash dedup so front-slice and side-slice don't overdraw identically
        key = (int(round(x * 26)), int(round(y * 26)), int(round(z * 26)))
        if key in seen_buckets:
            return
        seen_buckets.add(key)

        u = x * x + 2.25 * y * y + z * z - 1.0
        u2 = u * u
        z2 = z * z
        z3 = z2 * z
        nx = 6.0 * x * u2 - 2.0 * x * z3
        ny = 13.5 * y * u2 - 0.225 * y * z3
        nz = 6.0 * z * u2 - 3.0 * x * x * z2 - 0.3375 * y * y * z2
        n_len = math.sqrt(nx * nx + ny * ny + nz * nz)
        if n_len < 1e-6:
            return
        pts.append((x, y, z, nx / n_len, ny / n_len, nz / n_len))

    step = 0.036

    # Pass 1: Slice (x, z) and bisect for front/back +/- y
    for ix in range(-36, 37):
        x = ix * step
        for iz in range(-32, 39):
            z = iz * step
            if (x * x + z * z - 1.0) ** 3 - x * x * (z ** 3) <= 0.0:
                lo, hi = 0.0, 0.72
                for _ in range(11):
                    m = (lo + hi) * 0.5
                    val = (x * x + 2.25 * m * m + z * z - 1.0) ** 3 - (x * x + 0.1125 * m * m) * (z ** 3)
                    if val <= 0.0:
                        lo = m
                    else:
                        hi = m
                y = lo
                add_point(x, y, z)
                if y > 0.025:
                    add_point(x, -y, z)

    # Pass 2: Slice (y, z) and bisect for left/right +/- x (eliminates holes at 90-degree edge view)
    for iy in range(-22, 23):
        y = iy * step
        for iz in range(-32, 39):
            z = iz * step
            if (2.25 * y * y + z * z - 1.0) ** 3 - 0.1125 * y * y * (z ** 3) <= 0.0:
                lo, hi = 0.0, 1.25
                for _ in range(11):
                    m = (lo + hi) * 0.5
                    val = (m * m + 2.25 * y * y + z * z - 1.0) ** 3 - (m * m + 0.1125 * y * y) * (z ** 3)
                    if val <= 0.0:
                        lo = m
                    else:
                        hi = m
                x = lo
                add_point(x, y, z)
                if x > 0.025:
                    add_point(-x, y, z)

    return pts


_HEART_CLOUD_CACHE = None


def get_3d_heart_cloud():
    """Return cached 3D Taubin heart point cloud (shared across local & HTTP streams)."""
    global _HEART_CLOUD_CACHE
    if _HEART_CLOUD_CACHE is None:
        _HEART_CLOUD_CACHE = build_3d_heart_cloud()
    return _HEART_CLOUD_CACHE


# ---------------------------------------------------------------------------
# Reusable Frame Generator (shared by local CLI & curl HTTP streaming server)
# ---------------------------------------------------------------------------

class LoveFrameGenerator:
    """Stateful ANSI frame generator for beat, 3D, and heart-fireworks animations."""

    def __init__(
        self,
        mode: str = "beat",
        theme: str = "crimson",
        message: str = "I LOVE YOU",
        ascii_only: bool = False,
        use_16color: bool = False,
        include_hud: bool = True,
        initial_width: int = 78,
        initial_height: int = 22,
    ):
        self.mode_idx = MODES.index(mode) if mode in MODES else 0
        self.theme_idx = THEMES.index(theme) if theme in THEMES else 0
        self.message = message
        self.ascii_only = ascii_only
        self.use_16color = use_16color
        self.include_hud = include_hud

        self.heart_cloud = get_3d_heart_cloud()
        self.sparks = [FloatingSpark(initial_width, initial_height, random_y=True) for _ in range(28)]
        self.fireworks = []
        self.next_fw_time = 0.0

        self.paused = False
        self.speed_mult = 1.0
        self.sim_time = 0.0
        self.angle_y = 0.0

    def render_frame(self, raw_dt: float, cur_w: int, cur_h: int) -> str:
        """Advance simulation by raw_dt and return one complete ANSI frame."""
        cur_mode = MODES[self.mode_idx]
        cur_theme = THEMES[self.theme_idx]
        effective_16 = self.use_16color or (cur_theme == "classic")

        canvas_h = max(12, cur_h - (1 if self.include_hud else 0))

        if not self.paused:
            dt = raw_dt * self.speed_mult
            self.sim_time += dt
            self.angle_y += dt * 1.15

        if self.ascii_only:
            shades = ".,-~:;=!*#$@"
            spark_chars = ("<3", "*", "+")
            heart_glyph = "*"
        else:
            shades = ".,-~:;=!*#\u2665@"
            spark_chars = ("\u2665", "*", "\u2022")
            heart_glyph = "\u2665"

        size = cur_w * canvas_h
        char_buf = [" "] * size
        col_buf = [""] * size
        z_buf = [-1e9] * size

        if not self.paused:
            for sp in self.sparks:
                sp.update(raw_dt * self.speed_mult, cur_w, canvas_h)

        for sp in self.sparks:
            sx = int(sp.x)
            sy = int(sp.y)
            if 0 <= sx < cur_w and 0 <= sy < canvas_h:
                twinkle = 0.5 + 0.5 * math.sin(sp.phase * 1.8)
                tint_val = max(0.15, min(0.95, sp.tint * (0.6 + 0.4 * twinkle)))
                col = sample_theme_rgb(cur_theme, tint_val, effective_16)
                if sp.kind == "heart":
                    if self.ascii_only and sx + 1 < cur_w:
                        idx = sy * cur_w + sx
                        char_buf[idx] = "<"
                        col_buf[idx] = col
                        char_buf[idx + 1] = "3"
                        col_buf[idx + 1] = col
                    else:
                        idx = sy * cur_w + sx
                        char_buf[idx] = heart_glyph
                        col_buf[idx] = col
                elif sp.kind == "spark":
                    idx = sy * cur_w + sx
                    char_buf[idx] = "+" if twinkle > 0.5 else "*"
                    col_buf[idx] = col
                else:
                    idx = sy * cur_w + sx
                    char_buf[idx] = "." if self.ascii_only else "\u2022"
                    col_buf[idx] = col

        boost, ring_p, ring_alpha = heartbeat_pulse(self.sim_time)
        cx = cur_w * 0.5
        cy = canvas_h * 0.46

        if cur_mode == "beat":
            beat_scale = 1.0 + boost
            scale_y = min(canvas_h * 0.34, cur_w / (2.5 * 2.05))
            scale_x = scale_y * 2.05
            inv_sx = 1.0 / (scale_x * beat_scale)
            inv_sy = 1.0 / (scale_y * beat_scale)

            ring_scale = 1.05 + ring_p * 0.95
            inv_rx = 1.0 / (scale_x * ring_scale)
            inv_ry = 1.0 / (scale_y * ring_scale)

            aura_col = rgb_ansi(
                THEME_STOPS.get(cur_theme, THEME_STOPS["crimson"])["aura"],
                use_16color=effective_16,
                fallback="\033[31m",
            )

            for py in range(canvas_h):
                ny_base = (cy - py) * inv_sy + 0.10
                ry_base = (cy - py) * inv_ry + 0.10
                row_off = py * cur_w

                for px in range(cur_w):
                    nx = (px - cx) * inv_sx
                    if nx < -1.6 or nx > 1.6 or ny_base < -1.4 or ny_base > 1.65:
                        continue

                    x2 = nx * nx
                    y2 = ny_base * ny_base
                    u = x2 + y2 - 1.0
                    f = u * u * u - x2 * (y2 * ny_base)

                    if f <= 0.0:
                        depth = min(1.0, (-f) ** 0.38 * 1.15)
                        highlight = max(0.0, (-nx * 0.45 + ny_base * 0.65) * 0.42)
                        lum = min(1.0, 0.25 + depth * 0.58 + highlight + boost * 0.65)
                        s_idx = min(len(shades) - 1, max(1, int(lum * (len(shades) - 1))))

                        idx = row_off + px
                        char_buf[idx] = shades[s_idx]
                        col_buf[idx] = sample_theme_rgb(cur_theme, lum, effective_16)
                    else:
                        u2 = u * u
                        df_x = 6.0 * nx * u2 - 2.0 * nx * (y2 * ny_base)
                        df_y = 6.0 * ny_base * u2 - 3.0 * x2 * y2
                        grad = math.sqrt(df_x * df_x + df_y * df_y)
                        dist = f / max(0.45, grad)

                        if dist < 0.085 * beat_scale:
                            glow = 1.0 - dist / (0.085 * beat_scale)
                            idx = row_off + px
                            char_buf[idx] = ":" if glow > 0.6 else "."
                            col_buf[idx] = aura_col
                        elif ring_alpha > 0.14:
                            rx = (px - cx) * inv_rx
                            rx2 = rx * rx
                            ry2 = ry_base * ry_base
                            ru = rx2 + ry2 - 1.0
                            rf = ru * ru * ru - rx2 * (ry2 * ry_base)
                            if -0.22 < rf < 0.22:
                                ru2 = ru * ru
                                rdx = 6.0 * rx * ru2 - 2.0 * rx * (ry2 * ry_base)
                                rdy = 6.0 * ry_base * ru2 - 3.0 * rx2 * ry2
                                rdist = abs(rf) / max(0.45, math.sqrt(rdx * rdx + rdy * rdy))
                                if rdist < 0.042:
                                    idx = row_off + px
                                    char_buf[idx] = "~" if ring_alpha > 0.5 else "."
                                    col_buf[idx] = sample_theme_rgb(cur_theme, 0.35 + 0.45 * ring_alpha, effective_16)

        elif cur_mode == "3d":
            beat_scale = 1.0 + boost * 0.85
            cos_a, sin_a = math.cos(self.angle_y), math.sin(self.angle_y)
            tilt_x = 0.22 * math.sin(self.sim_time * 0.7)
            cos_b, sin_b = math.cos(tilt_x), math.sin(tilt_x)

            k2 = 3.8
            k1 = min(canvas_h * 0.85, cur_w / 2.6) * k2 * 0.28 * beat_scale

            lx, ly, lz = 0.45, -0.70, 0.55
            l_len = math.sqrt(lx * lx + ly * ly + lz * lz)
            lx, ly, lz = lx / l_len, ly / l_len, lz / l_len

            for x, y, z, nx, ny, nz in self.heart_cloud:
                rx1 = x * cos_a - y * sin_a
                ry1 = x * sin_a + y * cos_a
                rz1 = z

                rx = rx1
                ry = ry1 * cos_b - rz1 * sin_b
                rz = ry1 * sin_b + rz1 * cos_b

                nrx1 = nx * cos_a - ny * sin_a
                nry1 = nx * sin_a + ny * cos_a
                nrz1 = nz

                nrx = nrx1
                nry = nry1 * cos_b - nrz1 * sin_b
                nrz = nry1 * sin_b + nrz1 * cos_b

                depth_z = k2 + ry
                if depth_z <= 0.2:
                    continue
                ooz = 1.0 / depth_z

                px = int(cx + k1 * ooz * rx * 2.0)
                py = int(cy - k1 * ooz * rz + 0.5)

                if 0 <= px < cur_w and 0 <= py < canvas_h:
                    idx = py * cur_w + px
                    if ooz > z_buf[idx]:
                        z_buf[idx] = ooz
                        dot = nrx * lx + nry * ly + nrz * lz
                        lum = max(0.08, min(1.0, 0.22 + max(0.0, dot) * 0.78 + boost * 0.35))
                        s_idx = min(len(shades) - 1, max(1, int(lum * (len(shades) - 1))))
                        char_buf[idx] = shades[s_idx]
                        col_buf[idx] = sample_theme_rgb(cur_theme, lum, effective_16)

        elif cur_mode == "fireworks":
            if not self.fireworks:
                first_fw = HeartFirework(cur_w, canvas_h)
                first_fw.x = cur_w * 0.5
                first_fw.y = canvas_h * 0.36
                first_fw._explode(cur_w, canvas_h)
                self.fireworks.append(first_fw)

            if not self.paused:
                if self.sim_time >= self.next_fw_time and len(self.fireworks) < 6:
                    self.fireworks.append(HeartFirework(cur_w, canvas_h))
                    self.next_fw_time = self.sim_time + random.uniform(0.35, 0.85)

                for fw in self.fireworks:
                    fw.update(raw_dt * self.speed_mult, cur_w, canvas_h)
                self.fireworks = [fw for fw in self.fireworks if not fw.is_done()]

            for fw in self.fireworks:
                if not fw.exploded:
                    fx, fy = int(fw.x), int(fw.y)
                    if 0 <= fx < cur_w and 0 <= fy < canvas_h:
                        idx = fy * cur_w + fx
                        char_buf[idx] = "^"
                        col_buf[idx] = sample_theme_rgb(cur_theme, 0.95, effective_16)
                    if 0 <= fx < cur_w and 0 <= fy + 1 < canvas_h:
                        idx2 = (fy + 1) * cur_w + fx
                        char_buf[idx2] = "|"
                        col_buf[idx2] = sample_theme_rgb(cur_theme, 0.50, effective_16)
                else:
                    for sp in fw.sparks:
                        sx, sy = int(sp.x), int(sp.y)
                        if 0 <= sx < cur_w and 0 <= sy < canvas_h:
                            life_ratio = sp.life / sp.max_life
                            idx = sy * cur_w + sx
                            if life_ratio > z_buf[idx]:
                                z_buf[idx] = life_ratio
                                g_char = spark_chars[sp.glyph_idx]
                                if g_char == "<3":
                                    g_char = "*" if self.ascii_only else "\u2665"
                                if life_ratio < 0.25:
                                    g_char = "."
                                char_buf[idx] = g_char
                                col_buf[idx] = sample_theme_rgb(
                                    cur_theme, min(1.0, sp.tint * (0.3 + 0.7 * life_ratio)), effective_16
                                )

        if self.message:
            msg_row = max(1, canvas_h - 2)
            decor = "<3" if self.ascii_only else heart_glyph
            banner_text = f" {decor}  {self.message}  {decor} "
            start_x = max(0, (cur_w - len(banner_text)) // 2)
            row_off = msg_row * cur_w

            for i, ch in enumerate(banner_text):
                tx = start_x + i
                if 0 <= tx < cur_w:
                    wave = 0.5 + 0.5 * math.sin(self.sim_time * 3.5 - i * 0.35)
                    col = sample_theme_rgb(cur_theme, 0.55 + 0.45 * wave, effective_16)
                    char_buf[row_off + tx] = ch
                    col_buf[row_off + tx] = col

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
                f" [M] {cur_mode.upper()} | [C] {cur_theme.upper()} | "
                f"[SPC] {'PAUSE' if self.paused else 'PLAY'} | [A] {'ASCII' if self.ascii_only else 'HEART'} | "
                f"[+/-] {self.speed_mult:.1f}x | [Q] Quit"
            )
            hud_clipped = hud_plain[:cur_w].ljust(cur_w)
            out_lines.append(f"\033[90m{hud_clipped}\033[0m")

        return "\n".join(out_lines) + "\n"


# ---------------------------------------------------------------------------
# Main Local Terminal Animation Loop
# ---------------------------------------------------------------------------

def render_love_animation(
    mode: str = "beat",
    theme: str = "crimson",
    message: str = "I LOVE YOU",
    target_fps: int = 30,
    ascii_only: bool = False,
    use_16color: bool = False,
    width: int = 80,
    height: int = 24,
    auto_resize: bool = True,
    max_frames: int = 0,
    kb_state=None,
):
    gen = LoveFrameGenerator(
        mode=mode,
        theme=theme,
        message=message,
        ascii_only=ascii_only,
        use_16color=use_16color,
        include_hud=True,
        initial_width=width,
        initial_height=height,
    )

    frame_count = 0
    sys.stdout.write("\033[?25l\033[2J")
    sys.stdout.flush()

    last_tick = time.perf_counter()
    frame_interval = 1.0 / max(5, target_fps)

    while True:
        cycle_start = time.perf_counter()
        raw_dt = min(0.1, cycle_start - last_tick)
        last_tick = cycle_start

        frame_count += 1
        if max_frames > 0 and frame_count > max_frames:
            break

        key = check_keypress_with_state(kb_state)
        if key:
            if key in ("q", "\x03"):
                break
            elif key == " ":
                gen.paused = not gen.paused
            elif key == "m":
                gen.mode_idx = (gen.mode_idx + 1) % len(MODES)
            elif key == "c":
                gen.theme_idx = (gen.theme_idx + 1) % len(THEMES)
            elif key == "a":
                gen.ascii_only = not gen.ascii_only
            elif key in ("+", "="):
                gen.speed_mult = min(3.0, gen.speed_mult + 0.25)
            elif key in ("-", "_"):
                gen.speed_mult = max(0.25, gen.speed_mult - 0.25)

        if auto_resize:
            cols, rows = shutil.get_terminal_size((80, 24))
            cur_w = max(44, cols - 1)
            cur_h = max(18, rows - 2)
        else:
            cur_w = max(44, width - 1)
            cur_h = max(18, height - 2)

        frame_str = gen.render_frame(raw_dt, cur_w, cur_h)
        sys.stdout.write(frame_str)
        sys.stdout.flush()

        elapsed = time.perf_counter() - cycle_start
        sleep_s = frame_interval - elapsed
        if sleep_s > 0:
            time.sleep(sleep_s)


# ---------------------------------------------------------------------------
# Optional HTTP Chunked Streaming Server (--serve, parrot.live style)
# ---------------------------------------------------------------------------

def _parse_int_param(params, name: str, default: int, lo: int, hi: int) -> int:
    raw = params.get(name, [None])[0]
    if raw is None:
        return default
    try:
        return max(lo, min(hi, int(raw)))
    except ValueError:
        return default


def _is_truthy(params, name: str, default: bool = False) -> bool:
    raw = params.get(name, [None])[0]
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


class ThreadingLoveHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class LoveStreamHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "LoveLive/1.0"

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
        if not data:
            return
        header = f"{len(data):x}\r\n".encode("ascii")
        self.wfile.write(header + data + b"\r\n")
        self.wfile.flush()

    def _finish_chunks(self):
        self.wfile.write(b"0\r\n\r\n")
        self.wfile.flush()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.strip("/").lower()
        params = parse_qs(parsed.query, keep_blank_values=True)

        if path == "health":
            payload = json.dumps({"status": "ok", "modes": MODES, "themes": THEMES}).encode("utf-8")
            self._send_bytes(200, "application/json; charset=utf-8", payload)
            return

        host_header = self.headers.get("Host", "localhost:8080")
        query_suffix = f"?{parsed.query}" if parsed.query else ""

        if path == "ps":
            stream_url = f"http://{host_header}/{query_suffix}"
            ps_script = f'& curl.exe -sN "{stream_url}"\n'.encode("utf-8")
            self._send_bytes(200, "text/plain; charset=utf-8", ps_script)
            return

        user_agent = self.headers.get("User-Agent", "")
        ua_lower = user_agent.lower()
        raw_override = _is_truthy(params, "raw", False) or "frames" in params

        if not raw_override and "windowspowershell" in ua_lower:
            hint = (
                "\n"
                "  [!] PowerShell Notice:\n"
                "  In Windows PowerShell 5.1, `curl` is an alias for Invoke-WebRequest,\n"
                "  which buffers responses and cannot stream live animations.\n\n"
                "  Run one of these instead:\n"
                f'    curl.exe -sN "http://{host_header}/{query_suffix}"\n'
                f'    irm "http://{host_header}/ps{query_suffix}" | iex\n\n'
                "  (In Command Prompt cmd.exe, `curl` works directly!)\n"
            ).encode("utf-8")
            self._send_bytes(200, "text/plain; charset=utf-8", hint)
            return

        is_browser = (
            not raw_override
            and "mozilla" in ua_lower
            and "curl" not in ua_lower
            and "wget" not in ua_lower
            and "httpie" not in ua_lower
        )
        if is_browser:
            safe_host = html.escape(host_header)
            page = (
                "<!doctype html><html lang='en'><head><meta charset='utf-8'/>"
                "<title>Terminal Love Animation</title>"
                "<style>body{font-family:Consolas,monospace;background:#120911;color:#ffd9e6;"
                "max-width:740px;margin:48px auto;padding:0 20px;line-height:1.6}"
                "h1{color:#ff5d93}pre{background:#22101e;border:1px solid #4d2240;"
                "border-radius:6px;padding:10px 14px;color:#ff9ec2;overflow-x:auto}</style>"
                "</head><body><h1>&lt;3 Terminal Love Animation</h1>"
                f"<p>Command Prompt:</p><pre>curl -sN http://{safe_host}/</pre>"
                f"<p>PowerShell:</p><pre>curl.exe -sN http://{safe_host}/</pre>"
                f"<p>PowerShell shortcut:</p><pre>irm http://{safe_host}/ps | iex</pre>"
                "<p>Options: <code>/beat</code>, <code>/3d</code>, <code>/fireworks</code>, "
                "<code>?theme=cyberlove&amp;msg=Forever+Yours&amp;utf8=1</code></p>"
                "</body></html>"
            ).encode("utf-8")
            self._send_bytes(200, "text/html; charset=utf-8", page)
            return

        default_mode = path if path in MODES else "beat"
        mode = params.get("mode", [default_mode])[0].lower()
        if mode not in MODES:
            mode = "beat"

        theme = params.get("theme", ["crimson"])[0].lower()
        if theme not in THEMES:
            theme = "crimson"

        message = params.get("msg", params.get("message", ["I LOVE YOU"]))[0]
        fps = _parse_int_param(params, "fps", 20, 5, 30)
        width = _parse_int_param(params, "w", 78, 44, 160)
        height = _parse_int_param(params, "h", 22, 16, 60)
        max_frames = _parse_int_param(params, "frames", 0, 0, 100000)

        use_utf8 = _is_truthy(params, "utf8", False)
        use_16color = params.get("color", [""])[0].strip() == "16"

        gen = LoveFrameGenerator(
            mode=mode,
            theme=theme,
            message=message,
            ascii_only=not use_utf8,
            use_16color=use_16color,
            include_hud=False,
            initial_width=width,
            initial_height=height,
        )

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8" if use_utf8 else "text/plain; charset=ascii")
        self.send_header("Transfer-Encoding", "chunked")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("X-Accel-Buffering", "no")
        self.send_header("Connection", "close")
        self.end_headers()

        frame_interval = 1.0 / fps
        last_tick = time.perf_counter()
        frame_num = 0
        encoding = "utf-8" if use_utf8 else "ascii"
        hint = f" [Ctrl+C to stop]  |  Mode: {mode.upper()}  |  Theme: {theme.upper()}"
        footer_bytes = f"\033[90m{hint[:width].ljust(width)}\033[0m".encode(encoding, errors="replace")

        try:
            self._send_chunk(b"\033[2J\033[H")

            while True:
                cycle_start = time.perf_counter()
                raw_dt = min(0.1, cycle_start - last_tick)
                last_tick = cycle_start

                frame_num += 1
                if max_frames > 0 and frame_num > max_frames:
                    break

                frame_bytes = gen.render_frame(raw_dt, width, height).encode(encoding, errors="replace")
                self._send_chunk(frame_bytes + footer_bytes)

                elapsed = time.perf_counter() - cycle_start
                sleep_s = frame_interval - elapsed
                if sleep_s > 0:
                    time.sleep(sleep_s)

            self._send_chunk(b"\033[0m\n")
            self._finish_chunks()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
            pass


def serve_love_http(host: str = "0.0.0.0", port: int = 8080):
    """Run the curl-streamable HTTP server."""
    get_3d_heart_cloud()
    httpd = ThreadingLoveHTTPServer((host, port), LoveStreamHandler)

    def _shutdown(_sig, _frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    display_host = "localhost" if host == "0.0.0.0" else host
    print(f"Love Animation curl server listening on http://{display_host}:{port}")
    print(f"  Command Prompt : curl -sN http://{display_host}:{port}/")
    print(f"  PowerShell     : curl.exe -sN http://{display_host}:{port}/")
    print(f"  PowerShell alt : irm http://{display_host}:{port}/ps | iex")
    print("Press Ctrl+C to stop the server.")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server cleanly...")
    finally:
        httpd.server_close()


def main():
    parser = argparse.ArgumentParser(
        description="Terminal Love Animation compatible with Windows Command Prompt & PowerShell",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--mode", "-m",
        choices=MODES,
        default="beat",
        help="Animation mode (press [M] in-app to switch live)",
    )
    parser.add_argument(
        "--theme", "-t",
        choices=THEMES,
        default="crimson",
        help="Color theme (press [C] in-app to switch live)",
    )
    parser.add_argument(
        "--message", "--msg",
        default="I LOVE YOU",
        help="Custom romantic message displayed below the animation",
    )
    parser.add_argument(
        "--fps", "-f",
        type=int,
        default=30,
        help="Target frames per second",
    )
    parser.add_argument(
        "--ascii",
        action="store_true",
        help="Force strict 7-bit ASCII characters (best for very old fonts)",
    )
    parser.add_argument(
        "--16color",
        dest="use_16color",
        action="store_true",
        help="Force standard 16-color ANSI palette instead of 24-bit TrueColor",
    )
    parser.add_argument(
        "--width", "-w",
        type=int,
        default=80,
        help="Fixed width when --no-resize is used",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=24,
        help="Fixed height when --no-resize is used",
    )
    parser.add_argument(
        "--no-resize",
        action="store_true",
        help="Disable dynamic terminal auto-resize",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=0,
        help="Render N frames then exit (useful for automated verification)",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Start HTTP chunked streaming server for curl clients",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host interface when --serve is active",
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=int(os.environ.get("PORT", "8080")),
        help="Port when --serve is active",
    )

    args = parser.parse_args()

    if args.serve:
        serve_love_http(host=args.host, port=args.port)
        return

    kb_state = setup_keyboard()
    try:
        with WindowsConsoleGuard(use_utf8=not args.ascii):
            render_love_animation(
                mode=args.mode,
                theme=args.theme,
                message=args.message,
                target_fps=args.fps,
                ascii_only=args.ascii,
                use_16color=args.use_16color,
                width=args.width,
                height=args.height,
                auto_resize=not args.no_resize,
                max_frames=args.frames,
                kb_state=kb_state,
            )
    except KeyboardInterrupt:
        pass
    finally:
        restore_keyboard(kb_state)
        print("Love animation ended cleanly.")


if __name__ == "__main__":
    main()
