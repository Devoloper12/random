
import os
import sys
import time
import math
import random
import shutil

# Enable ANSI colors on Windows
os.system("")

PINK = "\033[95m"
RED = "\033[91m"
GOLD = "\033[93m"
RESET = "\033[0m"

def clear():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

def get_size():
    size = shutil.get_terminal_size((80, 25))
    return max(40, size.columns), max(15, size.lines)

def main():
    width, height = get_size()

    hearts = [
        "   **     **   ",
        " *****   ***** ",
        "***************",
        " ************* ",
        "  ***********  ",
        "   *********   ",
        "    *******    ",
        "     *****     ",
        "      ***      ",
        "       *       "
    ]

    particles = [
        [random.randint(0, width - 1),
         random.randint(0, height - 1)]
        for _ in range(30)
    ]

    try:
        for frame in range(180):
            clear()

            width, height = get_size()
            screen = [[" " for _ in range(width)]
                      for _ in range(height)]

            # Floating stars and hearts
            for p in particles:
                x, y = p

                if 0 <= x < width and 0 <= y < height:
                    screen[y][x] = random.choice([".", "*", "+", "♥"])

                p[1] -= 1

                if p[1] < 0:
                    p[0] = random.randint(0, width - 1)
                    p[1] = height - 1

            # Beating heart
            scale = 1 + 0.08 * math.sin(frame * 0.25)
            heart_width = len(hearts[2])
            start_x = max(0, (width - heart_width) // 2)
            start_y = max(0, height // 2 - 6)

            for i, line in enumerate(hearts):
                for j, char in enumerate(line):
                    if char == "*":
                        x = start_x + j
                        y = start_y + i

                        if x < width and y < height:
                            screen[y][x] = "♥"

            output = []

            for row in screen:
                line = ""
                for char in row:
                    if char == "♥":
                        line += RED + "♥" + RESET
                    elif char in ".*+":
                        line += PINK + char + RESET
                    else:
                        line += char
                output.append(line)

            sys.stdout.write("\n".join(output))
            sys.stdout.write(
                "\n" + PINK +
                "       YOU ARE MY UNIVERSE <3" +
                RESET
            )
            sys.stdout.flush()

            time.sleep(0.08)

        clear()

        print(PINK + "\n   A MESSAGE FROM MY HEART...\n" + RESET)
        time.sleep(1)

        messages = [
            "Every heartbeat reminds me of you...",
            "Every moment feels special with you...",
            "You make my world beautiful.",
            "",
            "       I LOVE YOU <3",
            "",
            "       FOREVER & ALWAYS"
        ]

        for message in messages:
            for char in message:
                sys.stdout.write(RED + char + RESET)
                sys.stdout.flush()
                time.sleep(0.06)

            print()
            time.sleep(0.6)

    except KeyboardInterrupt:
        clear()
        print(PINK + "Love you! <3" + RESET)

    finally:
        sys.stdout.write(RESET)
        sys.stdout.flush()

if __name__ == "__main__":
    main()

