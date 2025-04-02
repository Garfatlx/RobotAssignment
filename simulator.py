import pygame
import math

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Robot Simulation with Speed and Direction")

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)  # For direction line

# Robot properties
robot_radius = 50
robot_pos = [WIDTH // 2, HEIGHT // 2]  # Start at center
robot_speed = 0  # Initial speed
robot_angle = 0  # Initial angle in radians (0 = right)
max_speed = 5  # Maximum speed limit
acceleration = 0.1  # Speed change per frame
turn_rate = 0.05  # Radians per frame for turning

# Font for numbers
font = pygame.font.SysFont(None, 24)

# Function to calculate number positions around the circle
def get_number_positions(center_x, center_y, radius, num_count=12):
    positions = []
    for i in range(num_count):
        angle = 2 * math.pi * i / num_count
        x = center_x + (radius + 20) * math.cos(angle - math.pi / 2)
        y = center_y + (radius + 20) * math.sin(angle - math.pi / 2)
        positions.append((x, y))
    return positions

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Keyboard input for speed and direction
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        robot_speed = min(robot_speed + acceleration, max_speed)  # Accelerate
    if keys[pygame.K_DOWN]:
        robot_speed = max(robot_speed - acceleration, -max_speed)  # Decelerate
    if keys[pygame.K_LEFT]:
        robot_angle -= turn_rate  # Turn left
    if keys[pygame.K_RIGHT]:
        robot_angle += turn_rate  # Turn right

    # Update robot position based on speed and angle
    robot_pos[0] += robot_speed * math.cos(robot_angle)
    robot_pos[1] += robot_speed * math.sin(robot_angle)

    # Keep robot within bounds
    robot_pos[0] = max(robot_radius, min(WIDTH - robot_radius, robot_pos[0]))
    robot_pos[1] = max(robot_radius, min(HEIGHT - robot_radius, robot_pos[1]))

    # Clear the screen
    screen.fill(WHITE)

    # Draw the robot (circle)
    pygame.draw.circle(screen, BLUE, (int(robot_pos[0]), int(robot_pos[1])), robot_radius)

    # Draw direction line
    line_length = robot_radius
    line_end_x = robot_pos[0] + line_length * math.cos(robot_angle)
    line_end_y = robot_pos[1] + line_length * math.sin(robot_angle)
    pygame.draw.line(screen, RED, robot_pos, (line_end_x, line_end_y), 3)

    # Calculate and draw the numbers around the robot
    number_positions = get_number_positions(robot_pos[0], robot_pos[1], robot_radius)
    for i, (x, y) in enumerate(number_positions):
        number = (i + 3) % 12
        if number == 0:
            number = 12
        text = font.render(str(number), True, BLACK)
        text_rect = text.get_rect(center=(x, y))
        screen.blit(text, text_rect)

    # Update the display
    pygame.display.flip()
    clock.tick(60)  # Limit to 60 FPS

# Quit Pygame
pygame.quit()