import sqlite3
import time
import pygame
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from config import *


class GameOverWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Over") # Window title
        self.showFullScreen() # Show the window in full-screen mode

        layout = QVBoxLayout() # Create a vertical layout for the window's contents

        # Create a label for the "Game Over" message, set font, add the label to screen
        game_over_label = QLabel("Game Over")
        game_over_label.setFont(QFont("Arial", 30))
        # Align the label to be slightly lower and center horizontally
        layout.addWidget(game_over_label, alignment=Qt.AlignVCenter | Qt.AlignHCenter)

        losingMessage_label = QLabel("Unlucky, you lost! Try again") # Create a label for the losing message
        losingMessage_label.setFont(QFont("Arial", 24)) # Set the font for the label
        losingMessage_label.setStyleSheet("color: red;") # Set the colour for the label
        layout.addWidget(losingMessage_label, alignment=Qt.AlignHCenter) # Align the losing message label to the center horizontally

        backToMenu_button = QPushButton("Back to Start Menu") # Create a button to go back to the Start Menu
        backToMenu_button.clicked.connect(self.close_window) # When button is clicked, it calls close_window method
        backToMenu_button.setMinimumSize(350, 100) # Dimensions of button
        layout.addWidget(backToMenu_button, alignment=Qt.AlignCenter) # Add the button to layout and align it in the center
        self.setLayout(layout) # Set the layout for the window

    def close_window(self):  # Close the Game Over window when the button is clicked
        self.close()

        global running
        running = False

class winning_GameOverWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Over") # Window title
        self.showFullScreen() # Show the window in full-screen mode

        global start_time
        self.elapsed_time = round(time.time() - start_time)

        self.update_leaderboard()
        self.remove_duplicates()

        layout = QVBoxLayout() # Create a vertical layout for the window's contents

        # Create a label for the "Game Over" message, set font, add the label to screen
        game_over_label = QLabel("Congratulations, you have finished the game!")
        game_over_label.setFont(QFont("Arial", 30))
        # Align the label to be slightly lower and center horizontally
        layout.addWidget(game_over_label, alignment=Qt.AlignVCenter | Qt.AlignHCenter)

        winningMessage_label = QLabel(f'You finished in {self.elapsed_time} seconds', self) # Create a label for the losing message
        winningMessage_label.setFont(QFont("Arial", 24)) # Set the font for the label
        winningMessage_label.setStyleSheet("color: green;") # Set the colour for the label
        layout.addWidget(winningMessage_label, alignment=Qt.AlignHCenter) # Align the losing message label to the center horizontally

        leaderboard_label = QLabel("Leaderboard:", self)
        leaderboard_label.setFont(QFont("Arial", 24))
        layout.addWidget(leaderboard_label, alignment=Qt.AlignHCenter)

        # Retrieve top 5 fastest times and usernames from the leaderboard
        top_5_records = self.get_top_5_leaderboard()

        # Display top 5 fastest times and usernames in a QLabel
        leaderboard_text = "\n".join([f"{username}: {time} seconds" for username, time in top_5_records])
        leaderboard_display_label = QLabel(leaderboard_text, self)
        leaderboard_display_label.setFont(QFont("Arial", 20))
        layout.addWidget(leaderboard_display_label, alignment=Qt.AlignHCenter)

        backToMenu_button = QPushButton("Back to Start Menu") # Create a button to go back to the Start Menu
        backToMenu_button.clicked.connect(self.close_window) # When button is clicked, it calls close_window method
        backToMenu_button.setMinimumSize(350, 100) # Dimensions of button
        layout.addWidget(backToMenu_button, alignment=Qt.AlignCenter) # Add the button to layout and align it in the center
        self.setLayout(layout) # Set the layout for the window

    def close_window(self):  # Close the Game Over window and then set running = False when the button is clicked
        self.close()

        global running
        running = False
        global current_level
        current_level = 1

    def update_leaderboard(self):
        global logged_in # Indicates whether a user is logged in or not
        global username_email # Stores the username or email of the user

        # Check if a user is logged in
        if logged_in == True:
            # If logged in, connect to the user_data.db database
            connection = sqlite3.connect("user_data.db")
            cursor = connection.cursor()

            # Insert the logged-in user's username/email and elapsed time into the leaderboard table
            cursor.execute("INSERT INTO leaderboard (Username, Time_taken) VALUES (?, ?)",

                           (username_email, self.elapsed_time,))
            # Commit the changes and close the database connection
            connection.commit()
            connection.close()
        else:
            # If not logged in, connect to the user_data.db database
            connection = sqlite3.connect("user_data.db")
            cursor = connection.cursor()

            # Insert "Unnamed" as the username and elapsed time into the leaderboard table
            cursor.execute("INSERT INTO leaderboard (Username, Time_taken) VALUES (?, ?)",
                           ("Unnamed", self.elapsed_time,))

            # Commit the changes and close the database connection
            connection.commit()
            connection.close()

    def remove_duplicates(self):
        # Connect to the SQLite database named "user_data.db"
        connection = sqlite3.connect("user_data.db")
        cursor = connection.cursor()

        # Execute a SQL query to delete duplicate records from the "leaderboard" table
        cursor.execute("""
            DELETE FROM leaderboard 
            WHERE (Username, Time_taken) IN ( 
                SELECT Username, Time_taken -- Selects duplicate Username and Time_taken pairs 
                FROM leaderboard 
                GROUP BY Username, Time_taken -- Groups records by Username and Time_taken and selects only duplicates
                HAVING COUNT(*) > 1 -- Filters groups to include only those with more than one record
            )
        """)

        # Commit the changes to the database and close the connection
        connection.commit()
        connection.close()

    def get_top_5_leaderboard(self):
        # Connect to the SQLite database named "user_data.db"
        connection = sqlite3.connect("user_data.db")
        cursor = connection.cursor()

        # Execute an SQL query to retrieve the top 5 fastest times and usernames from the leaderboard
        cursor.execute("""
            SELECT Username, Time_taken
            FROM leaderboard
            ORDER BY Time_taken ASC
            LIMIT 5
        """)

        # Fetch all the records obtained from the query
        top_5_records = cursor.fetchall()

        # Close the database connection
        connection.close()

        # Return the top 5 records retrieved from the leaderboard
        return top_5_records
