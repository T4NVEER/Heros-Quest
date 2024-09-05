import pygame
import random
import math

from bullet import Bullet
from config import *

class Enemy(pygame.sprite.Sprite):
    def __init__(self, cell_size, map_width, map_height, screen, bullets_group, map_layout, damage):
        super().__init__()
        self.cell_size = cell_size
        self.map_width = map_width
        self.map_height = map_height
        self.screen = screen
        self.bullets_group = bullets_group
        self.map_layout = map_layout
        self.damage = damage

        self.angle = 0
        self.rotation_speed = 3.5
        self.shoot_delay = 1100  # Delay between shots in milliseconds
        self.last_shot_time = pygame.time.get_ticks()  # Initialize the last shot time

        self.sprite = pygame.sprite.Sprite() # Create a Sprite object for the enemy
        self.sprite.rect = pygame.Rect(0, 0, cell_size, cell_size) # Create a rectangle representing the enemy sprite

        self.place_sprite_randomly()  # Place the enemy sprite at a random valid position within the map

    def place_sprite_randomly(self):
        center_x = (self.screen.get_width() - self.map_width) // 2
        center_y = (self.screen.get_height() - self.map_height) // 2

        available_positions = []
        for y, row in enumerate(self.map_layout):
            for x, char in enumerate(row):
                if char == ".":
                    available_positions.append((x * self.cell_size + center_x, y * self.cell_size + center_y))

        random_position = random.choice(available_positions)
        self.sprite.rect.topleft = random_position

    def move_towards_target(self, target_position):
        # Calculate the vector from the enemy to the Hero
        dx = target_position[0] - self.sprite.rect.centerx
        dy = target_position[1] - self.sprite.rect.centery

        # Calculate the distance between the enemy and the Hero
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # Normalize the vector to get the desired direction of movement
        if distance > 0:
            dx /= distance
            dy /= distance

        # Set the maximum speed for movement
        max_speed = 2
        dx *= max_speed
        dy *= max_speed

        # Calculate the new position of the enemy based on the desired velocity
        new_rect = self.sprite.rect.move(dx, dy)

        # Check if the proposed new position is a valid move (no collision with walls)
        if self.is_valid_move(new_rect):
            self.sprite.rect = new_rect

    def move_towards_hero(self, hero_position):
        self.move_towards_target(hero_position)  # Call the move_towards_target function

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

    def shoot_towards_hero(self, hero_position):
        current_time = pygame.time.get_ticks()
        # Check if enough time has passed since the last shot
        if current_time - self.last_shot_time > self.shoot_delay:
            # Calculate the angle and shoot a bullet only if the delay has passed
            dx = hero_position[0] - self.sprite.rect.centerx
            dy = hero_position[1] - self.sprite.rect.centery
            angle_to_hero = math.degrees(math.atan2(-dy, dx))
            self.angle = angle_to_hero
            bullet = Bullet(*self.sprite.rect.center, self.angle, owner=self)
            self.bullets_group.add(bullet)

            self.last_shot_time = current_time  # Update the last shot time

class Enforcer(Enemy):
    def __init__(self, cell_size, map_width, map_height, screen, bullets_group, map_layout):
        super().__init__(cell_size, map_width, map_height, screen, bullets_group, map_layout, damage=20)

        self.sprite_image = pygame.image.load("sprites/enemies/enforcer.png") # Load the enforcer image from the file
        self.sprite_image = pygame.transform.scale(self.sprite_image, (self.cell_size, self.cell_size))
        self.sprite.image = self.sprite_image # Set the image for the enforcer sprite

class Grunt(Enemy):
    def __init__(self, cell_size, map_width, map_height, screen, bullets_group, map_layout):
        super().__init__(cell_size, map_width, map_height, screen, bullets_group, map_layout, damage=35)

        self.sprite_image = pygame.image.load("sprites/enemies/grunt.png") # Load the grunt image from the file
        self.sprite_image = pygame.transform.scale(self.sprite_image, (self.cell_size, self.cell_size))
        self.sprite.image = self.sprite_image # Set the image for the grunt sprite

class Apex(Enemy):
    def __init__(self, cell_size, map_width, map_height, screen, bullets_group, map_layout):
        super().__init__(cell_size, map_width, map_height, screen, bullets_group, map_layout,  damage=50)

        self.sprite_image = pygame.image.load("sprites/enemies/apex.png") # Load the apex image from the file
        self.sprite_image = pygame.transform.scale(self.sprite_image, (self.cell_size, self.cell_size))
        self.sprite.image = self.sprite_image # Set the image for the apex sprite