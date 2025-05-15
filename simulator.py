import pygame
import math
import numpy as np

import RobotClass as Robot
from const import *
from Beacon import Beacon
from BeaconSensor import BeaconSensor
import Map

from controls import movement_control
from DrawUtils import draw_map_cached, draw_velocity_status, generate_grayscale_surface



# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH * 2, HEIGHT))
pygame.display.set_caption("Robot Simulation")

# Load map and beacons
map, beacons, map_surface = Map.make_map(type='lalilu')
draw_map_cached(map_surface, map)

# Create robot
robot = Robot.Robot(WIDTH // 2, HEIGHT - 50, -1.2, ROBOT_RADIUS, map)

# Add beacon sensor
beacon_sensor = BeaconSensor(robot, relative_angle=0, fov=math.radians(360), range=200, precision=0)
robot.add_sensor(beacon_sensor)

font = pygame.font.SysFont(None, 24)

grid_surface = generate_grayscale_surface(robot.mapped_grid, scale=10)

# Main game loop
running = True
clock = pygame.time.Clock()
cycle = 0
action_process=0
step=0
while running:
    cycle += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    movement_control(robot, "direct")  



    robot.move(robot.vl, robot.vr)

    robot.kalman_filter(beacon_sensor.get_observed_pose(beacons))

    # Drawing
    screen.fill(WHITE)
    screen.blit(map_surface, (0, 0))
    robot.draw_robot(screen, font)

    for beacon in beacons:
        beacon.draw(screen)

    beacon_sensor.draw_detected(screen, font, beacons)
    draw_velocity_status(screen, font, robot.vl, robot.vr)
    if cycle % 100 == 0:
        # lag prevention the map visual only updates every 100 cycles
        grid_surface = generate_grayscale_surface(robot.mapped_grid, scale=10)
        print("mapscore", np.sum(np.abs(robot.mapped_grid)))

    screen.blit(grid_surface, (WIDTH, 0))

    pygame.display.flip()
    clock.tick(20)

pygame.quit()
