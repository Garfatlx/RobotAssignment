import asyncio
import platform
import pygame
import math
import numpy as np
import RobotClass as Robot
from const import *
from Beacon import Beacon
from BeaconSensor import BeaconSensor
import Map
from DrawUtils import draw_map_cached, draw_velocity_status, generate_grayscale_surface
from EAController import NavigatorGA, NeuralNetwork

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH * 2, HEIGHT))
pygame.display.set_caption("Robot Simulation")

# Load map and beacons
map_data, beacons, map_surface = Map.make_map(type='lalilu')
draw_map_cached(map_surface, map_data)

# Create robot
robot = Robot.Robot(WIDTH // 2, HEIGHT - 50, -1.2, ROBOT_RADIUS, map_data)

# Add beacon sensor
beacon_sensor = BeaconSensor(robot, relative_angle=0, fov=math.radians(360), range=200, precision=0)
robot.add_sensor(beacon_sensor)

font = pygame.font.SysFont(None, 24)
grid_surface = generate_grayscale_surface(robot.mapped_grid, scale=10)

# Evolve neural network controller
ga = NavigatorGA(population_size=20, mutation_rate=0.1, map_data=map_data, beacons=beacons)
controller = ga.evolve(generations=10, steps=200)

async def main():
    global grid_surface
    running = True
    clock = pygame.time.Clock()
    cycle = 0

    while running:
        cycle += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Get sensor readings
        sensor_readings = [sensor.get_distance(map_data) for sensor in robot.sensors[:-1]]
        beacon_reading = beacon_sensor.get_observed_pose(beacons)
        beacon_dist = beacon_reading[0] if beacon_reading else 200
        inputs = np.array(sensor_readings + [beacon_dist]) / 200  # Normalize
        # Get control outputs from NN
        vl, vr = controller.forward(inputs)
        robot.vl, robot.vr = vl, vr
        # Move robot
        robot.move(vl, vr)
        # Update Kalman filter
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
            grid_surface = generate_grayscale_surface(robot.mapped_grid, scale=10)
            print("mapscore", np.sum(np.abs(robot.mapped_grid)))
        screen.blit(grid_surface, (WIDTH, 0))

        pygame.display.flip()
        clock.tick(20)
        await asyncio.sleep(1.0 / 20)  # Control frame rate

    pygame.quit()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())