import pygame
import random
import math

from bullet import Bullet
from config import *

class Hero:
    def __init__(self, cell_size, map_width, map_height, screen, bullets_group, map_layout):
        # Store the values which will be passed as arguments in GameWindow
        self.cell_size = cell_size
        self.map_width = map_width
        self.map_height = map_height
        self.screen = screen
        self.bullets_group = bullets_group
        self.map_layout = map_layout
        self.bullet_count = 10

        # Set initial angle and rotation speed
        self.angle = 0
        self.rotation_speed = 3.5

        # Concurrent health and maximum health
        self.health = 100
        self.max_health = 100

        self.health_bar_width = 200  # Health bar width
        self.health_bar_height = 40  # Health bar width
        self.health_bar_color = (0, 255, 0)  # Green color

        # Load the sprite image and create a Sprite object
        self.sprite_image = pygame.image.load("sprites/hero/hero.png")
        self.sprite_image = pygame.transform.scale(self.sprite_image, (self.cell_size, self.cell_size))
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = self.sprite_image
        self.sprite.rect = self.sprite.image.get_rect()
        self.sprite.rect.topleft = (self.cell_size, self.cell_size)

        # Place the hero's sprite at a random valid position within the map
        self.place_sprite_randomly()

        self.lives = 3  # Number of lives
        self.heart_image = pygame.image.load("sprites/health/red_heart.png")  # Load the heart icon
        self.heart_image = pygame.transform.scale(self.heart_image, (80, 60))  # Resize the heart icon

    def draw_hearts(self):
        heart_x = self.screen.get_width() - 80  # X-coordinate for the first heart icon
        heart_y = 10  # Y-coordinate for all heart icons

        for heart in range(self.lives):
            self.screen.blit(self.heart_image, (heart_x, heart_y))
            heart_x -= 50  # Move to the left for the next heart icon

    def decrease_health(self, damage):
        self.health -= damage
        if self.health <= 0: # If health is 0, respawn the Hero and reset the bar to maximum health
            if self.lives > 0:
                self.lives -= 1
                self.respawn()
                self.health_bar_width = 200
        else:
            # Update health bar width based on remaining health in proportion to the width of the health bar
            self.health_bar_width = (self.health / self.max_health) * 200

    def respawn(self):
        self.health = 100  # Reset hero's health
        self.place_sprite_randomly()

    def place_sprite_randomly(self):
        # Calculate the position to center the map_layout on the screen
        center_x = (self.screen.get_width() - self.map_width) // 2
        center_y = (self.screen.get_height() - self.map_height) // 2

        # Get a list of available floor positions in the map
        available_positions = []
        for y, row in enumerate(self.map_layout):
            for x, char in enumerate(row):
                if char == ".":
                    available_positions.append((x * self.cell_size + center_x, y * self.cell_size + center_y))

        random_position = random.choice(available_positions) # Randomly select a position from the available positions list
        self.sprite.rect.topleft = random_position # Set the position of the sprite

    def update_sprite_angle(self):
        keys = pygame.key.get_pressed() # Get the keys currently pressed by the user
        if keys[pygame.K_LEFT]: # Check if the left arrow key is pressed
            self.angle += self.rotation_speed # Rotate the sprite to the left by increasing the angle
        elif keys[pygame.K_RIGHT]: # Check if the right arrow key is pressed
            self.angle -= self.rotation_speed # Rotate the sprite to the right by decreasing the angle

        self.angle %= 360 # Ensure the angle stays within 360 degrees

    def is_valid_move(self, new_rect):
        # Calculate the centering offsets for the map_layout on the screen
        center_x = (self.screen.get_width() - self.map_width) // 2
        center_y = (self.screen.get_height() - self.map_height) // 2

        # Check if the proposed new_rect collides with any wall in the map_layout
        for y, row in enumerate(self.map_layout):
            for x, char in enumerate(row):
                if char == "#":  # If the character is '#', it represents a wall
                    # Create a rectangle representing the wall at the current position (x, y)
                    wall_rect = pygame.Rect(x * self.cell_size + center_x, y * self.cell_size + center_y,
                                            self.cell_size, self.cell_size)
                    if new_rect.colliderect(wall_rect): # Check if the new rectangle collides with the wall
                        return False  # Collision with a wall, so the move is not valid
        return True  # No collision with any wall, so the move is valid

    def update_sprite_position(self):
        keys = pygame.key.get_pressed()
        movement_speed = 0.1  # Adjust this value to control the movement speed (smaller value means slower movement)

        if keys[pygame.K_UP]: # Check if the up arrow key is pressed
            rad_angle = math.radians(self.angle)  # Convert the angle from degrees to radians
            dx = math.cos(rad_angle)  # Calculate the change in the x-coordinate
            dy = -math.sin(rad_angle)  # Calculate the change in the y-coordinate

            # Calculate the proposed new position for the sprite
            new_rect = self.sprite.rect.move(dx * self.cell_size * movement_speed, dy * self.cell_size * movement_speed)
            # Check if the proposed new position is a valid move (no collision with walls)
            if self.is_valid_move(new_rect):
                self.sprite.rect = new_rect  # Update the sprite's position

        # Check if the down arrow key is pressed
        elif keys[pygame.K_DOWN]:
            rad_angle = math.radians(self.angle)  # Convert the angle from degrees to radians
            dx = -math.cos(rad_angle)  # Calculate the change in the x-coordinate
            dy = math.sin(rad_angle)  # Calculate the change in the y-coordinate

            # Calculate the proposed new position for the sprite
            new_rect = self.sprite.rect.move(dx * self.cell_size * movement_speed, dy * self.cell_size * movement_speed)
            # Check if the proposed new position is a valid move (no collision with walls)
            if self.is_valid_move(new_rect):
                self.sprite.rect = new_rect  # Update the sprite's position

        elif keys[pygame.K_m] and self.bullet_count > 0:  # Check if 'm' is pressed and the Hero has bullets
            bullet = Bullet(*self.sprite.rect.center, self.angle, owner=self)  # Create a new Bullet object
            self.bullets_group.add(bullet)  # Add the bullet to the bullets_group
            self.bullet_count -= 1  # Decrease the bullet count

    def gain_health(self):
        self.health += 10
        self.health_bar_width = (self.health / self.max_health) * 200
        if self.health > self.max_health:
            self.health = self.max_health