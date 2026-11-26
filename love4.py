
import os
import sys
import time
import math
import random
import shutil

os.system("")

R = "\033[91m"
P = "\033[95m"
B = "\033[94m"
C = "\033[96m"
Y = "\033[93m"
W = "\033[97m"
D = "\033[90m"
RESET = "\033[0m"

def size():
    s = shutil.get_terminal_size((80, 25))
    return max(65, min(s.columns, 95)), max(22, min(s.lines, 30))

def screen():
    w, h = size()
    return [[(" ", RESET) for _ in range(w)] for _ in range(h)]

def put(c, x, y, text, color=W):
    for i, ch in enumerate(text):
        if 0 <= y < len(c) and 0 <= x+i < len(c[0]):
            c[y][x+i] = (ch, color)

def center(c, y, text, color=W):
    put(c, max(0, (len(c[0])-len(text))//2), y, text, color)

def render(c):
    sys.stdout.write("\033[H\033[2J")
    for row in c:
        last = None
        for ch, color in row:
            if color != last:
                sys.stdout.write(color)
                last = color
            sys.stdout.write(ch)
        sys.stdout.write(RESET + "\n")
    sys.stdout.flush()

def stars(c, count=35):
    h, w = len(c), len(c[0])
    for _ in range(count):
        x = random.randrange(w)
        y = random.randrange(2, max(3, h-6))
        put(c, x, y, random.choice([".", "+", "*"]), D)

def subtitles(text):
    c = screen()
    center(c, 3, "THE SMILE THAT STARTED EVERYTHING", Y)
    center(c, len(c)-4, text, W)
    render(c)
    time.sleep(1.6)

def title():
    for f in range(35):
        c = screen()
        stars(c, 50)
        center(c, 5, "AN ORIGINAL LOVE STORY", Y)
        center(c, 10, "THE DAY YOU ASKED ME TO SMILE", P)
        center(c, 15, "BASED ON A TRUE STORY", W)
        center(c, 20, "A FILM ABOUT TWO HEARTS", D)
        render(c)
        time.sleep(0.13)

def person(c, x, y, color=P):
    put(c, x+1, y, "O", color)
    put(c, x, y+1, "/|\\", color)
    put(c, x, y+2, "/ \\", color)

def campus():
    w, h = size()
    for f in range(40):
        c = screen()
        stars(c, 15)

        center(c, 2, "SCENE 01 - FIRST YEAR", Y)

        put(c, 3, 7, " ______________________________")
        put(c, 3, 8, "|       COLLEGE CAMPUS         |")
        put(c, 3, 9, "|______________________________|")

        put(c, 0, h-6, "_"*w)

        person(c, 5+f, h-9, C)
        person(c, w-12, h-9, P)

        center(c, 4, "A NORMAL DAY. AN UNEXPECTED MEETING.")
        render(c)
        time.sleep(0.12)

    subtitles("And then she asked a simple question...")

    c = screen()
    stars(c, 20)
    person(c, 22, 9, C)
    person(c, 39, 9, P)
    center(c, 3, "THE FIRST CONVERSATION", Y)
    center(c, 19, '"WHY DON\'T YOU SMILE?"', P)
    render(c)
    time.sleep(2)

    subtitles("You smiled and explained about your teeth aligner.")
    subtitles("Neither of you knew what was about to begin.")

def friendship():
    for f in range(45):
        c = screen()
        stars(c, 25)
        center(c, 2, "SCENE 02 - THE FRIENDSHIP", Y)

        center(c, 7, "MONDAY  -  CONVERSATIONS")
        center(c, 10, "TUESDAY -  LAUGHTER")
        center(c, 13, "WEDNESDAY - MORE TALKS")

        center(c, 17, "MESSAGE AFTER MESSAGE...")
        center(c, 20, "FRIENDS BECAME BEST FRIENDS.")

        # Animated message bubbles
        x = 5 + (f % 20)
        put(c, x, 23, "<3", P)
        put(c, len(c[0])-x-3, 23, "<3", R)

        render(c)
        time.sleep(0.14)

    subtitles("Somewhere between all those conversations...")
    subtitles("She became your favourite person.")

def hackathon():
    for f in range(45):
        c = screen()
        stars(c, 12)

        center(c, 2, "SCENE 03 - THE HACKATHON", Y)
        center(c, 6, "THE GREAT CODING NIGHT", C)

        put(c, 5, 9, " __________________")
        put(c, 5, 10, "| >_ HELLO WORLD  |")
        put(c, 5, 11, "|________________|")
        put(c, 9, 12, "|______|")

        put(c, len(c[0])-24, 9, " __________________")
        put(c, len(c[0])-24, 10, "| >_ BUILDING LOVE |")
        put(c, len(c[0])-24, 11, "|_________________|")

        center(c, 16, "IDEAS. DEADLINES. LAUGHTER.")
        center(c, 19, "AND SOMETHING MORE...")
        center(c, 22, "THEY FELL IN LOVE.", P)

        render(c)
        time.sleep(0.15)

    subtitles("The hackathon changed everything.")
    subtitles("Best friends. Two hearts. One feeling.")

def countdown():
    for number in ["3", "2", "1"]:
        c = screen()
        center(c, 5, "THREE DAYS LATER...", Y)
        center(c, 12, number, R)
        render(c)
        time.sleep(0.9)

def car():
    w, h = size()

    for f in range(45):
        c = screen()
        stars(c, 25)

        center(c, 2, "SCENE 04 - THREE DAYS LATER", Y)
        center(c, 5, "A QUIET EVENING...", C)

        # Road
        put(c, 0, h-5, "_"*w, D)

        # Car body
        x = w//2-17
        put(c, x+6, 11, "  ___________________")
        put(c, x+2, 12, " /                   \\")
        put(c, x, 13, "|                     |")
        put(c, x, 14, "|_____________________|")
        put(c, x+5, 15, "O                   O", Y)

        center(c, 19, "HE HAD SOMETHING TO SAY...")
        center(c, 22, "BUT HIS HEART WAS RACING.", P)

        render(c)
        time.sleep(0.14)

    subtitles("A deep breath...")
    subtitles("A nervous smile...")
    subtitles("And finally, the words came out.")

def proposal():
    w, h = size()

    for f in range(35):
        c = screen()
        stars(c, 35)

        center(c, 2, "SCENE 05 - THE PROPOSAL", Y)

        person(c, w//2-13, 10, C)

        # Kneeling character
        put(c, w//2+5, 11, "O", P)
        put(c, w//2+3, 12, "/|__")
        put(c, w//2+3, 13, "/ \\")

        center(c, 6, "WILL YOU BE MINE?", P)

        if f % 4 == 0:
            center(c, 17, "<3", R)

        render(c)
        time.sleep(0.15)

    subtitles("You finally proposed...")
    subtitles("And waited for her answer.")

def hug():
    w, h = size()

    for f in range(40):
        c = screen()
        stars(c, 50)

        center(c, 2, "SCENE 06 - THE ANSWER", Y)

        # Two characters move together
        x1 = w//2-14 + min(f//3, 5)
        x2 = w//2+9 - min(f//3, 5)

        person(c, x1, 10, C)
        person(c, x2, 10, P)

        if f > 17:
            center(c, 7, "<3     <3     <3", R)

        center(c, 20, "SHE HUGGED YOU.", P)
        center(c, 22, "AND THAT WAS EVERYTHING.", W)

        render(c)
        time.sleep(0.15)

    subtitles("The hug you will never forget.")
    subtitles("Two hearts finally found their home.")

def ending():
    for f in range(35):
        c = screen()
        stars(c, 70)

        center(c, 4, "SCENE 07 - TOGETHER", Y)
        center(c, 9, "TWO BEST FRIENDS")
        center(c, 12, "TWO HEARTS")
        center(c, 15, "ONE PROMISE")
        center(c, 19, "A LOVE STORY JUST BEGINNING", P)

        render(c)
        time.sleep(0.14)

    os.system("cls" if os.name == "nt" else "clear")
    time.sleep(0.7)

    print("\n")
    print(Y + "       THE END... OR JUST THE BEGINNING?" + RESET)
    time.sleep(1.5)

    messages = [
        "It started with a question.",
        "Why don't you smile?",
        "",
        "Then came friendship.",
        "Then came a thousand conversations.",
        "Then came one unforgettable hackathon.",
        "",
        "Three days later...",
        "One car. One proposal. One hug.",
        "",
        "And a promise to stay together.",
        "",
        "If I could live this story again...",
        "I would still choose you.",
        "",
        "        I LOVE YOU.",
        "        FOREVER & ALWAYS."
    ]

    for msg in messages:
        for ch in msg:
            sys.stdout.write(P + ch + RESET)
            sys.stdout.flush()
            time.sleep(0.045)
        print()
        time.sleep(0.65)

    print("\n" + Y + "          ROLL CREDITS <3" + RESET)

try:
    title()
    campus()
    friendship()
    hackathon()
    countdown()
    car()
    proposal()
    hug()
    ending()

except KeyboardInterrupt:
    print(RESET + "\nTHE STORY CONTINUES...")

finally:
    sys.stdout.write(RESET)
    sys.stdout.flush()
