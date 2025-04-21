# main.py

import pygame
import math
import numpy as np

import RobotClass as Robot
from const import *
from Beacon import Beacon
from BeaconSensor import BeaconSensor
import Map



        

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




map, beacons, map_surface = Map.make_map(type='starter')


draw_map_cached(map_surface, map)

# Create a robot instance
robot = Robot.Robot(WIDTH // 2, HEIGHT -50, -1.2, ROBOT_RADIUS, map)


# Add a beacon sensor to the robot
beacon_sensor = BeaconSensor(robot, relative_angle=0, fov=math.radians(60), range=300, precision=5)
robot.add_sensor(beacon_sensor)

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

    # Draw beacons
    for beacon in beacons:
        beacon.draw(screen)

    # Draw sensor readings (only BeaconSensor supports this)
    beacon_sensor.draw_detected(screen, font, beacons)

    draw_velocity_status(screen, pygame.font.SysFont(None, 24), robot.vl, robot.vr)  # Draw the velocity status
    

    # Update the display
    pygame.display.flip()
    clock.tick(60)  # Limit to 60 FPS

# Quit Pygame
pygame.quit()

