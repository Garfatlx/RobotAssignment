# main.py

import pygame
import math
import numpy as np

import RobotClass as Robot
from const import *


        

# Function to draw the map onto the cached surface
def draw_map_cached(map_surface, map):
    map_surface.fill(WHITE)  # Clear the surface
    for x in range(map.shape[0]):
        for y in range(map.shape[1]):
            if map[x, map.shape[1]-1-y] == 1:  # Assuming 1 represents an obstacle
                pygame.draw.rect(map_surface, BLACK, (x, y, 1, 1))  # Draw a pixel for the obstacle

# Function to draw the velocity status on the screen
def draw_velocity_status(screen, font, vl, vr):
    # Draw the velocity status on the screen
    vl_text = font.render(f"vL: {vl:.2f}", True, BLACK)
    vr_text = font.render(f"vR: {vr:.2f}", True, BLACK)
    screen.blit(vl_text, (10, HEIGHT - 40))
    screen.blit(vr_text, (10, HEIGHT - 20))

def movement_control(robot, decay=False, steer='standard'):
    # Handle keyboard input for robot movement
    if steer == 'standard':
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            robot.set_vl(True)
        if keys[pygame.K_a]:
            robot.set_vl(False)
        if keys[pygame.K_w]:
            robot.set_vr(True)
        if keys[pygame.K_s]:
            robot.set_vr(False)

        if not (keys[pygame.K_q] or keys[pygame.K_a]):
            robot.vl_decay += 1
        if not (keys[pygame.K_w] or keys[pygame.K_s]):
            robot.vr_decay += 1

        if decay:
            robot.apply_vl_decay() # Decay function for the velocity of the left wheel
            robot.apply_vr_decay() # Decay function for the velocity of the right wheel

    if steer == 'reverse':
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            robot.set_vr(True)
        if keys[pygame.K_a]:
            robot.set_vr(False)
        if keys[pygame.K_w]:
            robot.set_vl(True)
        if keys[pygame.K_s]:
            robot.set_vl(False)

        if not (keys[pygame.K_q] or keys[pygame.K_a]):
            robot.vr_decay += 1
        if not (keys[pygame.K_w] or keys[pygame.K_s]):
            robot.vl_decay += 1

        if decay:
            robot.apply_vl_decay()
            robot.apply_vr_decay()


# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Robot Simulation with Speed and Direction")

# Robot properties
# vl= 0  # Left wheel speed
# vr= 0  # Right wheel speed

#create map
# Assuming the map is a 2D numpy array with 0 for free space and 1 for obstacles
map = np.zeros((WIDTH,HEIGHT), dtype=np.int8)  # Create a blank map
#create boundaries
map[0,:] = 1  # Top boundary
map[-1,:] = 1  # Bottom boundary
map[:,0] = 1  # Left boundary
map[:,-1] = 1  # Right boundary
# map[WIDTH//2+300:WIDTH//2+400, HEIGHT//2+200:HEIGHT//2+220] = 1  
map[WIDTH//2-75:WIDTH//2+75, HEIGHT//2-75:HEIGHT//2-74] = 1 
map[WIDTH//2+74:WIDTH//2+75, HEIGHT//2-75:HEIGHT//2+75] = 1 
map[WIDTH//2-75:WIDTH//2+75, HEIGHT//2+74:HEIGHT//2+75] = 1 
map[WIDTH//2-75:WIDTH//2-74, HEIGHT//2-75:HEIGHT//2+75] = 1 

map_surface = pygame.Surface((WIDTH, HEIGHT))
map_surface.fill(WHITE)  # Fill with background color

draw_map_cached(map_surface, map)

# Create a robot instance
robot = Robot.Robot(WIDTH // 2, HEIGHT // 2, 0, ROBOT_RADIUS, map)

# Font for numbers
font = pygame.font.SysFont(None, 24)

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle map changes (if any)
    # Example: If the map changes, redraw the cached surface
    # if map_changed:  # Add your condition here
    #     draw_map_cached(map_surface, map)

    # movement control
    movement_control(robot)
    
    robot.move(robot.vl,robot.vr)  # Update robot position based on wheel speeds

    # Clear the screen
    screen.fill(WHITE)

    # Blit the cached map surface onto the screen
    screen.blit(map_surface, (0, 0))

    robot.draw_robot(screen, font)  # Draw the robot

    draw_velocity_status(screen, pygame.font.SysFont(None, 24), robot.vl, robot.vr)  # Draw the velocity status
    

    # Update the display
    pygame.display.flip()
    clock.tick(60)  # Limit to 60 FPS

# Quit Pygame
pygame.quit()

