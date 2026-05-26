import pygame
from core.config import WIDTH, HEIGHT

# Initialize base pygame modules once
if not pygame.get_init():
    pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Premium Arcade Hub")
clock = pygame.time.Clock()
