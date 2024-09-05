import pygame
from pygame.locals import *
import random
import math

from hero import Hero
from enemies import Grunt, Enforcer, Apex
from bullet import Bullet
from game_over_window import *
from config import *

class GameWindow:
    def __init__(self):
        # Initialize pygame and set up the game window
        pygame.init()
        info = pygame.display.Info()  # Get display info
        self.screen = pygame.display.set_mode((info.current_w, info.current_h), FULLSCREEN)  # Make window full screen
        pygame.display.set_caption("Hero's Quest - Game Window")  # Set the window title
        self.clock = pygame.time.Clock()  # Create a clock to control the frame rate

        #Map layout
        self.map_layout = MAP_LAYOUT

        # Set up the map_layout properties
        self.cell_size = 40  # Adjust this value to change the size of each cell
        self.map_width = len(self.map_layout[0]) * self.cell_size  # Calculate the width of the map
        self.map_height = len(self.map_layout) * self.cell_size  # Calculate the height of the map
        self.wall_color = pygame.Color("Gray")  # Color for walls
        self.floor_color = pygame.Color("white")  # Color for floor

        self.bullets_group = pygame.sprite.Group()
        # Create instance of the Hero
        self.hero = Hero(self.cell_size, self.map_width, self.map_height, self.screen, self.bullets_group, self.map_layout)

        self.enemy_classes = [Grunt, Enforcer, Apex] # List of enemy classes

        # Create instances of two random enemy children
        self.enemies_group = pygame.sprite.Group()
        self.enemy_1 = random.choice(self.enemy_classes)(self.cell_size, self.map_width, self.map_height, self.screen, self.bullets_group, self.map_layout)
        self.enemies_group.add(self.enemy_1)
        self.enemy_2 = random.choice(self.enemy_classes)(self.cell_size, self.map_width, self.map_height, self.screen, self.bullets_group, self.map_layout)
        self.enemies_group.add(self.enemy_2)

        # Number of real ladders that will spawn
        self.num_real_ladders = 1

        # Generate random real ladder position
        self.real_ladder_position = []
        while len(self.real_ladder_position) < self.num_real_ladders:
            x = random.randint(0, len(self.map_layout[0]) - 1)
            y = random.randint(0, len(self.map_layout) - 1)
            if self.map_layout[y][x] == ".":
                self.real_ladder_position.append((x, y))

        # Number of decoy ladders that will spawn
        self.num_decoy_ladders = 1  # Change this to control the number of decoy ladders

        # Generate random decoy ladder positions
        self.decoy_ladder_positions = []
        while len(self.decoy_ladder_positions) < self.num_decoy_ladders:
            x = random.randint(0, len(self.map_layout[0]) - 1)
            y = random.randint(0, len(self.map_layout) - 1)
            if self.map_layout[y][x] == ".":
                self.decoy_ladder_positions.append((x, y))

        # Load the ladder image and scale it
        self.ladder_image = pygame.image.load("sprites/ladder/ladder.png")
        self.ladder_image = pygame.transform.scale(self.ladder_image, (self.cell_size, self.cell_size))

        # Number of bullet drops that will spawn on the map
        self.num_bullet_drops = 2

        # List to store the positions of bullet drops
        self.bullet_drops = []
        # Loop to randomly generate 'num_bullet_drops' many positions
        while len(self.bullet_drops) < self.num_bullet_drops:
            # Generate random x and y coordinates within the map boundaries
            x = random.randint(0, len(self.map_layout[0]) - 1)
            y = random.randint(0, len(self.map_layout) - 1)
            # Check if the selected position is on an empty floor tile (represented by ".")
            if self.map_layout[y][x] == ".":
                # If it's a valid position, add it to the list of bullet drops
                self.bullet_drops.append((x, y))

        self.bullet_drop_image = pygame.image.load("sprites/bullets/bullet_drop.png")
        self.bullet_drop_image = pygame.transform.scale(self.bullet_drop_image, (35, 35))

    def draw_map(self):
        # Calculate the position to center the map_layout on the screen
        center_x = (self.screen.get_width() - self.map_width) // 2
        center_y = (self.screen.get_height() - self.map_height) // 2

        for y, row in enumerate(self.map_layout):
            for x, char in enumerate(row):
                if char == "#":
                    pygame.draw.rect(self.screen, self.wall_color, (
                    x * self.cell_size + center_x, y * self.cell_size + center_y, self.cell_size, self.cell_size))
                elif char == ".":
                    pygame.draw.rect(self.screen, self.floor_color, (
                    x * self.cell_size + center_x, y * self.cell_size + center_y, self.cell_size, self.cell_size))
        for x, y in self.real_ladder_position:
            self.screen.blit(self.ladder_image, (
                x * self.cell_size + center_x, y * self.cell_size + center_y))
        for x, y in self.decoy_ladder_positions:
            self.screen.blit(self.ladder_image, (
                x * self.cell_size + center_x, y * self.cell_size + center_y))

        for x, y in self.bullet_drops:
            self.screen.blit(self.bullet_drop_image, (
                x * self.cell_size + center_x, y * self.cell_size + center_y))

    def draw_bullets(self):  # Draw all bullets in the bullets_group on the screen
        for bullet in self.bullets_group.sprites():
            self.screen.blit(bullet.image, bullet.rect)

    def handle_bullet_collision(self):
        # Calculate the position to center the map_layout on the screen
        center_x = (self.screen.get_width() - self.map_width) // 2
        center_y = (self.screen.get_height() - self.map_height) // 2

        for bullet in self.bullets_group.sprites():
            new_rect = bullet.rect.move(bullet.speed * math.cos(math.radians(bullet.angle)),
                                        -bullet.speed * math.sin(math.radians(bullet.angle)))

            # Check if the new rectangle collides with any wall in the map
            for y, row in enumerate(self.map_layout):
                for x, char in enumerate(row):
                    if char == "#":
                        wall_rect = pygame.Rect(x * self.cell_size + center_x, y * self.cell_size + center_y,
                                                self.cell_size, self.cell_size)
                        if new_rect.colliderect(wall_rect):
                            # Determine the wall's orientation (horizontal or vertical)
                            horizontal_wall = abs(bullet.rect.centery - wall_rect.centery) > abs(
                                bullet.rect.centerx - wall_rect.centerx)

                            # Handle ricochet based on wall orientation
                            if horizontal_wall:
                                # Colliding with a horizontal wall, reverse the vertical component of velocity
                                bullet.angle = -bullet.angle
                            else:
                                # Colliding with a vertical wall, reverse the horizontal component of velocity
                                bullet.angle = 180 - bullet.angle

                            break  # Stop checking for collisions with other walls

    def move_enemies_towards_hero(self):
        # Get the position of the Hero sprite's center
        hero_position = self.hero.sprite.rect.center

        # Loop through each enemy (self.enemy_1 and self.enemy_2) in a list of enemies
        for enemy in self.enemies_group:
            # Move the current enemy towards the hero's position
            enemy.move_towards_hero(hero_position)

            # Check if the enemy is close enough to the hero to shoot a bullet (using Pythagoras Theorem)
            distance_to_hero = math.sqrt((hero_position[0] - enemy.sprite.rect.centerx) ** 2 +
                                         (hero_position[1] - enemy.sprite.rect.centery) ** 2)
            if distance_to_hero < 150:
                enemy.shoot_towards_hero(hero_position)

    def handle_sprite_collisions(self):
        current_time = pygame.time.get_ticks()

        for bullet in self.bullets_group:
            if current_time - bullet.spawn_time > bullet.collision_delay:
                if bullet.rect.colliderect(self.hero.sprite.rect):
                    # Check the bullet's owner and apply damage accordingly
                    if isinstance(bullet.owner, Hero):
                        damage = 20 # Hero's bullets do 20 damage
                    else:
                        damage = bullet.owner.damage  # Use the enemy's specific damage value
                    self.hero.decrease_health(damage)  # Decrease hero's health when hit by a bullet
                    bullet.kill() # Remove bullet from screen

            # Check bullet-enemy collisions and remove enemies if they collide with bullets
            for enemy in self.enemies_group:
                if current_time - bullet.spawn_time > bullet.collision_delay:
                    if bullet.rect.colliderect(enemy.sprite.rect):
                        bullet.kill()
                        enemy.kill()
                        self.hero.gain_health()

    def show_game_over_window(self):
        self.game_over_window = GameOverWindow()
        global running
        running = False
        self.game_over_window.show()

    def show_winning_game_over_window(self):
        self.game_over_window = winning_GameOverWindow()
        global running
        running = False
        self.game_over_window.show()

    def check_bullet_drop_collisions(self):
        # Calculate the position to center the map_layout on the screen
        center_x = (self.screen.get_width() - self.map_width) // 2
        center_y = (self.screen.get_height() - self.map_height) // 2

        for bullet_drop_x, bullet_drop_y in self.bullet_drops:
            bullet_drop_rect = pygame.Rect(bullet_drop_x * self.cell_size + center_x, bullet_drop_y * self.cell_size + center_y,
                                      self.cell_size, self.cell_size)
            if self.hero.sprite.rect.colliderect(bullet_drop_rect):
                self.hero.bullet_count += 10
                self.bullet_drops.remove((bullet_drop_x, bullet_drop_y))

    def check_ladder_collisions(self):
        # Calculate the position to center the map_layout on the screen
        center_x = (self.screen.get_width() - self.map_width) // 2
        center_y = (self.screen.get_height() - self.map_height) // 2

        for ladder_x, ladder_y in self.real_ladder_position:
            ladder_rect = pygame.Rect(ladder_x * self.cell_size + center_x, ladder_y * self.cell_size + center_y,
                                      self.cell_size, self.cell_size)
            if self.hero.sprite.rect.colliderect(ladder_rect):
                global go_to_next_level
                go_to_next_level = True

    def next_level(self):
        global current_level
        if current_level == 1:
            current_level += 1
            Level_2().run()
        elif current_level == 2:
            current_level += 1
            Level_3().run()
        elif current_level == 3:
            current_level += 1
            Level_4().run()
        elif current_level == 4:
            current_level += 1
            Level_5().run()
        elif current_level == 5:
            current_level += 1

    def run(self):
        global running
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: # Check if the user closed the window
                    running = False # If the window is closed, stop the game loop

            global go_to_next_level
            global current_level
            # Handle user input to update sprite angle and position including bullet position and bullet-wall collisions
            self.hero.update_sprite_angle()
            self.hero.update_sprite_position()
            self.handle_bullet_collision()
            self.bullets_group.update()
            self.check_ladder_collisions()
            self.check_bullet_drop_collisions()

            # Move enemies towards the hero
            self.move_enemies_towards_hero()

            self.handle_sprite_collisions()

            # Set the background color to white
            self.screen.fill((255, 255, 255))

            self.draw_map() # Draw the map layout on the screen
            rotated_sprite = pygame.transform.rotate(self.hero.sprite.image, self.hero.angle) # Rotate the Hero sprite by the angle specified in `self.angle'
            rotated_rect = rotated_sprite.get_rect(center=self.hero.sprite.rect.center) # Ensure rotation is about the Hero's center and it doesn't drift when rotating
            self.screen.blit(rotated_sprite, rotated_rect) # Draw the rotated Hero sprite on the screen
            self.draw_bullets()  # Draw bullets on the screen

            # Draw the enemies on the screen
            for enemy in self.enemies_group:
                self.screen.blit(enemy.sprite.image, enemy.sprite.rect)

            pygame.draw.rect(self.screen, (255, 0, 0), (10, 10, 200, 40))  # Red background
            pygame.draw.rect(self.screen, self.hero.health_bar_color,
                             (10, 10, self.hero.health_bar_width, 40))  # Green health bar
            self.hero.draw_hearts()

            pygame.display.flip()  # Update the display
            self.clock.tick(30)  # Limit the frame rate to 30 frames per second

            if self.hero.lives == 0:
                current_level = 1
                self.hero.lives = 3
                self.show_game_over_window()

            if go_to_next_level == True:
                go_to_next_level = False
                running = False
                self.next_level()
                if current_level == 6:
                    self.show_winning_game_over_window()

        pygame.quit()

class Level_2(GameWindow):
    def __init__(self):
        # Initialize pygame and set up the game window
        pygame.init()
        info = pygame.display.Info()  # Get display info
        self.screen = pygame.display.set_mode((info.current_w, info.current_h), FULLSCREEN)  # Make window full screen
        pygame.display.set_caption("Hero's Quest - Level 2")  # Set the window title
        self.clock = pygame.time.Clock()  # Create a clock to control the frame rate

        # Map layout
        self.map_layout = MAP_LAYOUT_2

        # Set up the map_layout properties
        self.cell_size = 40  # Adjust this value to change the size of each cell
        self.map_width = len(self.map_layout[0]) * self.cell_size  # Calculate the width of the map
        self.map_height = len(self.map_layout) * self.cell_size  # Calculate the height of the map
        self.wall_color = pygame.Color("Gray")  # Color for walls
        self.floor_color = pygame.Color("white")  # Color for floor

        self.bullets_group = pygame.sprite.Group()
        # Create instance of the Hero
        self.hero = Hero(self.cell_size, self.map_width, self.map_height, self.screen, self.bullets_group,
                         self.map_layout)

        self.enemy_classes = [Grunt, Enforcer, Apex]  # List of enemy classes
        self.enemies_group = pygame.sprite.Group()

        num_enemies = random.randint(2, 3) # Generates a random number from 2 to 3 inclusive

        for index in range(num_enemies):
            random_enemy_class = random.choice(self.enemy_classes)  # Randomly select an enemy class
            enemy_instance = random_enemy_class(self.cell_size, self.map_width, self.map_height, self.screen,
                                                self.bullets_group, self.map_layout)  # Create an enemy object
            self.enemies_group.add(enemy_instance)  # Add the enemy object to the enemies group

        # Number of ladders that will spawn
        self.num_real_ladders = 1

        # Generate random ladder positions
        self.real_ladder_position = []
        while len(self.real_ladder_position) < self.num_real_ladders:
            x = random.randint(0, len(self.map_layout[0]) - 1)
            y = random.randint(0, len(self.map_layout) - 1)
            if self.map_layout[y][x] == ".":
                self.real_ladder_position.append((x, y))

        # Define the number of decoy ladders you want to spawn
        self.num_decoy_ladders = 1  # Change this to control the number of decoy ladders

        # Generate random decoy ladder positions
        self.decoy_ladder_positions = []
        while len(self.decoy_ladder_positions) < self.num_decoy_ladders:
            x = random.randint(0, len(self.map_layout[0]) - 1)
            y = random.randint(0, len(self.map_layout) - 1)
            if self.map_layout[y][x] == ".":
                self.decoy_ladder_positions.append((x, y))

        # Load the ladder image and scale it
        self.ladder_image = pygame.image.load("sprites/ladder/ladder.png")
        self.ladder_image = pygame.transform.scale(self.ladder_image, (self.cell_size, self.cell_size))

        # Number of bullet drops that will spawn on the map
        self.num_bullet_drops = 2

        # List to store the positions of bullet drops
        self.bullet_drops = []
        # Loop to randomly generate 'num_bullet_drops' many positions
        while len(self.bullet_drops) < self.num_bullet_drops:
            # Generate random x and y coordinates within the map boundaries
            x = random.randint(0, len(self.map_layout[0]) - 1)
            y = random.randint(0, len(self.map_layout) - 1)
            # Check if the selected position is on an empty floor tile (represented by ".")
            if self.map_layout[y][x] == ".":
                # If it's a valid position, add it to the list of bullet drops
                self.bullet_drops.append((x, y))

        self.bullet_drop_image = pygame.image.load("sprites/bullets/bullet_drop.png")
        self.bullet_drop_image = pygame.transform.scale(self.bullet_drop_image, (35, 35))

class Level_3(GameWindow):
    def __init__(self):
        # Initialize pygame and set up the game window
        pygame.init()
        info = pygame.display.Info()  # Get display info
        self.screen = pygame.display.set_mode((info.current_w, info.current_h), FULLSCREEN)  # Make window full screen
        pygame.display.set_caption("Hero's Quest - Level 3")  # Set the window title
        self.clock = pygame.time.Clock()  # Create a clock to control the frame rate

        # Map layout
        self.map_layout = MAP_LAYOUT_3

        # Set up the map_layout properties
        self.cell_size = 40  # Adjust this value to change the size of each cell
        self.map_width = len(self.map_layout[0]) * self.cell_size  # Calculate the width of the map
        self.map_height = len(self.map_layout) * self.cell_size  # Calculate the height of the map
        self.wall_color = pygame.Color("Gray")  # Color for walls
        self.floor_color = pygame.Color("white")  # Color for floor

        self.bullets_group = pygame.sprite.Group()
        # Create instance of the Hero
        self.hero = Hero(self.cell_size, self.map_width, self.map_height, self.screen, self.bullets_group,
                         self.map_layout)

        self.enemy_classes = [Grunt, Enforcer, Apex]  # List of enemy classes
        self.enemies_group = pygame.sprite.Group()

        num_enemies = random.randint(2, 3) # Generates a random number from 2 to 3 inclusive

        for index in range(num_enemies):
            random_enemy_class = random.choice(self.enemy_classes)  # Randomly select an enemy class
            enemy_instance = random_enemy_class(self.cell_size, self.map_width, self.map_height, self.screen,
                                                self.bullets_group, self.map_layout)  # Create an enemy object
            self.enemies_group.add(enemy_instance)  # Add the enemy object to the enemies group

        # Number of ladders that will spawn
        self.num_real_ladders = 1

        # Generate random ladder positions
        self.real_ladder_position = []
        while len(self.real_ladder_position) < self.num_real_ladders:
            x = random.randint(0, len(self.map_layout[0]) - 1)
            y = random.randint(0, len(self.map_layout) - 1)
            if self.map_layout[y][x] == ".":
                self.real_ladder_position.append((x, y))

        # Define the number of decoy ladders you want to spawn
        self.num_decoy_ladders = random.randint(1, 2)  # Change this to control the number of decoy ladders

        # Generate random decoy ladder positions
        self.decoy_ladder_positions = []
        while len(self.decoy_ladder_positions) < self.num_decoy_ladders:
            x = random.randint(0, len(self.map_layout[0]) - 1)
            y = random.randint(0, len(self.map_layout) - 1)
            if self.map_layout[y][x] == ".":
                self.decoy_ladder_positions.append((x, y))

        # Load the ladder image and scale it
        self.ladder_image = pygame.image.load("sprites/ladder/ladder.png")
        self.ladder_image = pygame.transform.scale(self.ladder_image, (self.cell_size, self.cell_size))

        # Number of bullet drops that will spawn on the map
        self.num_bullet_drops = 2

        # List to store the positions of bullet drops
        self.bullet_drops = []
        # Loop to randomly generate 'num_bullet_drops' many positions
        while len(self.bullet_drops) < self.num_bullet_drops:
            # Generate random x and y coordinates within the map boundaries
            x = random.randint(0, len(self.map_layout[0]) - 1)
            y = random.randint(0, len(self.map_layout) - 1)
            # Check if the selected position is on an empty floor tile (represented by ".")
            if self.map_layout[y][x] == ".":
                # If it's a valid position, add it to the list of bullet drops
                self.bullet_drops.append((x, y))

        self.bullet_drop_image = pygame.image.load("sprites/bullets/bullet_drop.png")
        self.bullet_drop_image = pygame.transform.scale(self.bullet_drop_image, (35, 35))

class Level_4(GameWindow):
    def __init__(self):
        # Initialize pygame and set up the game window
        pygame.init()
        info = pygame.display.Info()  # Get display info
        self.screen = pygame.display.set_mode((info.current_w, info.current_h), FULLSCREEN)  # Make window full screen
        pygame.display.set_caption("Hero's Quest - Level 4")  # Set the window title
        self.clock = pygame.time.Clock()  # Create a clock to control the frame rate

        # Map layout
        self.map_layout = MAP_LAYOUT_4

        # Set up the map_layout properties
        self.cell_size = 40  # Adjust this value to change the size of each cell
        self.map_width = len(self.map_layout[0]) * self.cell_size  # Calculate the width of the map
        self.map_height = len(self.map_layout) * self.cell_size  # Calculate the height of the map
        self.wall_color = pygame.Color("Gray")  # Color for walls
        self.floor_color = pygame.Color("white")  # Color for floor

        self.bullets_group = pygame.sprite.Group()
        # Create instance of the Hero
        self.hero = Hero(self.cell_size, self.map_width, self.map_height, self.screen, self.bullets_group,
                         self.map_layout)

        self.enemy_classes = [Grunt, Enforcer, Apex]  # List of enemy classes
        self.enemies_group = pygame.sprite.Group()

        num_enemies = random.randint(3, 4)  # Generates a random number from 3 to 4 inclusive

        for index in range(num_enemies):
            random_enemy_class = random.choice(self.enemy_classes)  # Randomly select an enemy class
            enemy_instance = random_enemy_class(self.cell_size, self.map_width, self.map_height, self.screen,
                                                self.bullets_group, self.map_layout)  # Create an enemy object
            self.enemies_group.add(enemy_instance)  # Add the enemy object to the enemies group

        # Number of ladders that will spawn
        self.num_real_ladders = 1

        # Generate random ladder positions
        self.real_ladder_position = []
        while len(self.real_ladder_position) < self.num_real_ladders:
            x = random.randint(0, len(self.map_layout[0]) - 1)
            y = random.randint(0, len(self.map_layout) - 1)
            if self.map_layout[y][x] == ".":
                self.real_ladder_position.append((x, y))

        # Define the number of decoy ladders you want to spawn
        self.num_decoy_ladders = random.randint(2, 3)  # Change this to control the number of decoy ladders

        # Generate random decoy ladder positions
        self.decoy_ladder_positions = []
        while len(self.decoy_ladder_positions) < self.num_decoy_ladders:
            x = random.randint(0, len(self.map_layout[0]) - 1)
            y = random.randint(0, len(self.map_layout) - 1)
            if self.map_layout[y][x] == ".":
                self.decoy_ladder_positions.append((x, y))

        # Load the ladder image and scale it
        self.ladder_image = pygame.image.load("sprites/ladder/ladder.png")
        self.ladder_image = pygame.transform.scale(self.ladder_image, (self.cell_size, self.cell_size))

        # Number of bullet drops that will spawn on the map
        self.num_bullet_drops = 2

        # List to store the positions of bullet drops
        self.bullet_drops = []
        # Loop to randomly generate 'num_bullet_drops' many positions
        while len(self.bullet_drops) < self.num_bullet_drops:
            # Generate random x and y coordinates within the map boundaries
            x = random.randint(0, len(self.map_layout[0]) - 1)
            y = random.randint(0, len(self.map_layout) - 1)
            # Check if the selected position is on an empty floor tile (represented by ".")
            if self.map_layout[y][x] == ".":
                # If it's a valid position, add it to the list of bullet drops
                self.bullet_drops.append((x, y))

        self.bullet_drop_image = pygame.image.load("sprites/bullets/bullet_drop.png")
        self.bullet_drop_image = pygame.transform.scale(self.bullet_drop_image, (35, 35))

class Level_5(GameWindow):
    def __init__(self):
        # Initialize pygame and set up the game window
        pygame.init()
        info = pygame.display.Info()  # Get display info
        self.screen = pygame.display.set_mode((info.current_w, info.current_h), FULLSCREEN)  # Make window full screen
        pygame.display.set_caption("Hero's Quest - Level 5")  # Set the window title
        self.clock = pygame.time.Clock()  # Create a clock to control the frame rate

        # Map layout
        self.map_layout = MAP_LAYOUT_5

        # Set up the map_layout properties
        self.cell_size = 40  # Adjust this value to change the size of each cell
        self.map_width = len(self.map_layout[0]) * self.cell_size  # Calculate the width of the map
        self.map_height = len(self.map_layout) * self.cell_size  # Calculate the height of the map
        self.wall_color = pygame.Color("Gray")  # Color for walls
        self.floor_color = pygame.Color("white")  # Color for floor

        self.bullets_group = pygame.sprite.Group()
        # Create instance of the Hero
        self.hero = Hero(self.cell_size, self.map_width, self.map_height, self.screen, self.bullets_group,
                         self.map_layout)

        self.enemy_classes = [Grunt, Enforcer, Apex]  # List of enemy classes
        self.enemies_group = pygame.sprite.Group()

        num_enemies = random.randint(4, 5)  # Generates a random number from 3 to 4 inclusive

        for index in range(num_enemies):
            random_enemy_class = random.choice(self.enemy_classes)  # Randomly select an enemy class
            enemy_instance = random_enemy_class(self.cell_size, self.map_width, self.map_height, self.screen,
                                                self.bullets_group, self.map_layout)  # Create an enemy object
            self.enemies_group.add(enemy_instance)  # Add the enemy object to the enemies group

        # Number of ladders that will spawn
        self.num_real_ladders = 1

        # Generate random ladder positions
        self.real_ladder_position = []
        while len(self.real_ladder_position) < self.num_real_ladders:
            x = random.randint(0, len(self.map_layout[0]) - 1)
            y = random.randint(0, len(self.map_layout) - 1)
            if self.map_layout[y][x] == ".":
                self.real_ladder_position.append((x, y))

        # Define the number of decoy ladders you want to spawn
        self.num_decoy_ladders = random.randint(3, 4)  # Change this to control the number of decoy ladders

        # Generate random decoy ladder positions
        self.decoy_ladder_positions = []
        while len(self.decoy_ladder_positions) < self.num_decoy_ladders:
            x = random.randint(0, len(self.map_layout[0]) - 1)
            y = random.randint(0, len(self.map_layout) - 1)
            if self.map_layout[y][x] == ".":
                self.decoy_ladder_positions.append((x, y))

        # Load the ladder image and scale it
        self.ladder_image = pygame.image.load("sprites/ladder/ladder.png")
        self.ladder_image = pygame.transform.scale(self.ladder_image, (self.cell_size, self.cell_size))

        # Number of bullet drops that will spawn on the map
        self.num_bullet_drops = 2

        # List to store the positions of bullet drops
        self.bullet_drops = []
        # Loop to randomly generate 'num_bullet_drops' many positions
        while len(self.bullet_drops) < self.num_bullet_drops:
            # Generate random x and y coordinates within the map boundaries
            x = random.randint(0, len(self.map_layout[0]) - 1)
            y = random.randint(0, len(self.map_layout) - 1)
            # Check if the selected position is on an empty floor tile (represented by ".")
            if self.map_layout[y][x] == ".":
                # If it's a valid position, add it to the list of bullet drops
                self.bullet_drops.append((x, y))

        self.bullet_drop_image = pygame.image.load("sprites/bullets/bullet_drop.png")
        self.bullet_drop_image = pygame.transform.scale(self.bullet_drop_image, (35, 35))