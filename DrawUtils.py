import pygame
from const import *

def draw_map_cached(map_surface, map):
    map_surface.fill(WHITE)
    for x in range(map.shape[0]):
        for y in range(map.shape[1]):
            if map[x, map.shape[1]-1-y] == 1:
                pygame.draw.rect(map_surface, BLACK, (x, y, 1, 1))

def draw_velocity_status(screen, font, vl, vr):
    vl_text = font.render(f"vL: {vl:.2f}", True, BLACK)
    vr_text = font.render(f"vR: {vr:.2f}", True, BLACK)
    screen.blit(vl_text, (10, HEIGHT - 40))
    screen.blit(vr_text, (10, HEIGHT - 20))
