import numpy as np
import math
import random

from BaseFilter import BaseFilter

class KalmanFilter(BaseFilter):
    def __init__(self, initial_pose, initial_covariance, radius, movement_noise):
        self.pose = initial_pose.reshape(3, 1)
        self.covariance = initial_covariance
        self.radius = radius
        self.noise = movement_noise
        self.path = []

    def update(self, vl, vr, angle, z):
        # Add noise to motion commands
        error_vl = (random.uniform(-self.noise, self.noise) / 100)
        error_vr = (random.uniform(-self.noise, self.noise) / 100)
        error_angle = random.uniform(-2 * math.pi * self.noise / 100, 2 * math.pi * self.noise / 100)

        kalman_vl = max(min(vl + error_vl, 1), -1)
        kalman_vr = max(min(vr + error_vr, 1), -1)
        kalman_angle = angle + error_angle

        # Prediction step
        A = np.eye(3)
        B = np.array([
            [math.cos(kalman_angle), 0],
            [math.sin(kalman_angle), 0],
            [0, 1]
        ])
        u = np.array([[(kalman_vl + kalman_vr) / 2], [(kalman_vr - kalman_vl) / self.radius]])
        R = np.eye(3) * 0.1

        predicted_pose = A @ self.pose + B @ u
        predicted_cov = A @ self.covariance @ A.T + R

        # Update step (if measurements available)
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
