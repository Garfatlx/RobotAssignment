from const import *
import numpy as np
import pygame
from Beacon import Beacon

def make_map(type='empty'):
    #create map
    # Assuming the map is a 2D numpy array with 0 for free space and 1 for obstacles
    map = np.zeros((WIDTH,HEIGHT), dtype=np.int8)  # Create a blank map
    beacons = []
    map_surface = pygame.Surface((WIDTH, HEIGHT))
    map_surface.fill(WHITE)  # Fill with background color
    #create boundaries
    map[0,:] = 1  # Top boundary
    map[-1,:] = 1  # Bottom boundary
    map[:,0] = 1  # Left boundary
    map[:,-1] = 1  # Right boundary

    if type == 'empty':
        return map, beacons, map_surface
    elif type == 'starter':
        # map[WIDTH//2+300:WIDTH//2+400, HEIGHT//2+200:HEIGHT//2+220] = 1  
        #map[WIDTH//2-75:WIDTH//2+75, HEIGHT//2-75:HEIGHT//2-74] = 1 
        #map[WIDTH//2+299:WIDTH//2+300, HEIGHT//2-75:HEIGHT//2+75] = 1 
        map[WIDTH//2+99:WIDTH//2+100, HEIGHT//2-HEIGHT//2:HEIGHT//2+HEIGHT//2] = 1 
        #map[WIDTH//2-75:WIDTH//2+75, HEIGHT//2+74:HEIGHT//2+75] = 1 
        #map[WIDTH//2-75:WIDTH//2-74, HEIGHT//2-75:HEIGHT//2+75] = 1 

        beacons.append(Beacon(100, 100, beacon_id=1))
        beacons.append(Beacon(500, 300, beacon_id=2))
        beacons.append(Beacon(700, 500, beacon_id=3))

        return map, beacons, map_surface
    elif type == 'maze':
        # Create a maze-like structure
        for i in range(0, WIDTH, 20):
            map[i, :] = 1
        for j in range(0, HEIGHT, 20):
            map[:, j] = 1

        # Add some random walls
        for _ in range(100):
            x = np.random.randint(1, WIDTH-1)
            y = np.random.randint(1, HEIGHT-1)
            map[x, y] = 1

        beacons.append(Beacon(100, 100, beacon_id=1))
        beacons.append(Beacon(500, 300, beacon_id=2))
        beacons.append(Beacon(700, 500, beacon_id=3))

        return map, beacons, map_surface
    elif type == 'complex':
        # Create a complex structure
        for i in range(0, WIDTH, 10):
            map[i, :] = 1
        for j in range(0, HEIGHT, 10):
            map[:, j] = 1

        # Add some random walls
        for _ in range(200):
            x = np.random.randint(1, WIDTH-1)
            y = np.random.randint(1, HEIGHT-1)
            map[x, y] = 1

        beacons.append(Beacon(100, 100, beacon_id=1))
        beacons.append(Beacon(500, 300, beacon_id=2))
        beacons.append(Beacon(700, 500, beacon_id=3))

        return map, beacons, map_surface
    elif type == 'custom':
        # Create a custom structure
        for i in range(0, WIDTH, 5):
            map[i, :] = 1
        for j in range(0, HEIGHT, 5):
            map[:, j] = 1

        # Add some random walls
        for _ in range(300):
            x = np.random.randint(1, WIDTH-1)
            y = np.random.randint(1, HEIGHT-1)
            map[x, y] = 1

        beacons.append(Beacon(100, 100, beacon_id=1))
        beacons.append(Beacon(500, 300, beacon_id=2))
        beacons.append(Beacon(700, 500, beacon_id=3))

        return map, beacons, map_surface

        