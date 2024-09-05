import sys
from PyQt5.QtWidgets import QApplication
from start_menu import StartMenu
from config import *


def main():
    app = QApplication(sys.argv)

    # Start the game UI (Start Menu)
    start_menu = StartMenu()
    start_menu.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
