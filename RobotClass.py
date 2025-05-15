import math
import numpy as np
import pygame
import Sensor
import random

from const import *
from KalmanFilter import KalmanFilter
from ExtendedKalmanFilter import ExtendedKalmanFilter
from skimage.draw import line




class Robot:
    def __init__(self, x, y, angle, radius, map_data, initial_predicted_pose=None, initial_predicted_covariance=None, sensor_precision=20, movement_noise=0, bias_strength=0):
        self.x = x
        self.y = y
        self.angle = angle  # Angle in radians
        self.radius = radius
        self.map = map_data
        self.map_width = map_data.shape[0]
        self.map_height = map_data.shape[1]
        self.grid_scale = 10 # Normal resoulution leads to lags so scaled down 10 pixel a tile
        self.mapped_grid = np.zeros((self.map_height // self.grid_scale, self.map_width // self.grid_scale))
        


        self.vl = 1
        self.vr = 1
        self.vl_decay = 0
        self.vr_decay = 0
        self.movement_noise = movement_noise

        self.collision_detected = False
        
        self.path = []

        self.sensors = []
        for i in range(12):
            angle = 2 * math.pi * i / 12
            sensor = Sensor.Sensor(self, angle, precision=sensor_precision)
            self.add_sensor(sensor)

        initial_pose = np.array([[x], [y], [self.angle]])
        initial_covariance = np.eye(3) * 0.1
        self.kalman = KalmanFilter(initial_pose, initial_covariance, radius, movement_noise, bias_strength)

        
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

        self.path.append((self.x, self.y))
        self.collision_detected = collision_detected
        for sensor in self.sensors:
            self.update_map(sensor.get_distance(self.map), sensor.relative_angle)


    def get_pos(self):
        return self.x, self.y, self.angle 
    def get_collision(self):
        return self.collision_detected
    
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
    

    def draw_path(self, screen):
        # Draw robot path
        if len(self.path) > 1:
            pygame.draw.lines(screen, BLACK, False, [(int(x), HEIGHT - 1 - int(y)) for x, y in self.path], 2)
    def draw_predicted_path(self, screen):
        path = self.kalman.get_path()
        if len(path) > 1:
            pygame.draw.lines(screen, BLUE, False, [(int(x), HEIGHT - 1 - int(y)) for x, y in path], 2)


    def draw_robot(self, screen, font):
        self.draw_path(screen)
        self.draw_predicted_path(screen)
        # Draw the robot as a circle
        currnt_x, currnt_y, current_angle = self.get_pos()
        pygame.draw.circle(screen, BLUE, (int(currnt_x), HEIGHT-1-int(currnt_y)), self.radius)

        # Draw the direction line
        line_length = self.radius
        line_end_x = currnt_x + line_length * math.cos(self.angle)
        line_end_y = currnt_y + line_length * math.sin(self.angle)
        pygame.draw.line(screen, RED, (currnt_x, HEIGHT-1-currnt_y), (line_end_x, HEIGHT-1-line_end_y), 3)

        for sensor in self.sensors:
            distance = sensor.draw_reading(screen, font, self.map)
            # self.update_map(distance, sensor.relative_angle)

    # def update_map(self, distance, relative_angle):
    #     # similar logic to the sensor function in reverse, separated out to account for change in sensor logic
    #     angle = self.kalman.pose[2][0] + relative_angle
    #     sensor_x = int(round(self.kalman.pose[0][0] + self.radius * math.cos(angle)))
    #     sensor_y = int(round(self.kalman.pose[1][0] + self.radius * math.sin(angle)))  
    #     end_x = np.clip(int(round(sensor_x + distance * np.cos(angle))),0,self.mapped_grid.shape[1]-1)
    #     end_y = np.clip(int(round(sensor_y + distance * np.cos(angle))),0,self.mapped_grid.shape[0]-1)
        
    #     # determining points in the grid that a line with our angle and distance passed through
    #     row, column = line(sensor_y, sensor_x, end_y, end_x)
    #     for cell in list(zip(row, column)):
    #         y, x = cell
    #         if y < 0 or y >= self.mapped_grid.shape[0] or x < 0 or x >= self.mapped_grid.shape[1]:
    #             break
    #         self.mapped_grid[cell] += np.log(0.3 / 0.7)  # log-odds of free
    #     if distance < 200:
    #         self.mapped_grid[end_y, end_x] += np.log(0.9 / 0.1)  # log-odds of occupied

    def update_map(self, distance, relative_angle):
        """
        update the occupancy grid map 
        In: 
            distance: distance of sensor to obstacle
            relative_angle: angle of sensor relative to robot
        Out:
            No real output but map gets updates
        """
        angle = self.kalman.pose[2][0] + relative_angle

        sensor_world_x = self.kalman.pose[0][0] + self.radius * math.cos(angle)
        sensor_world_y = self.kalman.pose[1][0] + self.radius * math.sin(angle)

        end_world_x = sensor_world_x + distance * math.cos(angle)
        end_world_y = sensor_world_y + distance * math.sin(angle)

        sensor_grid_y, sensor_grid_x = self.world_to_grid(sensor_world_x, sensor_world_y, self.grid_scale)
        end_grid_y, end_grid_x = self.world_to_grid(end_world_x, end_world_y, self.grid_scale)

        sensor_grid_x = np.clip(sensor_grid_x, 0, self.mapped_grid.shape[1] - 1)
        sensor_grid_y = np.clip(sensor_grid_y, 0, self.mapped_grid.shape[0] - 1)
        end_grid_x = np.clip(end_grid_x, 0, self.mapped_grid.shape[1] - 1)
        end_grid_y = np.clip(end_grid_y, 0, self.mapped_grid.shape[0] - 1)

        row_indices, col_indices = line(sensor_grid_y, sensor_grid_x, end_grid_y, end_grid_x)

        # for y, x in zip(row_indices[:-1], col_indices[:-1]):
        #     if 0 <= y < self.mapped_grid.shape[0] and 0 <= x < self.mapped_grid.shape[1]:
        #         self.mapped_grid[y, x] += np.log(0.4 / 0.6)  # free
        #         self.mapped_grid[y, x] = np.clip(self.mapped_grid[y,x], -5, 5)

        # if distance < 200:  
        #     if 0 <= end_grid_y < self.mapped_grid.shape[0] and 0 <= end_grid_x < self.mapped_grid.shape[1]:
        #         self.mapped_grid[end_grid_y, end_grid_x] += np.log(0.9 / 0.1)  # occupied
        #         self.mapped_grid[end_grid_y, end_grid_x] = np.clip(self.mapped_grid[end_grid_y, end_grid_x], -5, 5)
        for y, x in zip(row_indices[:-1], col_indices[:-1]):
            if 0 <= y < self.mapped_grid.shape[0] and 0 <= x < self.mapped_grid.shape[1]:
                self.mapped_grid[y, x] += np.log(0.3 / 0.7)  # free

        if distance < 200:  
            if 0 <= end_grid_y < self.mapped_grid.shape[0] and 0 <= end_grid_x < self.mapped_grid.shape[1]:
                self.mapped_grid[end_grid_y, end_grid_x] += np.log(0.9 / 0.1)  # occupied


    def world_to_grid(self, x, y, scale=10):
        return int(y // scale), int(x // scale)  # (row, col)

    def grid_to_world(self, row, col, scale=10):
        return col * scale + scale / 2, row * scale + scale / 2  # (x, y)
    
    def kalman_filter(self, z):
        self.kalman.update(self.vl, self.vr, self.angle, z)

    def clone(self):
        return Robot(self.x, self.y, self.angle, self.radius, self.map, initial_predicted_pose=self.kalman.pose, initial_predicted_covariance=self.kalman.covariance, sensor_precision=self.sensors[0].precision, movement_noise=self.movement_noise)
    def destroy(self):
        self.sensors = []
        self.path = []
        self.mapped_grid = np.zeros((self.map_height // self.grid_scale, self.map_width // self.grid_scale))
        self.mapped_score=0
        self.kalman = None
    def get_mapped_grid(self):
        return self.mapped_grid
