
import os
import sys
import time
import math
import random
import shutil

PINK = "\033[95m"
RED = "\033[91m"
RESET = "\033[0m"

def main():
    os.system("")
    width, height = shutil.get_terminal_size((80, 25))

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

    stars = [
        [random.randrange(width), random.randrange(height)]
        for _ in range(30)
    ]

    try:
        for frame in range(250):
            width, height = shutil.get_terminal_size((80, 25))
            screen = [[" " for _ in range(width)]
                      for _ in range(height)]

            for star in stars:
                x, y = star
                if x < width and y < height:
                    screen[y][x] = random.choice([".", "+", "*"])

                star[1] -= 1
                if star[1] < 0:
                    star[0] = random.randrange(width)
                    star[1] = height - 1

            x0 = max(0, (width - 11) // 2)
            y0 = max(0, (height - 10) // 2)

            for i, line in enumerate(heart):
                for j, char in enumerate(line):
                    if char == "*":
                        x, y = x0 + j, y0 + i
                        if x < width and y < height:
                            screen[y][x] = "#"

            sys.stdout.write("\033[H\033[2J")

            for row in screen:
                for char in row:
                    if char == "#":
                        sys.stdout.write(RED + "#" + RESET)
                    elif char in ".*+":
                        sys.stdout.write(PINK + char + RESET)
                    else:
                        sys.stdout.write(char)
                sys.stdout.write("\n")

            sys.stdout.write(
                PINK + "\n       YOU ARE MY UNIVERSE <3\n" + RESET
            )
            sys.stdout.flush()
            time.sleep(0.08)

        print("\n" + RED + "I LOVE YOU!" + RESET)

    except KeyboardInterrupt:
        print("\nLove you!")

if __name__ == "__main__":
    main()
