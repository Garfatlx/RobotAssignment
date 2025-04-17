import math
import numpy as np
from const import *
import pygame
import Sensor

class Robot:
    def __init__(self, x, y, angle, radius, map_data):
        self.x = x
        self.y = y
        self.radius = radius
        self.angle = angle  # Angle in radians
        self.map = map_data
        self.map_width = map_data.shape[0]
        self.map_height = map_data.shape[1]
        self.vl = 5
        self.vr = 5
        self.vl_decay = 0
        self.vr_decay = 0
        self.sensors = []

        for i in range(12):
            angle = 2 * math.pi * i / 12
            sensor = Sensor.Sensor(self, angle, precision=2)
            self.add_sensor(sensor)

    def add_sensor(self, sensor):
        self.sensors.append(sensor)

    def move(self, vl, vr):
        # Calculate proposed movement
        velocity = (vl + vr) / 2
        proposed_dx = velocity * math.cos(self.angle)
        proposed_dy = velocity * math.sin(self.angle)
        proposed_x = self.x + proposed_dx
        proposed_y = self.y + proposed_dy
        proposed_angle = self.angle + (vr - vl) / self.radius

        # Collision detection
        collision_detected = False
        normal_x, normal_y = 0, 0
        total_penetration = 0
        collision_count = 0

        for i in range(-self.radius, self.radius + 1):
            for j in range(-self.radius, self.radius + 1):
                if i**2 + j**2 <= self.radius**2:
                    x = int(proposed_x + i)
                    y = int(proposed_y + j)
                    if 0 <= x < self.map_width and 0 <= y < self.map_height:
                        if self.map[x, y] == 1:
                            collision_detected = True
                            nx = proposed_x - x
                            ny = proposed_y - y
                            dist = math.sqrt(nx**2 + ny**2)
                            if dist > 0:
                                normal_x += nx / dist
                                normal_y += ny / dist
                                total_penetration += max(0, self.radius - dist)
                                collision_count += 1

        if collision_detected and collision_count > 0:
            # Average the normal and penetration
            normal_x /= collision_count
            normal_y /= collision_count
            penetration_depth = total_penetration / collision_count

            # Normalize normal
            normal_length = math.sqrt(normal_x**2 + normal_y**2)
            if normal_length > 0:
                normal_x /= normal_length
                normal_y /= normal_length

            # Project velocity onto normal
            dot_product = proposed_dx * normal_x + proposed_dy * normal_y
            if dot_product < 0:  # Only correct if moving into obstacle
                correction_x = dot_product * normal_x - normal_x * (penetration_depth + 0.1)
                correction_y = dot_product * normal_y - normal_y * (penetration_depth + 0.1)
                self.x += proposed_dx - correction_x
                self.y += proposed_dy - correction_y
            else:
                self.x = proposed_x
                self.y = proposed_y

            self.angle = proposed_angle
        else:
            # No collision, apply full movement
            self.x = proposed_x
            self.y = proposed_y
            self.angle = proposed_angle

        # Keep within bounds (with small epsilon to avoid edge sticking)
        epsilon = 0.1
        self.x = max(self.radius + epsilon, min(self.map_width - self.radius - epsilon, self.x))
        self.y = max(self.radius + epsilon, min(self.map_height - self.radius - epsilon, self.y))


    def get_pos(self):
        return self.x, self.y, self.angle 
    
    def set_vl(self, forward=True):
        self.vl_decay = 0
        if forward:
            self.vl = min(self.vl + ACCELERATION, MAX_SPEED) 
        else:
            self.vl = max(self.vl - ACCELERATION, -MAX_SPEED) 

    def set_vr(self, forward=True):
        self.vr_decay = 0
        if forward:
            self.vr = min(self.vr + ACCELERATION, MAX_SPEED) 
        else:
            self.vr = max(self.vr - ACCELERATION, -MAX_SPEED) 

    def apply_vl_decay(self):
        # Don't decay for small decay counters
        if self.vl_decay < 10:
            return self.vl

        # Compute decay strength — grows non-linearly with decay_counter
        # You can tweak the multiplier and exponent to control how aggressive it is
        decay_strength = (self.vl_decay - 9) ** 1.2 * 0.0001  # 1.2 is the exponent, 0.01 is the scale

        # Apply decay proportional to the current velocity
        if self.vl > 0:
            self.vl -= decay_strength * self.vl
            self.vl = max(0, self.vl)  # Clamp to gzero
        elif self.vl < 0:
            self.vl += decay_strength * abs(self.vl)
            self.vl = min(0, self.vl)  # Clamp to zero

        return self.vl
    

    def apply_vr_decay(self):
        # Don't decay for small decay counters
        if self.vr_decay < 10:
            return self.vr

        # Compute decay strength — grows non-linearly with decay_counter
        # You can tweak the multiplier and exponent to control how aggressive it is
        decay_strength = (self.vr_decay - 9) ** 1.2 * 0.0001  # 1.2 is the exponent, 0.01 is the scale

        # Apply decay proportional to the current velocity
        if self.vr > 0:
            self.vr -= decay_strength * self.vr
            self.vr = max(0, self.vr)  # Clamp to zero
        elif self.vr < 0:
            self.vr += decay_strength * abs(self.vr)
            self.vr = min(0, self.vr)  # Clamp to zero

        return self.vr
    

    def draw_robot(self, screen, font):
        # Draw the robot as a circle
        currnt_x, currnt_y, current_angle = self.get_pos()
        pygame.draw.circle(screen, BLUE, (int(currnt_x), HEIGHT-1-int(currnt_y)), self.radius)

        # Draw the direction line
        line_length = self.radius
        line_end_x = currnt_x + line_length * math.cos(self.angle)
        line_end_y = currnt_y + line_length * math.sin(self.angle)
        pygame.draw.line(screen, RED, (currnt_x, HEIGHT-1-currnt_y), (line_end_x, HEIGHT-1-line_end_y), 3)

        for sensor in self.sensors:
            sensor.draw_reading(screen, font, self.map)

        # for i in range(12):
        #     angle = 2 * math.pi * i / 12
        #     x = currnt_x + (self.radius) * math.cos(angle)
        #     y = currnt_y + (self.radius) * math.sin(angle)
        #     text_x = currnt_x + (self.radius+20) * math.cos(angle)
        #     text_y = currnt_y + (self.radius+20) * math.sin(angle)
        #     for j in range(0,200):
        #         checking_x= x + j * math.cos(angle)
        #         checking_y= y + j * math.sin(angle)
        #         checking_x=max(0, min(checking_x, self.map_width-1))
        #         checking_y=max(0, min(checking_y, self.map_height-1))
        #         if self.map[int(checking_x), int(checking_y)] == 1:
        #             number= j-1
        #             break
        #     else:
        #         number= 200

        #     text= font.render(str(number), True, BLACK)
        #     text_rect = text.get_rect(center=(text_x, HEIGHT-1-text_y))
        #     screen.blit(text, text_rect)
