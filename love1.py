
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
GOLD = "\033[93m"
WHITE = "\033[97m"
RESET = "\033[0m"

def clear():
    sys.stdout.write("\033[2J\033[H")

def draw(canvas, x, y, text, color=WHITE):
    for i, char in enumerate(text):
        if 0 <= y < len(canvas) and 0 <= x+i < len(canvas[0]):
            canvas[y][x+i] = (char, color)

def show(canvas):
    for row in canvas:
        last = None
        for char, color in row:
            if color != last:
                sys.stdout.write(color)
                last = color
            sys.stdout.write(char)
        sys.stdout.write(RESET + "\n")
    sys.stdout.flush()

def scene(stars, left, right, frame, message=""):
    width, height = shutil.get_terminal_size((80, 25))
    width = max(50, min(width, 110))
    height = max(18, min(height, 35))

    canvas = [[(" ", RESET) for _ in range(width)]
              for _ in range(height)]

    for x, y in stars:
        if x < width and y < height:
            draw(canvas, x, y, random.choice([".", "*", "+"]), BLUE)

    draw(canvas, 2, 1, "A LITTLE LOVE STORY...", PINK)

    ground = height - 5
    draw(canvas, 0, ground, "_" * width, WHITE)

    # Two animated characters
    draw(canvas, left, ground-3, " o ", PINK)
    draw(canvas, left, ground-2, "/|\\", PINK)
    draw(canvas, left, ground-1, "/ \\", PINK)

    draw(canvas, right, ground-3, " o ", RED)
    draw(canvas, right, ground-2, "/|\\", RED)
    draw(canvas, right, ground-1, "/ \\", RED)

    if message:
        draw(canvas, max(0, (width-len(message))//2),
             height-2, message, GOLD)

    clear()
    show(canvas)

def main():
    width, height = shutil.get_terminal_size((80, 25))
    width = max(50, width)

    stars = [
        (random.randint(0, width-1),
         random.randint(2, max(3, height-8)))
        for _ in range(45)
    ]

    center = width // 2

    # Opening scene
    for i in range(35):
        scene(stars, 3, width-7, i, "SOMEWHERE IN THIS UNIVERSE...")
        time.sleep(0.12)

    # Two people walking towards each other
    for i in range(45):
        left = 3 + i
        right = width - 7 - i

        scene(stars, left, right, i,
              "TWO HEARTS... ONE BEAUTIFUL STORY")
        time.sleep(0.12)

    # They meet
    for i in range(20):
        scene(stars, center-4, center+1, i,
              "AND THEN... THEY FOUND EACH OTHER")
        time.sleep(0.15)

    # Big animated heart
    heart = [
        "   ***     ***   ",
        "  *****   *****  ",
        " ***************** ",
        "  *************** ",
        "   *************  ",
        "    ***********   ",
        "      *******     ",
        "       *****      ",
        "        ***       ",
        "         *        "
    ]

    for i in range(35):
        clear()
        width, height = shutil.get_terminal_size((80, 25))
        canvas = [[(" ", RESET) for _ in range(width)]
                  for _ in range(height)]

        for x, y in stars:
            if x < width and y < height:
                draw(canvas, x, y, ".", BLUE)

        scale = 1 + 0.12 * math.sin(i * 0.5)
        for j, line in enumerate(heart):
            draw(canvas, center-10, height//2-7+j,
                 line, RED)

        draw(canvas, center-12, height//2+5,
             "YOU ARE MY FAVOURITE PERSON", PINK)

        show(canvas)
        time.sleep(0.12)

    # Fireworks
    for i in range(45):
        clear()
        width, height = shutil.get_terminal_size((80, 25))
        canvas = [[(" ", RESET) for _ in range(width)]
                  for _ in range(height)]

        for x, y in stars:
            if x < width and y < height:
                draw(canvas, x, y, random.choice([".", "+", "*"]),
                     random.choice([PINK, BLUE, GOLD]))

        for _ in range(35):
            x = random.randint(0, width-1)
            y = random.randint(2, max(3, height-7))
            draw(canvas, x, y, random.choice(["*", "+", "."]),
                 random.choice([RED, PINK, GOLD]))

        draw(canvas, center-10, height//2,
             "I LOVE YOU!!!", RED)
        draw(canvas, center-13, height//2+2,
             "FOREVER AND ALWAYS <3", PINK)

        show(canvas)
        time.sleep(0.15)

    # Final message
    clear()
    print("\n\n")
    print(PINK + "       DEAR YOU..." + RESET)
    time.sleep(1)

    messages = [
        "Out of all the stars in the universe,",
        "I would still choose you.",
        "You are my favourite adventure.",
        "My today, my tomorrow, my forever.",
        "",
        "        I LOVE YOU <3"
    ]

    for message in messages:
        for char in message:
            sys.stdout.write(RED + char + RESET)
            sys.stdout.flush()
            time.sleep(0.055)
        print()
        time.sleep(0.8)

    print(GOLD + "\n       ENDLESS LOVE <3" + RESET)

try:
    main()
except KeyboardInterrupt:
    print(RESET + "\n\nLove you! <3")
