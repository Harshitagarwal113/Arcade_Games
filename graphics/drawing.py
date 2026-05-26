import pygame
import math

def draw_apple(surface, x, y, size):
    pygame.draw.circle(surface, (220, 20, 60), (x + size//2, y + size//2 + 2), size//2 - 2)
    pygame.draw.circle(surface, (255, 99, 71), (x + size//2 - 3, y + size//2 - 2), 4)
    pygame.draw.line(surface, (139, 69, 19), (x + size//2, y + size//2 - 5), (x + size//2 + 3, y - 2), 3)
    pygame.draw.ellipse(surface, (50, 205, 50), (x + size//2 + 2, y, 8, 5))

def draw_snake_head(surface, x, y, size, dir_x, dir_y, tongue_out, theme):
    pygame.draw.rect(surface, theme["SNAKE_HEAD"], (x+1, y+1, size-2, size-2), border_radius=6)
    
    eye_color = (255, 255, 255)
    pupil_color = (0, 0, 0)
    
    if dir_x > 0:
        e1, e2 = (x + size - 6, y + 6), (x + size - 6, y + size - 6)
        p_off = (2, 0)
        t_start = (x + size, y + size//2)
        t_end1 = (x + size + 8, y + size//2 - 3)
        t_end2 = (x + size + 8, y + size//2 + 3)
    elif dir_x < 0:
        e1, e2 = (x + 6, y + 6), (x + 6, y + size - 6)
        p_off = (-2, 0)
        t_start = (x, y + size//2)
        t_end1 = (x - 8, y + size//2 - 3)
        t_end2 = (x - 8, y + size//2 + 3)
    elif dir_y < 0:
        e1, e2 = (x + 6, y + 6), (x + size - 6, y + 6)
        p_off = (0, -2)
        t_start = (x + size//2, y)
        t_end1 = (x + size//2 - 3, y - 8)
        t_end2 = (x + size//2 + 3, y - 8)
    else:
        e1, e2 = (x + 6, y + size - 6), (x + size - 6, y + size - 6)
        p_off = (0, 2)
        t_start = (x + size//2, y + size)
        t_end1 = (x + size//2 - 3, y + size + 8)
        t_end2 = (x + size//2 + 3, y + size + 8)

    pygame.draw.circle(surface, eye_color, e1, 4)
    pygame.draw.circle(surface, eye_color, e2, 4)
    pygame.draw.circle(surface, pupil_color, (e1[0]+p_off[0], e1[1]+p_off[1]), 2)
    pygame.draw.circle(surface, pupil_color, (e2[0]+p_off[0], e2[1]+p_off[1]), 2)
    
    if tongue_out:
        t_mid = (t_start[0] + p_off[0]*2, t_start[1] + p_off[1]*2)
        pygame.draw.line(surface, (255, 50, 50), t_start, t_mid, 2)
        pygame.draw.line(surface, (255, 50, 50), t_mid, t_end1, 2)
        pygame.draw.line(surface, (255, 50, 50), t_mid, t_end2, 2)

def draw_tictactoe_piece(surface, val, cx, cy, size, color):
    if val == "X":
        s = size // 3
        pygame.draw.line(surface, color, (cx - s, cy - s), (cx + s, cy + s), 12)
        pygame.draw.line(surface, color, (cx + s, cy - s), (cx - s, cy + s), 12)
        eye_y = cy - s//2
        pygame.draw.line(surface, (255, 255, 255), (cx - 20, eye_y - 10), (cx - 5, eye_y), 4)
        pygame.draw.line(surface, (255, 255, 255), (cx + 20, eye_y - 10), (cx + 5, eye_y), 4)
        pygame.draw.circle(surface, (255, 0, 0), (cx - 12, eye_y), 3)
        pygame.draw.circle(surface, (255, 0, 0), (cx + 12, eye_y), 3)
    elif val == "O":
        s = size // 3
        pygame.draw.circle(surface, color, (cx, cy), s + 4, 12)
        eye_y = cy - s//2
        pygame.draw.circle(surface, (0, 0, 0), (cx - 15, eye_y), 5)
        pygame.draw.circle(surface, (0, 0, 0), (cx + 15, eye_y), 5)
        pygame.draw.circle(surface, (255, 255, 255), (cx - 16, eye_y - 1), 2)
        pygame.draw.circle(surface, (255, 255, 255), (cx + 14, eye_y - 1), 2)
        pygame.draw.ellipse(surface, (0, 0, 0), (cx - 8, cy + 5, 16, 20))
        pygame.draw.ellipse(surface, (255, 100, 100), (cx - 5, cy + 15, 10, 8))

def draw_spaceship_paddle(surface, rect, theme, is_vertical=True):
    if is_vertical:
        pygame.draw.rect(surface, theme["SHADOW"], (rect.x+5, rect.y+5, rect.width, rect.height), border_radius=10)
        pygame.draw.rect(surface, theme["PANEL"], rect, border_radius=10)
        pygame.draw.ellipse(surface, (150, 200, 255), (rect.x-5, rect.centery-15, rect.width+10, 30))
        pygame.draw.rect(surface, (100, 100, 100), (rect.x, rect.top-5, rect.width, 10), border_radius=3)
        pygame.draw.rect(surface, (100, 100, 100), (rect.x, rect.bottom-5, rect.width, 10), border_radius=3)
    else:
        pygame.draw.rect(surface, theme["SECONDARY"], rect, border_radius=5)
        pygame.draw.ellipse(surface, (150, 200, 255), (rect.centerx-20, rect.y-5, 40, rect.height+10))
        anim = math.sin(pygame.time.get_ticks() / 100) * 5
        pygame.draw.polygon(surface, (0, 255, 255), [(rect.centerx-15, rect.bottom), (rect.centerx-5, rect.bottom+10+anim), (rect.centerx, rect.bottom)])
        pygame.draw.polygon(surface, (0, 255, 255), [(rect.centerx, rect.bottom), (rect.centerx+5, rect.bottom+10+anim), (rect.centerx+15, rect.bottom)])

def draw_brick_face(surface, rect, ball_y, theme, color):
    pygame.draw.rect(surface, color, rect, border_radius=4)
    dist = abs(rect.centery - ball_y)
    eye_offset_y = 0
    if dist < 60:
        eye_offset_y = -2 
    cx, cy = rect.centerx, rect.centery + eye_offset_y
    pygame.draw.circle(surface, (255, 255, 255), (cx - 10, cy), 4)
    pygame.draw.circle(surface, (255, 255, 255), (cx + 10, cy), 4)
    pygame.draw.circle(surface, (0, 0, 0), (cx - 10, cy), 2)
    pygame.draw.circle(surface, (0, 0, 0), (cx + 10, cy), 2)

def draw_energy_ball(surface, rect, theme):
    anim = abs(math.sin(pygame.time.get_ticks() / 150)) * 3
    pygame.draw.circle(surface, (0, 255, 255), rect.center, rect.width//2 + int(anim))
    pygame.draw.circle(surface, (255, 255, 255), rect.center, rect.width//2 - 2)

def draw_alien(surface, rect, theme, anim_timer):
    color = (min(255, theme["SECONDARY"][0]+50), min(255, theme["SECONDARY"][1]+50), min(255, theme["SECONDARY"][2]+50))
    pygame.draw.ellipse(surface, color, rect)
    offset = math.sin(anim_timer) * 3
    pygame.draw.polygon(surface, theme["SECONDARY"], [(rect.left, rect.centery), (rect.left - 10, rect.bottom + offset), (rect.left + 5, rect.bottom)])
    pygame.draw.polygon(surface, theme["SECONDARY"], [(rect.right, rect.centery), (rect.right + 10, rect.bottom + offset), (rect.right - 5, rect.bottom)])
    pygame.draw.circle(surface, (255, 0, 0), (rect.centerx - 8, rect.centery), 4)
    pygame.draw.circle(surface, (255, 0, 0), (rect.centerx + 8, rect.centery), 4)
