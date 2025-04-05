import math
import numpy as np

class Robot:
    '''
    Original coordinate's origin is at the top left corner of the screen.
    But we flip the y coordinate to make it more intuitive. It is done by subtracting the y coordinate from the height of the screen.
    '''
    def __init__(self, x, y, angle,radius,map):
        self.x = x
        self.y = y
        self.radius = radius
        self.angle = angle  # Angle in radians
        self.map = map
        self.map_width = map.shape[0]
        self.map_height = map.shape[1]

    def move(self, vl,vr):
        self.x += (vl + vr) / 2 * math.cos(self.angle)
        self.y += (vl + vr) / 2 * math.sin(self.angle)
        self.angle += (vr - vl) / self.radius 
        self.x = max(self.radius, min(self.map_width - self.radius, self.x))
        self.y = max(self.radius, min(self.map_height - self.radius, self.y))

        
    def get_pos(self):
        return self.x, self.map_height - self.y, self.angle # Flip y coordinate