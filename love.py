
import os
import sys
import time
import math
import random
import shutil

PINK = "\033[95m"
RED = "\033[91m"
GOLD = "\033[93m"
RESET = "\033[0m"

def main():
    os.system("")
    width, height = shutil.get_terminal_size((80, 25))
    width = max(40, width)
    height = max(15, height)

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

    particles = [
        [random.randint(0, width - 1),
         random.randint(0, height - 1)]
        for _ in range(25)
    ]

    try:
        for frame in range(200):
            width, height = shutil.get_terminal_size((80, 25))
            screen = [[" " for _ in range(width)]
                      for _ in range(height)]

            for p in particles:
                x, y = p
                if 0 <= x < width and 0 <= y < height:
                    screen[y][x] = random.choice([".", "+", "*"])

                p[1] -= 1
                if p[1] < 0:
                    p[0] = random.randint(0, width - 1)
                    p[1] = height - 1

            start_x = max(0, (width - 11) // 2)
            start_y = max(0, height // 2 - 5)

            pulse = 1 + 0.1 * math.sin(frame * 0.2)

            for i, line in enumerate(heart):
                for j, char in enumerate(line):
                    if char == "*":
                        x = start_x + j
                        y = start_y + i
                        if x < width and y < height:
                            screen[y][x] = "#"

            sys.stdout.write("\033[H\033[2J")

            for row in screen:
                output = ""
                for char in row:
                    if char == "#":
                        output += RED + char + RESET
                    elif char in ".*+":
                        output += PINK + char + RESET
                    else:
                        output += char
                print(output)

            print(PINK + "\n       YOU ARE MY UNIVERSE <3" + RESET)
            time.sleep(0.08)

        print("\n" + GOLD + "   A MESSAGE FROM MY HEART..." + RESET)
        time.sleep(1)

        messages = [
            "Every heartbeat reminds me of you...",
            "You make my world beautiful.",
            "You are my favourite person.",
            "",
            "       I LOVE YOU <3",
            "       FOREVER & ALWAYS"
        ]

        for message in messages:
            for char in message:
                sys.stdout.write(RED + char + RESET)
                sys.stdout.flush()
                time.sleep(0.06)
            print()
            time.sleep(0.7)

    except KeyboardInterrupt:
        print("\nLove you! <3")

    finally:
        print(RESET)

if __name__ == "__main__":
    main()
