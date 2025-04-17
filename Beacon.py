import pygame
from const import *

class Beacon:
    def __init__(self, x, y, beacon_id, color=ORANGE):
        self.x = x
        self.y = y
        self.id = beacon_id
        self.color = color

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), HEIGHT - 1 - int(self.y)), 6)
