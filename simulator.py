# main.py

import pygame
from const import *
from robot import Robot

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Robot Simulation with Speed and Direction")

# Font for numbers
font = pygame.font.SysFont(None, 24)

# Create a robot object
robot = Robot()

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Keyboard input for speed and direction
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        robot.accelerate()  # Accelerate
    if keys[pygame.K_DOWN]:
        robot.decelerate()  # Decelerate
    if keys[pygame.K_LEFT]:
        robot.turn_left()  # Turn left
    if keys[pygame.K_RIGHT]:
        robot.turn_right()  # Turn right

    # Update robot position based on speed and angle
    robot.update_position()

    # Clear the screen
    screen.fill(WHITE)

    # Draw the robot and its direction line
    robot.draw(screen)

    # Draw the numbers around the robot
    robot.draw_numbers(screen, font)

    # Update the display
    pygame.display.flip()
    clock.tick(60)  # Limit to 60 FPS

# Quit Pygame
pygame.quit()
