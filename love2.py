
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

def clear():
    sys.stdout.write("\033[H\033[2J")

def canvas_new(w, h):
    return [[" " for _ in range(w)] for _ in range(h)]

def put(c, x, y, text):
    for i, ch in enumerate(text):
        if 0 <= y < len(c) and 0 <= x+i < len(c[0]):
            c[y][x+i] = ch

def render(c, colors=None):
    for row in c:
        print("".join(row))

def size():
    s = shutil.get_terminal_size((80, 25))
    return max(60, min(s.columns, 100)), max(20, min(s.lines, 32))

def galaxy():
    w, h = size()
    stars = [
        [random.randrange(w), random.randrange(h)]
        for _ in range(90)
    ]

    for frame in range(100):
        w, h = size()
        c = canvas_new(w, h)

        for s in stars:
            x, y = s
            if x < w and y < h:
                c[y][x] = random.choice([".", "*", "+"])
            s[1] += 1
            if s[1] >= h:
                s[1] = 0
                s[0] = random.randrange(w)

        rocket = "===>"
        rx = (frame * 2) % max(1, w-5)
        put(c, rx, h//2, rocket)

        clear()
        print(CYAN + "          JOURNEY THROUGH THE UNIVERSE" + RESET)
        print("\n".join("".join(row) for row in c))
        time.sleep(0.09)

def meteor_shower():
    w, h = size()

    for frame in range(55):
        c = canvas_new(w, h)

        for _ in range(18):
            x = random.randrange(w)
            y = random.randrange(h)
            put(c, x, y, random.choice(["*", ".", "+"]))

        for i in range(6):
            x = (frame * 3 + i * 13) % w
            y = (frame + i * 4) % h
            put(c, x, y, "*****")

        clear()
        print("\n".join("".join(row) for row in c))
        time.sleep(0.1)

def heart_scene():
    w, h = size()
    heart = [
        "  ***       ***  ",
        " *****     ***** ",
        "*******   *******",
        "*****************",
        " *************** ",
        "  *************  ",
        "   ***********   ",
        "     *******     ",
        "       ***       ",
        "        *        "
    ]

    for frame in range(45):
        c = canvas_new(w, h)

        for _ in range(40):
            x = random.randrange(w)
            y = random.randrange(h)
            c[y][x] = random.choice([".", "+", "*"])

        for i, line in enumerate(heart):
            put(c, w//2-9, h//2-7+i, line)

        put(c, w//2-12, h//2+6, "MY UNIVERSE IS YOU")

        clear()
        print(RED + "\n".join("".join(row) for row in c) + RESET)
        time.sleep(0.13)

def final_message():
    clear()
    print(GOLD + "\n\n       TRANSMISSION RECEIVED..." + RESET)
    time.sleep(1.5)

    lines = [
        "From the edge of the universe...",
        "Across millions of stars...",
        "My heart found its destination.",
        "",
        "And that destination is YOU.",
        "",
        "       I LOVE YOU <3",
        "",
        "       YOU ARE MY UNIVERSE."
    ]

    for line in lines:
        for ch in line:
            sys.stdout.write(PINK + ch + RESET)
            sys.stdout.flush()
            time.sleep(0.06)
        print()
        time.sleep(0.7)

try:
    galaxy()
    meteor_shower()
    heart_scene()
    final_message()
except KeyboardInterrupt:
    clear()
    print(RED + "LOVE YOU FOREVER <3" + RESET)
