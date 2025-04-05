import pygame
import math
import numpy as np

import Robot

def draw_robot(screen, robot):
    # Draw the robot as a circle
    currnt_x, currnt_y, current_angle = robot.get_pos()
    pygame.draw.circle(screen, BLUE, (int(currnt_x), int(currnt_y)), robot.radius)

    # Draw the direction line
    line_length = robot.radius
    line_end_x = currnt_x + line_length * math.cos(robot.angle)
    line_end_y = currnt_y - line_length * math.sin(robot.angle)
    pygame.draw.line(screen, RED, (currnt_x, currnt_y), (line_end_x, line_end_y), 3)

    for i in range(12):
        angle = 2 * math.pi * i / 12
        x = currnt_x + (robot.radius + 20) * math.cos(angle)
        y = currnt_y - (robot.radius + 20) * math.sin(angle)
        for j in range(robot.radius,robot.radius + 200):
            checking_x= x + j * math.cos(angle)
            checking_y= y - j * math.sin(angle)
            if robot.map[int(checking_x), int(checking_y)] == 1:
                number= j-robot.radius
                break
        else:
            number= 200

        text= font.render(str(number), True, BLACK)
        text_rect = text.get_rect(center=(x, y))
        screen.blit(text, text_rect)
        


# Function to draw the map onto the cached surface
def draw_map_cached(map_surface, map):
    map_surface.fill(WHITE)  # Clear the surface
    for x in range(map.shape[0]):
        for y in range(map.shape[1]):
            if map[x, y] == 1:  # Assuming 1 represents an obstacle
                pygame.draw.rect(map_surface, BLACK, (x, y, 1, 1))  # Draw a pixel for the obstacle




# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 1200, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Robot Simulation with Speed and Direction")

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)  # For direction line

# Robot properties
robot_radius = 30
robot_pos = [WIDTH // 2, HEIGHT // 2]  # Start in the center of the screen
vl= 0  # Left wheel speed
vr= 0  # Right wheel speed
robot_angle = 0  # Initial angle in radians (0 = right)
max_speed = 5  # Maximum speed limit
acceleration = 0.02  # Speed change per frame

#create map
# Assuming the map is a 2D numpy array with 0 for free space and 1 for obstacles
map = np.zeros((WIDTH,HEIGHT), dtype=np.int8)  # Create a blank map
#create boundaries
map[0,:] = 1  # Top boundary
map[-1,:] = 1  # Bottom boundary
map[:,0] = 1  # Left boundary
map[:,-1] = 1  # Right boundary
map[WIDTH//2+300:WIDTH//2+400, HEIGHT//2+200:HEIGHT//2+220] = 1  

map_surface = pygame.Surface((WIDTH, HEIGHT))
map_surface.fill(WHITE)  # Fill with background color

draw_map_cached(map_surface, map)

# Create a robot instance
robot = Robot.Robot(robot_pos[0], robot_pos[1], robot_angle, robot_radius, map)

# Font for numbers
font = pygame.font.SysFont(None, 24)

# Main game loop
running = True
clock = pygame.time.Clock()



while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle map changes (if any)
    # Example: If the map changes, redraw the cached surface
    # if map_changed:  # Add your condition here
    #     draw_map_cached(map_surface, map)

    # movement control
    keys = pygame.key.get_pressed()
    if keys[pygame.K_q]:
        vl= min(vl + acceleration, max_speed)  
    if keys[pygame.K_a]:
        vl= max(vl - acceleration, -max_speed)  
    if keys[pygame.K_w]:
        vr= min(vr + acceleration, max_speed)
    if keys[pygame.K_s]:
        vr= max(vr - acceleration, -max_speed)
    
    robot.move(vl,vr)  # Update robot position based on wheel speeds
    robot_pos[0], robot_pos[1], robot_angle = robot.get_pos()

    # Keep robot within bounds
    robot_pos[0] = max(robot_radius, min(WIDTH - robot_radius, robot_pos[0]))
    robot_pos[1] = max(robot_radius, min(HEIGHT - robot_radius, robot_pos[1]))

    # Clear the screen
    screen.fill(WHITE)

    # Blit the cached map surface onto the screen
    screen.blit(map_surface, (0, 0))

    draw_robot(screen, robot)  # Draw the robot
    

    # Update the display
    pygame.display.flip()
    clock.tick(60)  # Limit to 60 FPS

# Quit Pygame
pygame.quit()

