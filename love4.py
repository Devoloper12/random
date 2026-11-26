
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
GREEN = "\033[92m"
RESET = "\033[0m"

def dimensions():
    s = shutil.get_terminal_size((80, 25))
    return max(60, min(s.columns, 95)), max(20, min(s.lines, 30))

def new_screen():
    w, h = dimensions()
    return [[" " for _ in range(w)] for _ in range(h)]

def put(screen, x, y, text):
    for i, ch in enumerate(text):
        if 0 <= y < len(screen) and 0 <= x+i < len(screen[0]):
            screen[y][x+i] = ch

def center(screen, y, text):
    x = max(0, (len(screen[0])-len(text))//2)
    put(screen, x, y, text)

def render(screen, color=WHITE):
    sys.stdout.write("\033[H\033[2J")
    sys.stdout.write(color)
    for row in screen:
        sys.stdout.write("".join(row) + "\n")
    sys.stdout.write(RESET)
    sys.stdout.flush()

def pause(t=0.12):
    time.sleep(t)

def stars(screen, count=35):
    h, w = len(screen), len(screen[0])
    for _ in range(count):
        x = random.randrange(w)
        y = random.randrange(max(1, h-4))
        screen[y][x] = random.choice([".", "*", "+"])

def dialogue(speaker, message, color=PINK):
    screen = new_screen()
    stars(screen, 20)
    center(screen, 5, "A LITTLE CONVERSATION...")
    center(screen, 10, speaker)
    center(screen, 12, '"' + message + '"')
    render(screen, color)
    pause(1.8)

def type_message(message, color=PINK, delay=0.045):
    for char in message:
        sys.stdout.write(color + char + RESET)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def title_scene():
    for f in range(20):
        s = new_screen()
        stars(s, 45)
        center(s, 5, "A STORY THAT CHANGED EVERYTHING")
        center(s, 10, "COLLEGE. FRIENDSHIP. LOVE.")
        center(s, 15, "A TRUE LOVE STORY")
        render(s, PINK)
        pause(0.18)

    pause(1)

def college_scene():
    w, h = dimensions()
    ground = h-7

    for f in range(36):
        s = new_screen()
        stars(s, 12)

        center(s, 2, "COLLEGE - FIRST YEAR")
        put(s, 2, ground, "_"*(w-4))

        left = 3 + f
        right = w-8

        put(s, left, ground-3, " O ")
        put(s, left, ground-2, "/|\\")
        put(s, left, ground-1, "/ \\")

        put(s, right, ground-3, " O ")
        put(s, right, ground-2, "/|\\")
        put(s, right, ground-1, "/ \\")

        center(s, 5, "TWO PEOPLE. ONE UNEXPECTED MEETING.")
        render(s, WHITE)
        pause(0.14)

    dialogue("HER", "Why don't you smile?")
    dialogue("YOU", "Because of my teeth aligner.")

    s = new_screen()
    center(s, 7, "SHE SMILED...")
    center(s, 10, "AND SO DID YOUR STORY.")
    render(s, GOLD)
    pause(2)

def friendship_scene():
    w, h = dimensions()

    for f in range(35):
        s = new_screen()
        stars(s, 22)

        center(s, 3, "DAYS TURNED INTO CONVERSATIONS...")
        center(s, 7, "MESSAGES")
        center(s, 9, "LAUGHTER")
        center(s, 11, "LITTLE JOKES")
        center(s, 13, "ENDLESS TALKS")

        x = int(w/2 + math.sin(f/3)*15)
        center(s, 17, "BEST FRIENDS <3")

        put(s, max(0, x-3), 19, "<3")
        render(s, PINK)
        pause(0.15)

    dialogue("HER", "You are my best friend.")
    dialogue("YOU", "And you are mine.")

def hackathon_scene():
    w, h = dimensions()

    for f in range(38):
        s = new_screen()
        stars(s, 15)

        center(s, 2, "THE HACKATHON")
        center(s, 5, "IDEAS. CODE. COFFEE. DEADLINES.")

        # Laptops
        center(s, 10, "  __________________     __________________")
        center(s, 11, " |  >_ CODE MODE   |   |  >_ BUILD MODE  |")
        center(s, 12, " |_________________|   |_________________|")
        center(s, 13, "       |____|                  |____|")

        center(s, 16, "BUT SOMETHING ELSE WAS HAPPENING...")
        center(s, 19, "TWO BEST FRIENDS...")
        center(s, 21, "FALLING IN LOVE.")

        if f % 2 == 0:
            center(s, 24, "<3     <3     <3")

        render(s, CYAN)
        pause(0.15)

    dialogue("YOUR HEART", "Wait... am I falling in love?")
    dialogue("HER HEART", "I think I am too.")

    s = new_screen()
    center(s, 8, "THE HACKATHON WAS OVER...")
    center(s, 11, "BUT YOUR LOVE STORY HAD JUST BEGUN.")
    render(s, RED)
    pause(2)

def countdown_scene():
    for n in ["3", "2", "1"]:
        s = new_screen()
        center(s, 7, "THREE DAYS LATER...")
        center(s, 13, n)
        render(s, GOLD)
        pause(0.9)

    s = new_screen()
    center(s, 10, "THE DAY YOU DECIDED TO TELL HER.")
    render(s, PINK)
    pause(2)

def car_scene():
    w, h = dimensions()

    for f in range(30):
        s = new_screen()
        stars(s, 35)

        center(s, 3, "A QUIET EVENING...")
        center(s, 8, "        __________________")
        center(s, 9, "   ____/                  \\____")
        center(s, 10, "  |       YOUR CAR              |")
        center(s, 11, "  |_____________________________|")
        center(s, 12, "     O                      O")

        center(s, 16, "YOUR HEART WAS BEATING FAST...")
        center(s, 19, "YOU HAD SOMETHING TO SAY.")
        render(s, BLUE)
        pause(0.18)

    dialogue("YOU", "I have something to tell you...")
    dialogue("YOU", "I think I have fallen in love with you.")

def proposal_scene():
    w, h = dimensions()

    for f in range(35):
        s = new_screen()
        stars(s, 30)

        center(s, 3, "THE MOMENT OF TRUTH")

        # Two characters
        put(s, w//2-13, 12, " O")
        put(s, w//2-14, 13, "/|\\")
        put(s, w//2-14, 14, "/ \\")

        # Kneeling character
        put(s, w//2+7, 13, " o")
        put(s, w//2+5, 14, "/|__")
        put(s, w//2+5, 15, "/ \\")

        if f % 3 == 0:
            center(s, 8, "<3")
        else:
            center(s, 8, "  *")

        center(s, 19, "WILL YOU BE MINE?")
        render(s, RED)
        pause(0.16)

    dialogue("YOU", "Will you be mine forever?")

    s = new_screen()
    center(s, 8, "SHE LOOKED AT YOU...")
    center(s, 11, "AND THEN...")
    render(s, GOLD)
    pause(2)

def hug_scene():
    w, h = dimensions()

    for f in range(30):
        s = new_screen()
        stars(s, 35)

        center(s, 3, "SHE MOVED CLOSER...")
        center(s, 10, "       \\ O /")
        center(s, 11, "        \\|/")
        center(s, 12, "         |")
        center(s, 13, "        / \\")
        center(s, 17, "         <3")

        render(s, PINK)
        pause(0.15)

    for f in range(20):
        s = new_screen()
        stars(s, 45)

        center(s, 6, "       O---O")
        center(s, 7, "       /\\_/\\")
        center(s, 8, "        / \\")

        center(s, 13, "SHE HUGGED YOU.")
        center(s, 16, "AND THAT WAS YOUR ANSWER.")
        render(s, RED)
        pause(0.2)

    dialogue("YOUR HEART", "I wish this moment lasted forever.")

def commitment_scene():
    w, h = dimensions()

    for f in range(40):
        s = new_screen()
        stars(s, 50)

        center(s, 4, "AND JUST LIKE THAT...")
        center(s, 9, "TWO BEST FRIENDS")
        center(s, 11, "BECAME TWO PEOPLE IN LOVE.")
        center(s, 15, "COMMITTED. TOGETHER.")
        center(s, 19, "<3       <3       <3")

        render(s, PINK if f % 2 else RED)
        pause(0.15)

def finale():
    s = new_screen()
    stars(s, 60)
    center(s, 5, "THE END?")
    center(s, 9, "NO...")
    center(s, 13, "JUST THE BEGINNING.")
    render(s, GOLD)
    pause(2)

    os.system("cls" if os.name == "nt" else "clear")

    print("\n")
    print(PINK + "       THE SMILE THAT STARTED EVERYTHING" + RESET)
    print("\n")

    messages = [
        "It all started with one question...",
        "",
        '"Why don\'t you smile?"',
        "",
        "Then came the conversations.",
        "Then came the friendship.",
        "Then came the hackathon.",
        "Then came the feelings.",
        "",
        "Three days later...",
        "A car. A proposal. A hug.",
        "",
        "And two hearts chose each other.",
        "",
        "Our story started with your question.",
        "And I hope it never ends.",
        "",
        "        I LOVE YOU <3",
        "",
        "        FOREVER YOURS."
    ]

    for line in messages:
        type_message(line, RED if "LOVE" in line else PINK)
        pause(0.5)

    print("\n" + GOLD + "     TO BE CONTINUED..." + RESET)

try:
    title_scene()
    college_scene()
    friendship_scene()
    hackathon_scene()
    countdown_scene()
    car_scene()
    proposal_scene()
    hug_scene()
    commitment_scene()
    finale()

except KeyboardInterrupt:
    print(RESET + "\n\nOUR STORY CONTINUES <3")

finally:
    sys.stdout.write(RESET)
    sys.stdout.flush()
