import pygame
from lsystem import LSystem

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Multiple L-Systems in Pygame")
clock = pygame.time.Clock()

# Create multiple L-Systems
lsystem1 = LSystem(start_pos=(400,300))

# Main loop
running = True
i = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill((255, 255, 255))
    
    # Grow and draw all L-Systems
    lsystem1.draw(screen)

    if i > 30:
        lsystem1.iterate()
        i = 0
    else:
        i += 1

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(30)

pygame.quit()
