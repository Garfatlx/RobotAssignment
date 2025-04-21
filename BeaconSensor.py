import math
import pygame
from const import *
from Sensor import Sensor

class BeaconSensor(Sensor):
    def __init__(self, robot, relative_angle=0, fov=math.radians(45), range=200, precision=0):
        super().__init__(robot, relative_angle, precision)
        self.fov = fov
        self.range = range

    def detect_beacons(self, beacons):
        robot_x, robot_y, robot_angle = self.robot.get_pos()
        sensor_angle = robot_angle + self.relative_angle

        detected = []

        for beacon in beacons:
            dx = beacon.x - robot_x
            dy = beacon.y - robot_y
            distance = math.hypot(dx, dy)

            if distance > self.range:
                continue

            angle_to_beacon = math.atan2(dy, dx)
            angle_diff = self._normalize_angle(angle_to_beacon - sensor_angle)

            if abs(angle_diff) <= self.fov / 2:
                noisy_distance = distance + self._get_error()
                detected.append((beacon.id, noisy_distance, angle_diff, beacon))

        return detected

    def _normalize_angle(self, angle):
        while angle <= -math.pi: angle += 2 * math.pi
        while angle > math.pi: angle -= 2 * math.pi
        return angle

    def _get_error(self):
        import random
        return random.uniform(-self.precision, self.precision)

    def draw_detected(self, screen, font, beacons):
        detected = self.detect_beacons(beacons)
        for beacon_id, distance, angle_offset, beacon in detected:
            x = self.robot.x + (self.robot.radius + 20) * math.cos(self.robot.angle + self.relative_angle)
            y = self.robot.y + (self.robot.radius + 20) * math.sin(self.robot.angle + self.relative_angle)
            text = font.render(f"B{beacon_id}", True, GREEN)
            screen.blit(text, (x, HEIGHT - 1 - y))
            pygame.draw.line(screen, GREEN, (self.robot.x, HEIGHT - 1 - self.robot.y), (beacon.x, HEIGHT - 1 - beacon.y), 2)

