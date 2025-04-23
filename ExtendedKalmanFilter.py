import numpy as np
import math
import random
from BaseFilter import BaseFilter

class ExtendedKalmanFilter(BaseFilter):
    def __init__(self, initial_pose, initial_covariance, radius, movement_noise):
        self.pose = initial_pose.reshape(3, 1)
        self.covariance = initial_covariance
        self.radius = radius
        self.noise = movement_noise
        self.path = []

    def update(self, vl, vr, angle, z):
        error_vl = (random.uniform(-self.noise, self.noise) / 100)
        error_vr = (random.uniform(-self.noise, self.noise) / 100)
        error_angle = random.uniform(-2 * math.pi * self.noise / 100, 2 * math.pi * self.noise / 100)

        vl += error_vl
        vr += error_vr
        angle += error_angle

        v = (vl + vr) / 2
        w = (vr - vl) / self.radius

        theta = self.pose[2, 0]
        dt = 1  # assuming discrete time step of 1

        # Non-linear motion model
        fx = np.array([
            [self.pose[0, 0] + v * math.cos(theta) * dt],
            [self.pose[1, 0] + v * math.sin(theta) * dt],
            [theta + w * dt]
        ])

        # Jacobian of motion model w.r.t. state
        A = np.array([
            [1, 0, -v * math.sin(theta)],
            [0, 1,  v * math.cos(theta)],
            [0, 0, 1]
        ])

        # Jacobian of motion model w.r.t. control (approx)
        B = np.array([
            [0.5 * math.cos(theta), 0.5 * math.cos(theta)],
            [0.5 * math.sin(theta), 0.5 * math.sin(theta)],
            [-1/self.radius, 1/self.radius]
        ])

        R = np.eye(3) * 0.1
        u = np.array([[vl], [vr]])

        predicted_pose = fx
        predicted_cov = A @ self.covariance @ A.T + R

        if len(z) > 0:
            z = np.array(z).reshape(3, 1)
            C = np.eye(3)
            Q = np.eye(3) * 0.1
            K = predicted_cov @ C.T @ np.linalg.inv(C @ predicted_cov @ C.T + Q)
            self.pose = predicted_pose + K @ (z - C @ predicted_pose)
            self.covariance = (np.eye(3) - K @ C) @ predicted_cov
        else:
            self.pose = predicted_pose
            self.covariance = predicted_cov

        self.path.append((self.pose[0, 0], self.pose[1, 0]))

    def get_pose(self):
        return self.pose

    def get_path(self):
        return self.path
