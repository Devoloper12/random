
import os
import time
import random
import sys

# Enable colors in Windows CMD and PowerShell
os.system("")

RESET = "\033[0m"
RED = "\033[91m"
PINK = "\033[95m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
WHITE = "\033[97m"
BLUE = "\033[94m"


# ---------------- BASIC FUNCTIONS ----------------

def clear():
    print("\033[2J\033[H", end="", flush=True)


def wait(seconds=1):
    time.sleep(seconds)


def center(text=""):
    print(str(text).center(72))


def line():
    print(PINK + "=" * 72 + RESET)


def speak(name, message, color=WHITE):
    print()
    print()
    center(YELLOW + message + RESET)
    wait(1.8)



def transition():
    for i in range(1, 5):
        clear()
        center(PINK + "." * i + RESET)
        wait(0.25)



def scene_heading(number, name):
    clear()
    line()
    center(PINK + name + RESET)
    line()
    wait(1.5)


# ---------------- HEART ANIMATION ----------------

def heart_animation():
    heart = [
        "       **     **       ",
        "     ****** ******     ",
        "    ***************    ",
        "     *************     ",
        "       *********       ",
        "         *****         ",
        "           *           "
    ]

    for i in range(3):
        clear()
        print()

        for row in heart:
            center(RED + row + RESET)

        center(PINK + "A LOVE STORY" + RESET)
        wait(0.5)


# ---------------- SCENE 1 ----------------

def campus():
    scene_heading(1, "THE FIRST MEETING")

    frames = [
        [
            "          __________________________",
            "         |                          |",
            "         |          COLLEGE         |",
            "         |__________________________|",
            "",
            "                 O          O",
            "                /|\\        /|\\",
            "                / \\        / \\",
        ],
        [
            "          __________________________",
            "         |                          |",
            "         |          COLLEGE         |",
            "         |__________________________|",
            "",
            "                 O -----> O",
            "                /|\\        /|\\",
            "                / \\        / \\",
        ]
    ]

    for frame in frames:
        clear()

        for row in frame:
            center(CYAN + row + RESET)

        wait(1.2)

    speak("GIRL", "Nee entha chirikkathe?", PINK)

    speak("BOY", "Ente teeth aligner kaaranam...", CYAN)

    speak("GIRL", "Athinentha? Chirichude!", PINK)

   clear();
center(GREEN + "And that was the beginning..." + RESET)
wait(3)


# ---------------- SCENE 2 ----------------

def friendship():
    scene_heading(2, "A BEAUTIFUL FRIENDSHIP")

    frames = [
        [
            "             O                    O",
            "            /|\\                  /|\\",
            "            / \\                  / \\",
            "",
            "                 TWO FRIENDS",
        ],
        [
            "                O              O",
            "               /|\\            /|\\",
            "               / \\            / \\",
            "",
            "                ALWAYS TOGETHER",
        ],
        [
            "                    O      O",
            "                   /|\\    /|\\",
            "                   / \\    / \\",
            "",
            "                  BEST FRIENDS",
        ]
    ]

    for frame in frames:
        clear()

        for row in frame:
            center(PINK + row + RESET)

        wait(1.2)

    speak("BOY", "Nammal ippo nalla friends alle?", CYAN)

    speak("GIRL", "Athe... nalla friends!", PINK)

    speak("BOY", "Ninakku oppam irikkumbol time pokunnathu ariyilla.", CYAN)

    clear()
    center(GREEN + "Days passed... and their bond grew stronger." + RESET)
    wait(3)


# ---------------- SCENE 3 ----------------

def hackathon():
    scene_heading(3, "THE HACKATHON")

    frames = [
        [
            "       ______________________________",
            "      |                              |",
            "      |          HACKATHON           |",
            "      |______________________________|",
            "",
            "             O              O",
            "            /|\\            /|\\",
            "            / \\            / \\",
        ],
        [
            "       ______________________________",
            "      |                              |",
            "      |           TEAM WORK          |",
            "      |______________________________|",
            "",
            "                 O      O",
            "                /|\\    /|\\",
            "                / \\    / \\",
        ]
    ]

    for frame in frames:
        clear()

        for row in frame:
            center(CYAN + row + RESET)

        wait(1.2)

    speak("BOY", "Ninne kandappol muthal entho oru special feeling aanu.", CYAN)

    speak("GIRL", "Enikkum angane thanne thonnunnu...", PINK)

    clear()
    center(RED + "SOME FEELINGS NEED NO WORDS..." + RESET)
    wait(3)

    heart_animation()


# ---------------- SCENE 4 ----------------

def three_days():
    scene_heading(4, "THREE DAYS LATER")

    for i in range(5, 0, -1):
        clear()

        center(YELLOW + "3 DAYS LATER..." + RESET)
        center("")
        center(WHITE + "Something special is about to happen..." + RESET)
        center(RED + str(i) + RESET)

        wait(0.8)


# ---------------- SCENE 5 ----------------

def car_scene():
    scene_heading(5, "THE MOMENT IN THE CAR")

    frames = [
        [
            "          __________________________",
            "         /                          \\",
            "        /____________________________\\",
            "        |                            |",
            "        |       O          O         |",
            "        |      /|\\        /|\\        |",
            "        |      / \\        / \\        |",
            "        |____________________________|",
            "            O                    O",
        ],
        [
            "          __________________________",
            "         /                          \\",
            "        /____________________________\\",
            "        |                            |",
            "        |        O       O           |",
            "        |       /|\\     /|\\          |",
            "        |       / \\     / \\          |",
            "        |____________________________|",
            "            O                    O",
        ]
    ]

    for frame in frames:
        clear()

        for row in frame:
            center(BLUE + row + RESET)

        wait(1.2)

    speak("BOY", "Enikk ninne orupaadu ishtamaanu.", CYAN)

    speak("BOY", "Ente life-il nee undaakanamennu njan aagrahikkunnu.", CYAN)

    clear()
    center(RED + "HEARTBEAT..." + RESET)
    wait(1)

    center(RED + "HEARTBEAT..." + RESET)
    wait(1)

    speak("BOY", "Will you be mine?", YELLOW)


# ---------------- SCENE 6 ----------------

def proposal():
    scene_heading(6, "THE PROPOSAL")

    for i in range(1, 5):
        clear()

        center(YELLOW + "THE MOST IMPORTANT QUESTION..." + RESET)
        print()
        center(RED + "WILL YOU BE MINE?" + RESET)
        print()
        center(PINK + "<3 " * i + RESET)

        wait(0.8)

    speak("GIRL", "Yes...", PINK)

    speak("GIRL", "Njanum ninne orupaadu ishtappedunnu.", PINK)

    heart_animation()


# ---------------- SCENE 7 ----------------

def hug():
    scene_heading(7, "THE FIRST HUG")

    frames = [
        [
            "             O                 O",
            "            /|\\               /|\\",
            "            / \\               / \\",
        ],
        [
            "                 O     O",
            "                /|\\   /|\\",
            "                / \\   / \\",
        ],
        [
            "                   O-O",
            "                  /|X|\\",
            "                   / \\",
            "",
            "                  FOREVER",
        ]
    ]

    for frame in frames:
        clear()

        for row in frame:
            center(RED + row + RESET)

        wait(1.2)

    center(PINK + "A hug that said everything..." + RESET)
    wait(3)


# ---------------- FINAL SCENE ----------------

def ending():
    clear()

    heart_animation()
    transition()

    clear()

    line()

    center(YELLOW + "THE END... OR JUST THE BEGINNING?" + RESET)

    print()

    center(PINK + "Ann thudangiya friendship..." + RESET)

    center(PINK + "Innu oru beautiful love story aayi." + RESET)

    print()

    center(RED + "TWO HEARTS. ONE LOVE. FOREVER." + RESET)

    print()

    center(WHITE + "Some stories are written by destiny." + RESET)

    center(WHITE + "This one is written by two hearts." + RESET)

    print()

    center(RED + "<3  <3  <3  <3  <3" + RESET)

    line()

    wait(5)


# ---------------- PLAY THE MOVIE ----------------

def movie():
    try:
        clear()

        heart_animation()

        campus()
        transition()

        friendship()
        transition()

        hackathon()
        transition()

        three_days()

        car_scene()
        transition()

        proposal()

        hug()

        ending()

        clear()
        center(GREEN + "THANK YOU FOR WATCHING!" + RESET)

    except KeyboardInterrupt:
        clear()
        print("Movie stopped.")


if __name__ == "__main__":
    movie()
