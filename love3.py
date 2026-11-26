
import os
import sys
import time
import math
import random
import shutil

os.system("")

PINK = "\033[95m"
RED = "\033[91m"
BLUE = "\033[94m"
CYAN = "\033[96m"
GOLD = "\033[93m"
WHITE = "\033[97m"
RESET = "\033[0m"

def terminal():
    s = shutil.get_terminal_size((80, 25))
    return min(s.columns, 90), min(s.lines, 28)

def frame():
    w, h = terminal()
    return [[" " for _ in range(w)] for _ in range(h)]

def put(c, x, y, text):
    for i, ch in enumerate(text):
        if 0 <= y < len(c) and 0 <= x+i < len(c[0]):
            c[y][x+i] = ch

def show(c, color=WHITE):
    sys.stdout.write("\033[H\033[2J")
    sys.stdout.write(color)
    sys.stdout.write("\n".join("".join(row) for row in c))
    sys.stdout.write(RESET)
    sys.stdout.flush()

def wait(t=0.08):
    time.sleep(t)

def stars(c, count=35):
    h, w = len(c), len(c[0])
    for _ in range(count):
        x = random.randrange(w)
        y = random.randrange(max(1, h-5))
        c[y][x] = random.choice([".", "*", "+"])

def opening():
    w, h = terminal()

    for f in range(35):
        c = frame()
        stars(c, 45)

        put(c, w//2-5, 3, "A NIGHT TO REMEMBER")
        put(c, w-15, 4, " .--. ")
        put(c, w-15, 5, "(    )")
        put(c, w-15, 6, " '--' ")

        put(c, w//2-13, h//2, "SOMEWHERE UNDER THE STARS...")
        show(c, CYAN)
        wait(0.16)

def walking():
    w, h = terminal()
    ground = h-6

    for f in range(48):
        c = frame()
        stars(c, 35)

        put(c, w-16, 3, "( MOON )")
        put(c, 0, ground, "_"*w)

        left = 2 + f
        right = w-7-f

        # Walking characters
        put(c, left, ground-3, " O ")
        put(c, left, ground-2, "/|\\")
        put(c, left, ground-1, "/ \\")

        put(c, right, ground-3, " O ")
        put(c, right, ground-2, "/|\\")
        put(c, right, ground-1, "/ \\")

        put(c, w//2-15, 2, "TWO STRANGERS...")
        put(c, w//2-15, 3, "ONE BEAUTIFUL DESTINY")

        show(c, WHITE)
        wait(0.12)

def meeting():
    w, h = terminal()
    ground = h-6

    for f in range(30):
        c = frame()
        stars(c, 40)

        put(c, 0, ground, "_"*w)

        put(c, w//2-5, ground-3, " O     O ")
        put(c, w//2-5, ground-2, "/|\\   /|\\")
        put(c, w//2-5, ground-1, "/ \\   / \\")

        put(c, w//2-12, 2, "AND THEN THEY MET...")
        put(c, w//2-13, 4, "THE WORLD STOOD STILL")

        show(c, PINK)
        wait(0.18)

def rain_scene():
    w, h = terminal()
    drops = [
        [random.randrange(w), random.randrange(h)]
        for _ in range(65)
    ]

    for f in range(45):
        c = frame()
        stars(c, 20)

        for d in drops:
            x, y = d
            if 0 <= x < w and 0 <= y < h:
                c[y][x] = "|"
            d[1] += 1
            if d[1] >= h:
                d[0] = random.randrange(w)
                d[1] = 0

        put(c, w//2-12, h//2, "EVEN THE RAIN...")
        put(c, w//2-15, h//2+2, "COULD NOT HIDE THEIR LOVE")

        show(c, CYAN)
        wait(0.10)

def heart_scene():
    w, h = terminal()

    heart = [
        "  **   **  ",
        " **** **** ",
        "***********",
        " ********* ",
        "  *******  ",
        "   *****   ",
        "    ***    ",
        "     *     "
    ]

    for f in range(55):
        c = frame()
        stars(c, 45)

        for i, line in enumerate(heart):
            put(c, w//2-6, h//2-6+i, line)

        put(c, w//2-13, h//2+5, "MY HEART CHOSE YOU")

        show(c, RED if f % 2 else PINK)
        wait(0.12)

def fireworks():
    w, h = terminal()

    for f in range(45):
        c = frame()

        for _ in range(65):
            x = random.randrange(w)
            y = random.randrange(h-3)
            c[y][x] = random.choice(["*", "+", ".", "x"])

        put(c, w//2-8, h//2, "YOU ARE MY STAR")
        put(c, w//2-11, h//2+2, "YOU ARE MY EVERYTHING")

        show(c, random.choice([GOLD, PINK, RED, CYAN]))
        wait(0.13)

def finale():
    w, h = terminal()
    messages = [
        "I searched the whole universe...",
        "But I found my whole world in you.",
        "",
        "You are my favourite story.",
        "My happiest place.",
        "My forever person.",
        "",
        "I LOVE YOU.",
        "",
        "FOREVER AND ALWAYS <3"
    ]

    sys.stdout.write("\033[2J\033[H")
    time.sleep(0.8)

    print("\n")
    print(PINK + "          A MESSAGE FROM MY HEART" + RESET)
    time.sleep(1.2)

    for line in messages:
        for ch in line:
            sys.stdout.write(RED + ch + RESET)
            sys.stdout.flush()
            wait(0.055)
        print()
        wait(0.65)

    print("\n" + GOLD + "          END OF OUR LITTLE MOVIE." + RESET)

try:
    opening()
    walking()
    meeting()
    rain_scene()
    heart_scene()
    fireworks()
    finale()

except KeyboardInterrupt:
    sys.stdout.write(RESET + "\n\nLOVE YOU <3\n")

finally:
    sys.stdout.write(RESET)
    sys.stdout.flush()
