import pygame
from const import *
import numpy as np

def draw_map_cached(map_surface, map):
    map_surface.fill(WHITE)
    for x in range(map.shape[0]):
        for y in range(map.shape[1]):
            if map[x, map.shape[1]-1-y] == 1:
                pygame.draw.rect(map_surface, BLACK, (x, y, 1, 1))

def draw_velocity_status(screen, font, vl, vr):
    """
    Draws the velocity stati of left and right wheel on the bottom left of screen
    """
    vl_text = font.render(f"vL: {vl:.2f}", True, BLACK)
    vr_text = font.render(f"vR: {vr:.2f}", True, BLACK)
    screen.blit(vl_text, (10, HEIGHT - 40))
    screen.blit(vr_text, (10, HEIGHT - 20))

def logodds_to_probability(logodds):
    return 1 - 1 / (1 + np.exp(logodds))


def generate_grayscale_surface(grid, scale=10):
    """
    Visualization of the occupancy grid map
    In:
        grid: 2D numpy array of occupancy values
        scale: scale factor for the surface to make it big again
    Out:
        surface: pygame surface to plot
    """
    grid = logodds_to_probability(grid)
    rows, cols = grid.shape
    surface = pygame.Surface((cols * scale, rows * scale))
    for y in range(rows):
        for x in range(cols):
            value = grid[y, x]
            # print(value)
            color = int(255 * (1 - value))
            pygame.draw.rect(
                surface,
                (color, color, color),
                (x * scale, HEIGHT - y * scale, scale, scale)
            )
    return surface




