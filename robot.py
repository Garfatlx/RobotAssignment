import math
import pygame
from const import *

class Robot:
    def __init__(self):
        self.radius = ROBOT_RADIUS
        self.position = [WIDTH // 2, HEIGHT // 2]  # Start at center
        self.speed = 0  # Initial speed
        self.angle = 0  # Initial angle in radians (0 = right)

    def accelerate(self):
        self.speed = min(self.speed + ACCELERATION, MAX_SPEED)

    def decelerate(self):
        self.speed = max(self.speed - ACCELERATION, -MAX_SPEED)

    def turn_left(self):
        self.angle -= TURN_RATE

    def turn_right(self):
        self.angle += TURN_RATE

    def update_position(self):
        self.position[0] += self.speed * math.cos(self.angle)
        self.position[1] += self.speed * math.sin(self.angle)

        # Keep the robot within bounds
        self.position[0] = max(self.radius, min(WIDTH - self.radius, self.position[0]))
        self.position[1] = max(self.radius, min(HEIGHT - self.radius, self.position[1]))

    def draw(self, screen):
        # Draw the robot (circle)
        pygame.draw.circle(screen, BLUE, (int(self.position[0]), int(self.position[1])), self.radius)

        # Draw direction line
        line_length = self.radius
        line_end_x = self.position[0] + line_length * math.cos(self.angle)
        line_end_y = self.position[1] + line_length * math.sin(self.angle)
        pygame.draw.line(screen, RED, self.position, (line_end_x, line_end_y), 3)

    def get_number_positions(self):
        positions = []
        for i in range(12):
            angle = 2 * math.pi * i / 12
            x = self.position[0] + (self.radius + 20) * math.cos(angle - math.pi / 2)
            y = self.position[1] + (self.radius + 20) * math.sin(angle - math.pi / 2)
            positions.append((x, y))
        return positions

    def draw_numbers(self, screen, font):
        number_positions = self.get_number_positions()
        for i, (x, y) in enumerate(number_positions):
            number = (i + 3) % 12
            if number == 0:
                number = 12
            text = font.render(str(number), True, BLACK)
            text_rect = text.get_rect(center=(x, y))
            screen.blit(text, text_rect)
