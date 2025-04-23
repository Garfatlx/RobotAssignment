import math
import pygame
from const import *
from Sensor import Sensor
import numpy as np

class BeaconSensor(Sensor):
    def __init__(self, robot, relative_angle=0, fov=math.radians(360), range=200, precision=0):
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

    def get_observed_pose(self, beacons):
        detected = self.detect_beacons(beacons)
        if not detected or len(detected) < 3:
            return []

        beacon_positions = []
        distances = []

        for beacon_id, distance, angle_offset, beacon in detected[:3]:
            beacon_positions.append((beacon.x, beacon.y))
            distances.append(distance)

        (x1, y1), (x2, y2), (x3, y3) = beacon_positions
        r1, r2, r3 = distances

        A = np.array([
            [2*(x2 - x1), 2*(y2 - y1)],
            [2*(x3 - x1), 2*(y3 - y1)]
        ])
        b = np.array([
            r1**2 - r2**2 - x1**2 + x2**2 - y1**2 + y2**2,
            r1**2 - r3**2 - x1**2 + x3**2 - y1**2 + y3**2
        ])

        try:
            pos = np.linalg.solve(A, b)
            x, y = pos[0], pos[1]
        except np.linalg.LinAlgError:
            print("Singular matrix — beacons might be collinear.")
            return []

        # Approximate angle using the first beacon direction
        # This is arbitrary unless you have a more robust method
        angle= math.atan(y1/x1)+detected[0][2]  # angle_offset

        x = int(round(x))
        y = int(round(y))
        return [x, y, angle]
    
    def get_observed_pose_by_scanning(self, beacons):
        detected = self.detect_beacons(beacons)
        if not detected or len(detected) < 3:
            return []

        beacon_positions = []
        distances = []
        searching_ranges_x = []
        searching_ranges_y = []

        for beacon_id, distance, angle_offset, beacon in detected[:3]:
            beacon_positions.append((beacon.x, beacon.y))
            distances.append(distance)
            searching_ranges_x.append((beacon.x - distance, beacon.x + distance))
            searching_ranges_y.append((beacon.y - distance, beacon.y + distance))

        searching_rang_x= int(round(max([x[0] for x in searching_ranges_x]))), int(round(min([x[1] for x in searching_ranges_x])))
        searching_rang_y= int(round(max([y[0] for y in searching_ranges_y]))), int(round(min([y[1] for y in searching_ranges_y])))

        optimal_position=[]
        min_error= float('inf')
        for checking_x in range(searching_rang_x[0], searching_rang_x[1]):
            for checking_y in range(searching_rang_y[0], searching_rang_y[1]):
                error=0
                for beacon_id, distance, angle_offset, beacon in detected:
                    checking_distance= math.sqrt((checking_x - beacon.x)**2 + (checking_y - beacon.y)**2)
                    error+= abs(checking_distance - distance)
                if error < min_error:
                    min_error= error
                    optimal_position=[checking_x, checking_y]
        
        angle= math.atan2(optimal_position[1]-self.robot.y, optimal_position[0]-self.robot.x) + detected[0][2]  # angle_offset
        x = int(round(optimal_position[0]))
        y = int(round(optimal_position[1]))
        return [x, y, angle]