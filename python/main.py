import pygame
import numpy as np
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('4D Hypercube Rotation')

# Define colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

# Define 4D hypercube vertices
vertices = np.array([
    [-1, -1, -1, -1],
    [1, -1, -1, -1],
    [1, 1, -1, -1],
    [-1, 1, -1, -1],
    [-1, -1, 1, -1],
    [1, -1, 1, -1],
    [1, 1, 1, -1],
    [-1, 1, 1, -1],
    [-1, -1, -1, 1],
    [1, -1, -1, 1],
    [1, 1, -1, 1],
    [-1, 1, -1, 1],
    [-1, -1, 1, 1],
    [1, -1, 1, 1],
    [1, 1, 1, 1],
    [-1, 1, 1, 1]
])

# Define 4D hypercube edges
edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7),
    (8, 9), (9, 10), (10, 11), (11, 8),
    (12, 13), (13, 14), (14, 15), (15, 12),
    (8, 12), (9, 13), (10, 14), (11, 15),
    (0, 8), (1, 9), (2, 10), (3, 11),
    (4, 12), (5, 13), (6, 14), (7, 15)
]

# Rotation matrices for 4D
def rotation_matrix_4d(axis, theta):
    if axis == 'x':
        return np.array([
            [1, 0, 0, 0],
            [0, np.cos(theta), -np.sin(theta), 0],
            [0, np.sin(theta), np.cos(theta), 0],
            [0, 0, 0, 1]
        ])
    elif axis == 'y':
        return np.array([
            [np.cos(theta), 0, np.sin(theta), 0],
            [0, 1, 0, 0],
            [-np.sin(theta), 0, np.cos(theta), 0],
            [0, 0, 0, 1]
        ])
    elif axis == 'z':
        return np.array([
            [np.cos(theta), -np.sin(theta), 0, 0],
            [np.sin(theta), np.cos(theta), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
    elif axis == 'w':
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, np.cos(theta), -np.sin(theta)],
            [0, 0, np.sin(theta), np.cos(theta)]
        ])

# Combine rotation matrices
def combined_rotation_matrix(angles):
    rotation = np.identity(4)
    for axis, theta in angles.items():
        rotation = np.dot(rotation, rotation_matrix_4d(axis, theta))
    return rotation

# Define projection matrices
projection_matrix_4d_to_3d = np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0]
])

projection_matrix_3d_to_2d = np.array([
    [1, 0, 0],
    [0, 1, 0]
])

# Project 4D points to 3D using a projection matrix
def project_to_3d(points):
    projected_points = []
    for point in points:
        projected_point = np.dot(projection_matrix_4d_to_3d, point)
        w = point[3] + 2  # Perspective division factor
        projected_points.append(projected_point / w)
    return projected_points

# Project 3D points to 2D using a projection matrix
def project(points):
    projected_points = []
    for point in points:
        projected_point = np.dot(projection_matrix_3d_to_2d, point)
        z = point[2] + 5  # Perspective division factor
        projected_points.append((width // 2 + int(projected_point[0] * 200 / z), height // 2 - int(projected_point[1] * 200 / z)))
    return projected_points

# Draw coordinate system arrows
def draw_coordinate_system(screen, center, length=100):
    pygame.draw.line(screen, red, center, (center[0] + length, center[1]), 2)  # X-axis in red
    pygame.draw.line(screen, green, center, (center[0], center[1] - length), 2)  # Y-axis in green
    pygame.draw.line(screen, blue, center, (center[0], center[1] + length), 2)  # Z-axis in blue

# Draw labels for coordinate system arrows
def draw_labels(screen, center, length=100):
    font = pygame.font.SysFont(None, 24)
    label_x = font.render('X', True, red)
    label_y = font.render('Y', True, green)
    label_z = font.render('Z', True, blue)
    screen.blit(label_x, (center[0] + length + 5, center[1] - 10))
    screen.blit(label_y, (center[0] - 10, center[1] - length - 20))
    screen.blit(label_z, (center[0] - 10, center[1] + length + 5))

# Draw background gradient
def draw_background(screen):
    for y in range(height):
        color = (0, 0, int(255 * (y / height)))
        pygame.draw.line(screen, color, (0, y), (width, y))

# Function to generate rainbow colors
def get_rainbow_color(t, i, total):
    frequency = 0.3
    red = int(np.sin(frequency * t + 2 * np.pi * i / total) * 127 + 128)
    green = int(np.sin(frequency * t + 2 * np.pi * i / total + 2 * np.pi / 3) * 127 + 128)
    blue = int(np.sin(frequency * t + 2 * np.pi * i / total + 4 * np.pi / 3) * 127 + 128)
    return (red, green, blue)

# Main loop
running = True
angles = {'x': 0, 'y': 0, 'z': 0, 'w': 0}  # Rotation angles for each axis
directions = {'x': 1, 'y': 1, 'z': 1, 'w': 1}  # Rotation directions for each axis
active_axes = set()  # Set of active rotation axes
clock = pygame.time.Clock()
t = 0  # Time variable for color change

def reset_rotation(axis):
    angles[axis] = 0

def toggle_direction(axis):
    directions[axis] *= -1

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_x:
                if 'x' in active_axes:
                    active_axes.remove('x')
                else:
                    active_axes.add('x')
            elif event.key == K_y:
                if 'y' in active_axes:
                    active_axes.remove('y')
                else:
                    active_axes.add('y')
            elif event.key == K_z:
                if 'z' in active_axes:
                    active_axes.remove('z')
                else:
                    active_axes.add('z')
            elif event.key == K_w:
                if 'w' in active_axes:
                    active_axes.remove('w')
                else:
                    active_axes.add('w')
            elif event.key == K_r:
                reset_rotation('x')
                reset_rotation('y')
                reset_rotation('z')
                reset_rotation('w')
            elif event.key == K_d:
                toggle_direction('x')
                toggle_direction('y')
                toggle_direction('z')
                toggle_direction('w')

    draw_background(screen)

    # Draw fixed coordinate system
    draw_coordinate_system(screen, (50, height - 50))
    draw_labels(screen, (50, height - 50))

    # Update rotation angles
    for axis in active_axes:
        angles[axis] += 0.01 * directions[axis]

    # Rotate hypercube
    rotation = combined_rotation_matrix(angles)
    rotated_vertices = np.dot(vertices, rotation)

    # Project vertices to 3D
    projected_vertices_3d = project_to_3d(rotated_vertices)

    # Project vertices to 2D
    projected_vertices_2d = project(projected_vertices_3d)

    # Draw edges with rainbow colors
    for i, edge in enumerate(edges):
        color = get_rainbow_color(t, i, len(edges))
        pygame.draw.line(screen, color, projected_vertices_2d[edge[0]], projected_vertices_2d[edge[1]], 2)

    # Draw title and instructions
    font = pygame.font.SysFont(None, 36)
    title = font.render('4D Hypercube Rotation', True, white)
    screen.blit(title, (width // 2 - title.get_width() // 2, 10))

    font = pygame.font.SysFont(None, 24)
    instructions = font.render('Press X, Y, Z, W to toggle rotation axes', True, white)
    screen.blit(instructions, (width // 2 - instructions.get_width() // 2, 50))

    # Display frame rate
    font = pygame.font.SysFont(None, 24)
    fps = font.render(f'FPS: {int(clock.get_fps())}', True, white)
    screen.blit(fps, (10, 10))

    # Display rotation angles
    angle_text_x = f"X={angles['x']*180/np.pi%360:.1f}°"
    angle_text_y = f"Y={angles['y']*180/np.pi%360:.1f}°"
    angle_text_z = f"Z={angles['z']*180/np.pi%360:.1f}°"
    angle_text_w = f"W={angles['w']*180/np.pi%360:.1f}°"

    angle_display = font.render(angle_text_x, True, white)
    screen.blit(angle_display, (10, 40))
    angle_display = font.render(angle_text_y, True, white)
    screen.blit(angle_display, (10, 60))
    angle_display = font.render(angle_text_z, True, white)
    screen.blit(angle_display, (10, 80))
    angle_display = font.render(angle_text_w, True, white)
    screen.blit(angle_display, (10, 100))
    
    # Display buttons for direction and reset
    button_text = "Press R to reset rotation, D to change direction"
    button_display = font.render(button_text, True, white)
    screen.blit(button_display, (width // 2 - instructions.get_width() // 2, 70))

    t += 0.01  # Increment time for color change
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
