import pygame
import math

from config import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, owner):
        super().__init__()
        self.image = pygame.image.load("sprites/bullets/bullets.png")  # Load the bullet image from the file
        self.image = pygame.transform.scale(self.image, (10, 10))  # Resize the bullet image to (10, 10)
        self.rect = self.image.get_rect()  # Get the rectangle for the bullet image
        self.rect.center = (x, y)  # Set the starting position of the bullet at the given (x, y) coordinates
        self.angle = angle  # Store the initial angle of the bullet (direction it will move)
        self.speed = 5  # Speed of the bullet#
        self.spawn_time = pygame.time.get_ticks()  # Store the time when the bullet was created
        self.collision_delay = 300  # Delay in milliseconds
        self.owner = owner # Assigned to the entity which fires the bullet

    def update(self):
        # Remove the bullet if it has exceeded the 10-second duration
        if pygame.time.get_ticks() - self.spawn_time >= 10000:
            self.kill()

        rad_angle = math.radians(self.angle)  # Convert the angle from degrees to radians (since we're using trig)
        # Calculate the change in x and y coordinates based on the angle and speed
        dx = math.cos(rad_angle) * self.speed
        dy = -math.sin(rad_angle) * self.speed
        self.rect.x += dx  # Move the bullet horizontally (change its x-coordinate)
        self.rect.y += dy  # Move the bullet vertically (change its y-coordinate)
