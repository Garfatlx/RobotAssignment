import math
import pygame
from const import *

import math
import pygame
from const import *

class Sensor:
    def __init__(self, robot, relative_angle, precision=0):
        self.robot = robot
        self.relative_angle = relative_angle  # relative to robot's current angle
        self.precision = precision  # max error to add to distance reading

    def get_distance(self, map_data, max_range=200):
        angle = self.robot.angle + self.relative_angle
        x = self.robot.x + self.robot.radius * math.cos(angle)
        y = self.robot.y + self.robot.radius * math.sin(angle)

        for i in range(max_range):
            checking_x = x + i * math.cos(angle)
            checking_y = y + i * math.sin(angle)

            checking_x = max(0, min(checking_x, self.robot.map_width - 1))
            checking_y = max(0, min(checking_y, self.robot.map_height - 1))

            if map_data[int(checking_x), int(checking_y)] == 1:
                distance = i - 1
                break
        else:
            distance = max_range

        # Apply precision error (simulate noise)
        if self.precision > 0:
            import random
            error = random.uniform(-self.precision, self.precision)
            distance += error
            distance = max(0, min(distance, max_range))

        return int(distance)

    def draw_reading(self, screen, font, map_data):
        angle = self.robot.angle + self.relative_angle
        x = self.robot.x
        y = self.robot.y
        text_x = x + (self.robot.radius + 20) * math.cos(angle)
        text_y = y + (self.robot.radius + 20) * math.sin(angle)
        distance = self.get_distance(map_data)

        text = font.render(str(distance), True, BLACK)
        text_rect = text.get_rect(center=(text_x, HEIGHT - 1 - text_y))
        screen.blit(text, text_rect)

        return distance
