from const import *
import numpy as np
import pygame
from Beacon import Beacon

def add_boundaries(map):
    map[0, :] = 1
    map[-1, :] = 1
    map[:, 0] = 1
    map[:, -1] = 1

def add_random_walls(map, count):
    for _ in range(count):
        x = np.random.randint(1, WIDTH - 1)
        y = np.random.randint(1, HEIGHT - 1)
        map[x, y] = 1

def add_grid_walls(map, step):
    for i in range(0, WIDTH, step):
        map[i, :] = 1
    for j in range(0, HEIGHT, step):
        map[:, j] = 1

def make_map(type='empty'):
    map = np.zeros((WIDTH, HEIGHT), dtype=np.int8)
    beacons = []
    map_surface = pygame.Surface((WIDTH, HEIGHT))
    map_surface.fill(WHITE)

    add_boundaries(map)

    if type == 'empty':
        pass

    elif type == 'starter':
        map[WIDTH // 2 + 99:WIDTH // 2 + 100, :] = 1
        beacons += [
            Beacon(100, 100, 1),
            Beacon(500, 300, 2),
            Beacon(700, 500, 3),
            Beacon(450, 350, 4),
            Beacon(600, 400, 5),
        ]

    elif type == 'maze':
        add_grid_walls(map, 20)
        add_random_walls(map, 100)
        beacons += [
            Beacon(100, 100, 1),
            Beacon(500, 300, 2),
            Beacon(700, 500, 3),
        ]

    elif type == 'complex':
        add_grid_walls(map, 10)
        add_random_walls(map, 200)
        beacons += [
            Beacon(100, 100, 1),
            Beacon(500, 300, 2),
            Beacon(700, 500, 3),
        ]

    elif type == 'custom':
        add_grid_walls(map, 5)
        add_random_walls(map, 300)
        beacons += [
            Beacon(100, 100, 1),
            Beacon(500, 300, 2),
            Beacon(700, 500, 3),
        ]

    elif type == 'spokes':
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        branch_length = 150
        spacing = 80
        num_branches = 8
        angle_step = 2 * np.pi / num_branches

        for i in range(num_branches):
            angle = i * angle_step
            for j in range(branch_length):
                x = int(center_x + j * np.cos(angle))
                y = int(center_y + j * np.sin(angle))
                if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                    map[x, y] = 0  # Clear path

            # Add walls around corridor
            for offset in [-1, 1]:
                for j in range(branch_length):
                    x = int(center_x + j * np.cos(angle) + offset * np.sin(angle))
                    y = int(center_y + j * np.sin(angle) - offset * np.cos(angle))
                    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                        map[x, y] = 1  # Wall

            # Place beacon at end of each spoke
            bx = int(center_x + branch_length * np.cos(angle))
            by = int(center_y + branch_length * np.sin(angle))
            if 0 <= bx < WIDTH and 0 <= by < HEIGHT:
                beacons.append(Beacon(bx, by, i + 1))

        map[center_x - 10:center_x + 10, center_y - 10:center_y + 10] = 0  # open central hub
        # map[WIDTH // 2 - 100:WIDTH // 2 + 100, WIDTH // 2 + 199:WIDTH // 2 + 200] = 1


    elif type == 'boundary_spokes':
        spacing = 100
        corridor_width = 5
        beacon_id = 1

        # Horizontal spokes from top and bottom
        for x in range(spacing, WIDTH, spacing):
            for w in range(-corridor_width // 2, corridor_width // 2 + 1):
                map[x + w, 0:80] = 0  # Top spoke
                map[x + w, HEIGHT - 80:] = 0  # Bottom spoke

            # Add beacons at inner ends
            beacons.append(Beacon(x, 80, beacon_id))
            beacon_id += 1
            beacons.append(Beacon(x, HEIGHT - 81, beacon_id))
            beacon_id += 1

        # Vertical spokes from left and right
        for y in range(spacing, HEIGHT, spacing):
            for w in range(-corridor_width // 2, corridor_width // 2 + 1):
                map[0:80, y + w] = 0  # Left spoke
                map[WIDTH - 80:, y + w] = 0  # Right spoke

            # Add beacons at inner ends
            beacons.append(Beacon(80, y, beacon_id))
            beacon_id += 1
            beacons.append(Beacon(WIDTH - 81, y, beacon_id))
            beacon_id += 1

        # Ensure center area is clear (like a main area)
        center_clear = 200
        cx, cy = WIDTH // 2, HEIGHT // 2
        map[cx - center_clear//2:cx + center_clear//2, cy - center_clear//2:cy + center_clear//2] = 0

    return map, beacons, map_surface


