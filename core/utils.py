import pygame
from core.config import WIDTH, HEIGHT
import core.data as data

def draw_text(surface, text, size, x, y, color, shadow_color=None, shadow=True, center=True):
    if shadow_color is None:
        shadow_color = data.theme["SHADOW"]
    font = pygame.font.SysFont('segoeui', size, bold=True)
    if shadow:
        shadow_img = font.render(text, True, shadow_color)
        s_rect = shadow_img.get_rect(center=(x+4, y+4)) if center else shadow_img.get_rect(topleft=(x+4, y+4))
        surface.blit(shadow_img, s_rect)
    img = font.render(text, True, color)
    rect = img.get_rect(center=(x, y)) if center else img.get_rect(topleft=(x, y))
    surface.blit(img, rect)

def draw_panel(surface, w, h, border_color):
    panel_rect = pygame.Rect(WIDTH//2 - w//2, HEIGHT//2 - h//2, w, h)
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(s, (*data.theme["PANEL"], 230), (0, 0, w, h), border_radius=20)
    surface.blit(s, panel_rect.topleft)
    pygame.draw.rect(surface, border_color, panel_rect, width=4, border_radius=20)
    return panel_rect
