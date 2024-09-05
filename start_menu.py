import sqlite3
import hashlib
import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from game import GameWindow

class StartMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Hero's Quest - Start Menu")
        self.showFullScreen()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)  # Center the buttons vertically

        title_label = QLabel("Hero's Quest")
        title_label.setFont(QFont("Arial", 36))
        layout.addWidget(title_label)

        button_width = 400  # Width for all buttons
        button_height = 100  # Height for all buttons
        spacing = 50  # Increased spacing between buttons
        top_margin = 150  # A top margin to bring all buttons down

        start_button = QPushButton("Start Game", self)
        start_button.clicked.connect(self.start_game)
        start_button.setFixedHeight(button_height)
        start_button.setFixedWidth(button_width)

        user_guide_button = QPushButton("User Guide", self)
        user_guide_button.clicked.connect(self.user_guide)
        user_guide_button.setFixedHeight(button_height)
        user_guide_button.setFixedWidth(button_width)

        register_button = QPushButton("Register", self)
        register_button.clicked.connect(self.registration)
        register_button.setFixedHeight(button_height)
        register_button.setFixedWidth(button_width)

        sign_in_button = QPushButton("Sign-in", self)
        sign_in_button.clicked.connect(self.sign_in)
        sign_in_button.setFixedHeight(button_height)
        sign_in_button.setFixedWidth(button_width)

        layout.addSpacing(top_margin)  # A top margin to push all buttons down
        layout.addWidget(start_button)
        layout.addSpacing(spacing)
        layout.addWidget(user_guide_button)
        layout.addSpacing(spacing)
        layout.addWidget(register_button)
        layout.addSpacing(spacing)
        layout.addWidget(sign_in_button)

        self.setLayout(layout)

    def start_game(self):
        self.game_window = GameWindow()
        self.game_window.run()
        global start_time
        start_time = time.time()

    def user_guide(self):
        self.user_guide_window = UserGuideWindow()
        self.user_guide_window.show()

    def registration(self):
        self.register_window = RegisterWindow()
        self.register_window.show()

    def sign_in(self):
        self.sign_in_window = SignInWindow()
        self.sign_in_window.show()

class UserGuideWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("User Guide")
        self.setGeometry(1250, 200, 600, 400)

        layout = QVBoxLayout()

        guide_label = QLabel(
            """
            Welcome to Hero's Quest.

            In this game, there are 5 levels. Your aim is to complete these levels with the Hero 
            in the lowest possible time but there are measures in place to try and slow you down.

            In each map, there are 2 bullet drops. The hero spawns with an initial 10 bullets and each bullet drop 
            gives 10 more bullets. It's up to you to keep count of your bullets so you know how many you have left.

            In each map, there are multiple ladders. Only one ladder is real and this ladder will take you to the 
            next level; all the other ladders are decoys and will simply waste your time.

            In each map, there are also multiple enemies. There are three types of enemies: Enforcers, Grunts, and Apexes. 
            These enemies will shoot bullets at you. Some of these will do more damage than others.

            To move the Hero, firstly rotate your Hero to look in the direction you want to travel; this can be done by using the left or 
            right arrow keys. The up and down arrow keys will move the hero up and down with respect to the direction the Hero is facing.

            Hope you enjoy.
            """
        )

        layout.addWidget(guide_label)

        self.setLayout(layout)

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Register")
        self.setGeometry(700, 300, 500, 300)

        layout = QVBoxLayout()

        username_label = QLabel("Username:")
        self.username_input = QLineEdit()

        email_label = QLabel("Email:")
        self.email_input = QLineEdit()

        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        layout.addWidget(username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)

        register_button = QPushButton("Register")
        register_button.clicked.connect(self.register_user)
        layout.addWidget(register_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def register_user(self):
        username = self.username_input.text()
        email = self.email_input.text()
        password = self.password_input.text()

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        connection = sqlite3.connect("user_data.db")
        cursor = connection.cursor()

        cursor.execute("SELECT email FROM users WHERE email=?", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            connection.close()
            QMessageBox.warning(self, "Registration Failed", "This email is already registered.")
        else:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password_hash))
            connection.commit()
            connection.close()

            self.close()

            QMessageBox.information(self, "Registration Success", "Your registration was successful!")

class SignInWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sign-In")
        self.setGeometry(700, 300, 500, 300)

        layout = QVBoxLayout()

        username_email_label = QLabel("Username/Email:")
        self.username_email_input = QLineEdit()

        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        layout.addWidget(username_email_label)
        layout.addWidget(self.username_email_input)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)

        sign_in_button = QPushButton("Sign-In")
        sign_in_button.clicked.connect(self.SignInValidation)
        layout.addWidget(sign_in_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def SignInValidation(self):
        global username_email
        username_email = self.username_email_input.text()
        password = self.password_input.text()
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        connection = sqlite3.connect("user_data.db")
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM users WHERE (username=? OR email=?) AND password=?", (username_email, username_email, password_hash))
        user_data = cursor.fetchone()
        connection.close()

        if user_data:
            QMessageBox.information(self, "Sign-In Success", "You have successfully signed in!")
            global logged_in
            logged_in = True
            self.close()
        else:
            QMessageBox.warning(self, "Sign-In Failed", "Invalid username/email or password.")
