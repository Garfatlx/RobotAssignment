import math
import numpy as np
from const import *

class Robot:
    def __init__(self, x, y, angle,radius,map):
        self.x = x
        self.y = y
        self.radius = radius
        self.angle = angle  # Angle in radians
        self.map = map
        self.map_width = map.shape[0]
        self.map_height = map.shape[1]
        self.vl = 0
        self.vr = 0

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
        penetration_depth = 0
        
        # Check circular area around proposed position
        for i in range(-self.radius, self.radius + 1):
            for j in range(-self.radius, self.radius + 1):
                if i**2 + j**2 <= self.radius**2:
                    x = int(proposed_x + i)
                    y = int(proposed_y + j)
                    if 0 <= x < self.map_width and 0 <= y < self.map_height:
                        if self.map[x, y] == 1:  # Obstacle detected
                            collision_detected = True
                            # Calculate normal and penetration
                            nx = proposed_x - x
                            ny = proposed_y - y
                            dist = math.sqrt(nx**2 + ny**2)
                            if dist > 0:
                                normal_x += nx / dist
                                normal_y += ny / dist
                                # Estimate penetration depth
                                penetration_depth = max(penetration_depth, self.radius - dist)
                            break
            if collision_detected:
                break

        if collision_detected:
            # Normalize the normal vector
            normal_length = math.sqrt(normal_x**2 + normal_y**2)
            if normal_length > 0:
                normal_x /= normal_length
                normal_y /= normal_length
            else:
                normal_x, normal_y = 0, 0  # Fallback if no valid normal

            # Project velocity onto normal to find penetration component
            dot_product = proposed_dx * normal_x + proposed_dy * normal_y
            if dot_product < 0:  # Moving into obstacle
                # Remove motion toward obstacle and add penetration correction
                correction_x = dot_product * normal_x - normal_x * (penetration_depth + 0.1)  # Small buffer
                correction_y = dot_product * normal_y - normal_y * (penetration_depth + 0.1)
                self.x += proposed_dx - correction_x
                self.y += proposed_dy - correction_y
            else:
                # No penetration, just apply movement
                self.x = proposed_x
                self.y = proposed_y
                self.angle = proposed_angle
        else:
            # No collision, apply full movement
            self.x = proposed_x
            self.y = proposed_y
            self.angle = proposed_angle

        # Keep robot within bounds (with small epsilon to avoid edge sticking)
        epsilon = 0.1
        self.x = max(self.radius + epsilon, min(self.map_width - self.radius - epsilon, self.x))
        self.y = max(self.radius + epsilon, min(self.map_height - self.radius - epsilon, self.y))

    def get_pos(self):
        return self.x, self.y, self.angle # Flip y coordinate
    
    def set_vl(self, forward=True):
        if forward:
            self.vl = min(self.vl + ACCELERATION, MAX_SPEED) 
        else:
            self.vl = max(self.vl - ACCELERATION, -MAX_SPEED) 

    def set_vr(self, forward=True):
        if forward:
            self.vr = min(self.vr + ACCELERATION, MAX_SPEED) 
        else:
            self.vr = max(self.vr - ACCELERATION, -MAX_SPEED) 