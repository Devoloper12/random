import os
import time
import random

# Enable ANSI colors in Windows CMD and PowerShell
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


# Names are deliberately not displayed; only the dialogue appears.
def speak(message, color=WHITE):
    print()
    center(color + '"' + message + '"' + RESET)
    wait(1.8)


def transition():
    for i in range(1, 5):
        clear()
        center(PINK + "." * i + RESET)
        wait(0.25)


# Display only the scene title, without scene numbers.
def scene_heading(name):
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

    for _ in range(3):
        clear()
        print()
        for row in heart:
            center(RED + row + RESET)
        center(PINK + "A LOVE STORY" + RESET)
        wait(0.5)


# ---------------- FIRST MEETING ----------------

def campus():
    scene_heading("THE FIRST MEETING")

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

    speak("Nee entha chirikkathe?", PINK)
    speak("Ente teeth aligner kaaranam...", CYAN)
    speak("Athinentha? Chirichude!", PINK)

    clear()
    center(GREEN + "And that was the beginning..." + RESET)
    wait(3)


# ---------------- FRIENDSHIP ----------------

def friendship():
    scene_heading("A BEAUTIFUL FRIENDSHIP")

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

    speak("Nammal ippo nalla friends alle?", CYAN)
    speak("Athe... nalla friends!", PINK)
    speak("Ninakku oppam irikkumbol time pokunnathu ariyilla.", CYAN)

    clear()
    center(GREEN + "Days passed... and their bond grew stronger." + RESET)
    wait(3)


# ---------------- HACKATHON ----------------

def hackathon():
    scene_heading("THE HACKATHON")

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

    speak("Ninne kandappol muthal entho oru special feeling aanu.", CYAN)
    speak("Enikkum angane thanne thonnunnu...", PINK)

    clear()
    center(RED + "SOME FEELINGS NEED NO WORDS..." + RESET)
    wait(3)
    heart_animation()


# ---------------- THREE DAYS LATER ----------------

def three_days():
    scene_heading("THREE DAYS LATER")

    for i in range(5, 0, -1):
        clear()
        center(YELLOW + "3 DAYS LATER..." + RESET)
        center("")
        center(WHITE + "Something special is about to happen..." + RESET)
        center(RED + str(i) + RESET)
        wait(0.8)


# ---------------- THE CAR ----------------

def car_scene():
    scene_heading("THE MOMENT IN THE CAR")

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

    speak("Enikk ninne orupaadu ishtamaanu.", CYAN)
    speak("Ente life-il nee undaakanamennu njan aagrahikkunnu.", CYAN)

    clear()
    center(RED + "HEARTBEAT..." + RESET)
    wait(1)
    center(RED + "HEARTBEAT..." + RESET)
    wait(1)

    speak("Will you be mine?", YELLOW)


# ---------------- PROPOSAL ----------------

def proposal():
    scene_heading("THE PROPOSAL")

    for i in range(1, 5):
        clear()
        center(YELLOW + "THE MOST IMPORTANT QUESTION..." + RESET)
        print()
        center(RED + "WILL YOU BE MINE?" + RESET)
        print()
        center(PINK + "<3 " * i + RESET)
        wait(0.8)

    speak("Yes...", PINK)
    speak("Njanum ninne orupaadu ishtappedunnu.", PINK)
    heart_animation()


# ---------------- THE HUG ----------------

def hug():
    scene_heading("THE FIRST HUG")

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


# ---------------- ENDING ----------------

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
