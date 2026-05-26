import pygame
import sys
import math
import random
import os
import json
import time

pygame.init()

# ==========================================
# CONFIG & THEMES
# ==========================================
WIDTH = 800
HEIGHT = 600
FPS = 60

THEMES = {
    "NEON": {
        "BG_COLOR": (20, 15, 35),
        "PRIMARY": (57, 255, 20),    
        "SECONDARY": (255, 20, 147), 
        "TERTIARY": (0, 255, 255),   
        "TEXT": (255, 255, 255),     
        "TEXT_MUTED": (100, 100, 120),
        "PANEL": (30, 30, 50),       
        "SHADOW": (10, 5, 20),
        "SNAKE_HEAD": (57, 255, 20),
        "SNAKE_BODY": (100, 255, 100),
        "FOOD": (255, 20, 147)
    },
    "RETRO": {
        "BG_COLOR": (40, 40, 40),
        "PRIMARY": (245, 152, 66),   
        "SECONDARY": (66, 245, 138), 
        "TERTIARY": (245, 66, 66),   
        "TEXT": (230, 230, 230),
        "TEXT_MUTED": (150, 150, 150),
        "PANEL": (60, 60, 60),
        "SHADOW": (20, 20, 20),
        "SNAKE_HEAD": (245, 152, 66),
        "SNAKE_BODY": (200, 120, 50),
        "FOOD": (245, 66, 66)
    },
    "MIDNIGHT": {
        "BG_COLOR": (10, 10, 15),
        "PRIMARY": (150, 100, 255),  
        "SECONDARY": (100, 200, 255),
        "TERTIARY": (255, 100, 150), 
        "TEXT": (220, 220, 255),
        "TEXT_MUTED": (80, 80, 120),
        "PANEL": (25, 25, 35),
        "SHADOW": (5, 5, 10),
        "SNAKE_HEAD": (150, 100, 255),
        "SNAKE_BODY": (120, 80, 200),
        "FOOD": (255, 100, 150)
    },
    "CYBERPUNK": {
        "BG_COLOR": (25, 0, 51),     
        "PRIMARY": (255, 255, 0),    
        "SECONDARY": (0, 255, 255),  
        "TERTIARY": (255, 0, 60),    
        "TEXT": (255, 255, 255),
        "TEXT_MUTED": (120, 80, 150),
        "PANEL": (50, 0, 80),
        "SHADOW": (10, 0, 20),
        "SNAKE_HEAD": (255, 255, 0),
        "SNAKE_BODY": (200, 200, 0),
        "FOOD": (255, 0, 60)
    }
}

# ==========================================
# DATA MANAGER
# ==========================================
DATA_FILE = "data.json"

DEFAULT_DATA = {
    "theme": "NEON",
    "high_scores": {
        "Snake": 0,
        "Pong": 0,
        "TicTacToe": 0,
        "Flappy": 0,
        "BrickBreaker": 0
    }
}

def load_data():
    if not os.path.exists(DATA_FILE):
        save_data(DEFAULT_DATA)
        return DEFAULT_DATA.copy()
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            for key in DEFAULT_DATA:
                if key not in data:
                    data[key] = DEFAULT_DATA[key]
            for game in DEFAULT_DATA["high_scores"]:
                if game not in data["high_scores"]:
                    data["high_scores"][game] = DEFAULT_DATA["high_scores"][game]
            return data
    except (json.JSONDecodeError, IOError):
        return DEFAULT_DATA.copy()

def save_data(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"Error saving data: {e}")

def get_high_score(game_name):
    data = load_data()
    return data["high_scores"].get(game_name, 0)

def set_high_score(game_name, score):
    data = load_data()
    if game_name not in data["high_scores"] or score > data["high_scores"][game_name]:
        data["high_scores"][game_name] = score
        save_data(data)
        return True
    return False

def get_theme_name():
    data = load_data()
    return data.get("theme", "NEON")

def set_theme_name(name):
    data = load_data()
    data["theme"] = name
    save_data(data)
    update_theme()

# Global Theme
theme_name = get_theme_name()
theme = THEMES.get(theme_name, THEMES["NEON"])

def update_theme():
    global theme_name, theme
    theme_name = get_theme_name()
    theme = THEMES.get(theme_name, THEMES["NEON"])

# ==========================================
# COMMON UTILS
# ==========================================
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Premium Arcade Hub")
clock = pygame.time.Clock()

def draw_text(surface, text, size, x, y, color, shadow_color=None, shadow=True, center=True):
    if shadow_color is None:
        shadow_color = theme["SHADOW"]
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
    pygame.draw.rect(s, (*theme["PANEL"], 230), (0, 0, w, h), border_radius=20)
    surface.blit(s, panel_rect.topleft)
    pygame.draw.rect(surface, border_color, panel_rect, width=4, border_radius=20)
    return panel_rect

# ==========================================
# CHARACTER DRAWING HELPERS
# ==========================================
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

# ==========================================
# GAMES
# ==========================================

# --- SNAKE ---
class SnakeGame:
    def __init__(self):
        self.grid_size = 25
        self.reset()
        
    def reset(self):
        self.snake = [(WIDTH//2, HEIGHT//2)]
        self.dir = (self.grid_size, 0)
        self.last_dir = self.dir
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False
        self.last_move = time.time()
        self.move_delay = 0.15
        self.shake_timer = 0
        self.floating_texts = []
        self.particles = []

    def spawn_food(self):
        while True:
            x = random.randint(1, (WIDTH - self.grid_size*2) // self.grid_size) * self.grid_size
            y = random.randint(1, (HEIGHT - self.grid_size*2) // self.grid_size) * self.grid_size
            if not hasattr(self, 'snake') or (x, y) not in self.snake:
                return (x, y)

    def run(self):
        running = True
        pulse_anim = 0
        high_score = get_high_score("Snake")
        
        while running:
            clock.tick(FPS)
            pulse_anim += 0.1
            self.shake_timer = max(0, self.shake_timer - 1)
            for t in self.floating_texts[:]:
                t['y'] -= 1
                t['alpha'] -= 5
                if t['alpha'] <= 0:
                    self.floating_texts.remove(t)
            for p in self.particles[:]:
                p['life'] -= 1
                if p.get('is_ring'):
                    p['radius'] += 4
                else:
                    p['radius'] -= 0.2
                    p['x'] += p['vx']
                    p['y'] += p['vy']
                if p['life'] <= 0 or p['radius'] <= 0:
                    self.particles.remove(p)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return # Return to menu
                    if not self.game_over:
                        if event.key == pygame.K_UP and self.last_dir != (0, self.grid_size):
                            self.dir = (0, -self.grid_size)
                        elif event.key == pygame.K_DOWN and self.last_dir != (0, -self.grid_size):
                            self.dir = (0, self.grid_size)
                        elif event.key == pygame.K_LEFT and self.last_dir != (self.grid_size, 0):
                            self.dir = (-self.grid_size, 0)
                        elif event.key == pygame.K_RIGHT and self.last_dir != (-self.grid_size, 0):
                            self.dir = (self.grid_size, 0)
                    else:
                        if event.key == pygame.K_SPACE:
                            self.reset()
                            high_score = get_high_score("Snake")

            if not self.game_over:
                if time.time() - self.last_move > self.move_delay:
                    head_x, head_y = self.snake[0]
                    new_head = (head_x + self.dir[0], head_y + self.dir[1])

                    if (new_head[0] < 0 or new_head[0] >= WIDTH or 
                        new_head[1] < 0 or new_head[1] >= HEIGHT or 
                        new_head in self.snake):
                        self.game_over = True
                        set_high_score("Snake", self.score)
                    else:
                        self.snake.insert(0, new_head)
                        if new_head == self.food:
                            self.score += 10
                            self.move_delay = max(0.04, self.move_delay - 0.005)
                            self.shake_timer = 10
                            self.floating_texts.append({'x': self.food[0], 'y': self.food[1], 'alpha': 255})
                            self.particles.append({'x': self.food[0]+12, 'y': self.food[1]+12, 'vx': 0, 'vy': 0, 'life': 20, 'radius': 5, 'color': theme["PRIMARY"], 'is_ring': True})
                            for _ in range(15):
                                self.particles.append({
                                    'x': self.food[0]+12, 'y': self.food[1]+12, 
                                    'vx': random.uniform(-6, 6), 'vy': random.uniform(-6, 6),
                                    'life': 30, 'radius': random.uniform(3, 8), 'color': theme["FOOD"]
                                })
                            self.food = self.spawn_food()
                        else:
                            tail = self.snake.pop()
                            self.particles.append({
                                'x': tail[0]+12, 'y': tail[1]+12,
                                'vx': 0, 'vy': 0, 'life': 15, 'radius': 8, 'color': theme["SNAKE_BODY"]
                            })
                    self.last_dir = self.dir
                    self.last_move = time.time()

            screen.fill(theme["BG_COLOR"])
            grid_color = (min(255, theme["BG_COLOR"][0] + 15), min(255, theme["BG_COLOR"][1] + 15), min(255, theme["BG_COLOR"][2] + 15))
            offset = int(pulse_anim * 15) % self.grid_size
            for x in range(offset - self.grid_size, WIDTH, self.grid_size):
                pygame.draw.line(screen, grid_color, (x, 0), (x, HEIGHT))
            for y in range(offset - self.grid_size, HEIGHT, self.grid_size):
                pygame.draw.line(screen, grid_color, (0, y), (WIDTH, y))

            food_glow = int(abs(math.sin(pulse_anim * 2)) * 8)
            pygame.draw.rect(screen, theme["PRIMARY"], (self.food[0] - food_glow, self.food[1] - food_glow, self.grid_size + food_glow*2, self.grid_size + food_glow*2), border_radius=5)
            draw_apple(screen, self.food[0], self.food[1], self.grid_size)
            
            tongue_out = (math.sin(pulse_anim * 3) > 0.5)
            for i, segment in enumerate(self.snake):
                pulse_scale = math.sin(pulse_anim * 2 - i * 0.5) * 2
                size_mod = int(pulse_scale) if self.move_delay < 0.14 else 0
                if i == 0:
                    draw_snake_head(screen, segment[0]-size_mod, segment[1]-size_mod, self.grid_size+size_mod*2, self.dir[0], self.dir[1], tongue_out, theme)
                else:
                    color = theme["SNAKE_BODY"]
                    pygame.draw.rect(screen, color, (segment[0]+1-size_mod, segment[1]+1-size_mod, self.grid_size-2+size_mod*2, self.grid_size-2+size_mod*2), border_radius=4)
                    pygame.draw.line(screen, theme["SHADOW"], (segment[0]+4, segment[1]+self.grid_size//2), (segment[0]+self.grid_size-4, segment[1]+self.grid_size//2), 2)

            for p in self.particles:
                if p.get('is_ring'):
                    pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), int(p['radius']), max(1, 6 - int(p['radius']/10)))
                else:
                    pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), int(max(1, p['radius'])))
            for t in self.floating_texts:
                draw_text(screen, "+10", 20, t['x'], int(t['y']), theme["PRIMARY"], shadow=False)

            draw_text(screen, f"SCORE: {self.score}", 40, WIDTH//2, 40, theme["PRIMARY"])
            draw_text(screen, f"HIGH SCORE: {max(self.score, high_score)}", 20, WIDTH//2, 80, theme["TEXT_MUTED"])
            draw_text(screen, "Press ESC to exit", 20, 80, 20, theme["TEXT_MUTED"], shadow=False)

            if self.game_over:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                screen.blit(overlay, (0, 0))
                
                draw_panel(screen, 400, 240, theme["SECONDARY"])
                
                draw_text(screen, "GAME OVER", 60, WIDTH//2, HEIGHT//2 - 40, theme["SECONDARY"])
                draw_text(screen, f"Final Score: {self.score}", 30, WIDTH//2, HEIGHT//2 + 20, theme["TEXT"])
                draw_text(screen, "Press SPACE to restart", 20, WIDTH//2, HEIGHT//2 + 70, theme["TEXT_MUTED"])

            if self.shake_timer > 0:
                shake_x = random.randint(-4, 4)
                shake_y = random.randint(-4, 4)
                shook_surface = screen.copy()
                screen.fill(theme["BG_COLOR"])
                screen.blit(shook_surface, (shake_x, shake_y))

            pygame.display.update()

# --- PONG ---
class PongGame:
    def __init__(self):
        self.reset()
        self.particles = []

    def reset(self):
        self.ball = pygame.Rect(WIDTH//2 - 12, HEIGHT//2 - 12, 24, 24)
        start_speed = 4.0
        self.ball_vel = [random.choice([-start_speed, start_speed]), random.choice([-start_speed, start_speed])]
        self.p1 = pygame.Rect(40, HEIGHT//2 - 60, 20, 120)
        self.p2 = pygame.Rect(WIDTH - 60, HEIGHT//2 - 60, 20, 120)
        self.score = [0, 0]
        self.shake_timer = 0
        self.ball_trail = []
        self.pulse_anim = 0

    def add_particles(self, x, y, color, dir_x=0):
        for _ in range(25):
            vx = random.uniform(2, 8) if dir_x > 0 else (random.uniform(-8, -2) if dir_x < 0 else random.uniform(-5, 5))
            vy = random.uniform(-5, 5)
            self.particles.append([[x, y], [vx, vy], random.uniform(3, 8), color])

    def run(self):
        running = True
        high_score = get_high_score("Pong")
        
        while running:
            clock.tick(FPS)
            self.pulse_anim += 0.1
            self.shake_timer = max(0, self.shake_timer - 1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return # Return to menu

            keys = pygame.key.get_pressed()
            if keys[pygame.K_w] and self.p1.top > 0: self.p1.y -= 8
            if keys[pygame.K_s] and self.p1.bottom < HEIGHT: self.p1.y += 8
            if keys[pygame.K_UP] and self.p2.top > 0: self.p2.y -= 8
            if keys[pygame.K_DOWN] and self.p2.bottom < HEIGHT: self.p2.y += 8

            self.ball.x += self.ball_vel[0]
            self.ball.y += self.ball_vel[1]
            
            self.ball_trail.append(self.ball.copy())
            if len(self.ball_trail) > 10:
                self.ball_trail.pop(0)

            if self.ball.top <= 0 or self.ball.bottom >= HEIGHT:
                self.ball_vel[1] *= -1
                self.add_particles(self.ball.centerx, self.ball.centery, theme["TEXT"])
            
            if self.ball.colliderect(self.p1) and self.ball_vel[0] < 0:
                self.ball_vel[0] *= -1.05
                if self.ball_vel[0] > 15: self.ball_vel[0] = 15
                self.shake_timer = 8
                self.add_particles(self.ball.left, self.ball.centery, theme["TERTIARY"], dir_x=1)
            if self.ball.colliderect(self.p2) and self.ball_vel[0] > 0:
                self.ball_vel[0] *= -1.05
                if self.ball_vel[0] < -15: self.ball_vel[0] = -15
                self.shake_timer = 8
                self.add_particles(self.ball.right, self.ball.centery, theme["SECONDARY"], dir_x=-1)

            if self.ball.left <= -50:
                self.score[1] += 1
                self.ball.center = (WIDTH//2, HEIGHT//2)
                self.ball_vel = [4.0, random.choice([-4.0, 4.0])]
                self.ball_trail.clear()
                if self.score[1] > high_score:
                    high_score = self.score[1]
                    set_high_score("Pong", high_score)
            if self.ball.right >= WIDTH + 50:
                self.score[0] += 1
                self.ball.center = (WIDTH//2, HEIGHT//2)
                self.ball_vel = [-4.0, random.choice([-4.0, 4.0])]
                self.ball_trail.clear()
                if self.score[0] > high_score:
                    high_score = self.score[0]
                    set_high_score("Pong", high_score)

            screen.fill(theme["BG_COLOR"])
            
            bg_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            grid_spacing = 40
            bg_alpha = int(20 + math.sin(self.pulse_anim * 0.5) * 15)
            for x in range(0, WIDTH, grid_spacing):
                pygame.draw.line(bg_surf, (*theme["PRIMARY"], bg_alpha), (x, 0), (x, HEIGHT))
            for y in range(0, HEIGHT, grid_spacing):
                pygame.draw.line(bg_surf, (*theme["PRIMARY"], bg_alpha), (0, y), (WIDTH, y))
            screen.blit(bg_surf, (0,0))
            
            pulse_alpha = int(150 + math.sin(self.pulse_anim * 2) * 100)
            net_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            for y in range(0, HEIGHT, 40):
                pygame.draw.rect(net_surface, (*theme["SECONDARY"], pulse_alpha), (WIDTH//2 - 2, y + 10, 4, 20), border_radius=2)
            screen.blit(net_surface, (0,0))
                
            draw_spaceship_paddle(screen, self.p1, theme, True)
            draw_spaceship_paddle(screen, self.p2, theme, True)
            
            for i, tr in enumerate(self.ball_trail):
                alpha = int(100 + 155 * (i / max(1, len(self.ball_trail))))
                radius = int(4 + 8 * (i / max(1, len(self.ball_trail))))
                blend = i / max(1, len(self.ball_trail))
                c1, c2 = theme["TEXT"], theme["PRIMARY"]
                color = (int(c1[0]*(1-blend) + c2[0]*blend), int(c1[1]*(1-blend) + c2[1]*blend), int(c1[2]*(1-blend) + c2[2]*blend), alpha)
                
                tr_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                pygame.draw.circle(tr_surf, color, (radius, radius), radius)
                screen.blit(tr_surf, (tr.centerx - radius, tr.centery - radius))
                
            draw_energy_ball(screen, self.ball, theme)
            
            for p in self.particles[:]:
                p[0][0] += p[1][0]
                p[0][1] += p[1][1]
                p[2] -= 0.2
                if p[2] <= 0:
                    self.particles.remove(p)
                else:
                    pygame.draw.circle(screen, p[3], (int(p[0][0]), int(p[0][1])), int(p[2]))

            draw_text(screen, str(self.score[0]), 100, WIDTH//4, 100, theme["TERTIARY"])
            draw_text(screen, str(self.score[1]), 100, 3*WIDTH//4, 100, theme["SECONDARY"])
            draw_text(screen, "P1: W/S | P2: UP/DOWN | ESC: Exit", 20, WIDTH//2, HEIGHT - 30, theme["TEXT_MUTED"])

            if self.shake_timer > 0:
                shake_x = random.randint(-5, 5)
                shake_y = random.randint(-5, 5)
                shook_surface = screen.copy()
                screen.fill(theme["BG_COLOR"])
                screen.blit(shook_surface, (shake_x, shake_y))

            pygame.display.update()

# --- TIC TAC TOE ---
class TicTacToeGame:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.turn = "X"
        self.winner = None
        self.cell_size = 160
        self.offset_x = (WIDTH - self.cell_size * 3) // 2
        self.offset_y = (HEIGHT - self.cell_size * 3) // 2
        self.anim_timer = 0
        self.pieces_scale = {}

    def check_winner(self):
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != "": return self.board[i][0]
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != "": return self.board[0][i]
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != "": return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != "": return self.board[0][2]
        
        if all(self.board[row][col] != "" for row in range(3) for col in range(3)):
            return "Draw"
        return None

    def run(self):
        running = True
        wins = get_high_score("TicTacToe")
        
        while running:
            clock.tick(FPS)
            self.anim_timer += 0.05
            for k in self.pieces_scale:
                if self.pieces_scale[k] < 1.0:
                    self.pieces_scale[k] = min(1.0, self.pieces_scale[k] + 0.15)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    if event.key == pygame.K_SPACE and self.winner:
                        self.reset()
                
                if event.type == pygame.MOUSEBUTTONDOWN and not self.winner:
                    mx, my = event.pos
                    if self.offset_x < mx < self.offset_x + 3 * self.cell_size and \
                       self.offset_y < my < self.offset_y + 3 * self.cell_size:
                        col = (mx - self.offset_x) // self.cell_size
                        row = (my - self.offset_y) // self.cell_size
                        if self.board[row][col] == "":
                            self.board[row][col] = self.turn
                            self.pieces_scale[(row, col)] = 0.0
                            self.turn = "O" if self.turn == "X" else "X"
                            self.winner = self.check_winner()
                            if self.winner and self.winner != "Draw":
                                wins += 1
                                set_high_score("TicTacToe", wins)

            screen.fill(theme["BG_COLOR"])
            
            # Draw subtle grid glow in background
            glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*theme["PANEL"][:3], 30), (WIDTH//2, HEIGHT//2), 300)
            screen.blit(glow_surf, (0, 0))
            
            mx, my = pygame.mouse.get_pos()
            for row in range(3):
                for col in range(3):
                    cx = self.offset_x + col * self.cell_size
                    cy = self.offset_y + row * self.cell_size
                    if cx < mx < cx + self.cell_size and cy < my < cy + self.cell_size and not self.winner and self.board[row][col] == "":
                        s = pygame.Surface((self.cell_size-10, self.cell_size-10), pygame.SRCALPHA)
                        pygame.draw.rect(s, (*theme["TEXT"][:3], 30), s.get_rect(), border_radius=15)
                        screen.blit(s, (cx+5, cy+5))

            glow_offset = math.sin(self.anim_timer) * 3
            grid_color = theme["PANEL"]
            for i in range(1, 3):
                pygame.draw.line(screen, grid_color, (self.offset_x + i * self.cell_size, self.offset_y), 
                                                (self.offset_x + i * self.cell_size, self.offset_y + 3 * self.cell_size), 10)
                pygame.draw.line(screen, theme["TEXT"], (self.offset_x + i * self.cell_size, self.offset_y), 
                                                (self.offset_x + i * self.cell_size, self.offset_y + 3 * self.cell_size), 4)
                pygame.draw.line(screen, grid_color, (self.offset_x, self.offset_y + i * self.cell_size), 
                                                (self.offset_x + 3 * self.cell_size, self.offset_y + i * self.cell_size), 10)
                pygame.draw.line(screen, theme["TEXT"], (self.offset_x, self.offset_y + i * self.cell_size), 
                                                (self.offset_x + 3 * self.cell_size, self.offset_y + i * self.cell_size), 4)

            for row in range(3):
                for col in range(3):
                    val = self.board[row][col]
                    cx = self.offset_x + col * self.cell_size + self.cell_size // 2
                    cy = self.offset_y + row * self.cell_size + self.cell_size // 2
                    scale = self.pieces_scale.get((row, col), 1.0)
                    if val == "X":
                        size = int((120 + glow_offset) * scale)
                        if size > 0: draw_tictactoe_piece(screen, "X", cx, cy, size, theme["SECONDARY"])
                    elif val == "O":
                        size = int((120 - glow_offset) * scale)
                        if size > 0: draw_tictactoe_piece(screen, "O", cx, cy, size, theme["TERTIARY"])

            draw_text(screen, "Press ESC to exit", 20, 80, 20, theme["TEXT_MUTED"])
            draw_text(screen, f"Total Wins: {wins}", 20, WIDTH - 80, 20, theme["TEXT_MUTED"])

            if self.winner:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                screen.blit(overlay, (0, 0))
                
                panel_color = theme["PRIMARY"] if self.winner == "Draw" else (theme["SECONDARY"] if self.winner == "X" else theme["TERTIARY"])
                
                draw_panel(screen, 400, 240, panel_color)
                
                text = "DRAW!" if self.winner == "Draw" else f"{self.winner} WINS!"
                draw_text(screen, text, 80, WIDTH//2, HEIGHT//2 - 30, panel_color)
                draw_text(screen, "Press SPACE to restart", 25, WIDTH//2, HEIGHT//2 + 50, theme["TEXT"])
            else:
                current_color = theme["SECONDARY"] if self.turn == "X" else theme["TERTIARY"]
                draw_text(screen, f"{self.turn}'s Turn", 30, WIDTH//2, 30, current_color)

            pygame.display.update()

# --- BRICK BREAKER ---
class BrickBreakerGame:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.paddle = pygame.Rect(WIDTH//2 - 50, HEIGHT - 40, 100, 15)
        self.ball = pygame.Rect(WIDTH//2 - 8, HEIGHT//2 - 8, 16, 16)
        self.ball_vel = [3.5, -3.5]
        
        self.bricks = []
        rows = 6
        cols = 10
        b_width = WIDTH // cols
        b_height = 30
        for r in range(rows):
            for c in range(cols):
                color = theme["PRIMARY"] if r < 2 else (theme["SECONDARY"] if r < 4 else theme["TERTIARY"])
                self.bricks.append({"rect": pygame.Rect(c * b_width + 2, r * b_height + 50 + 2, b_width - 4, b_height - 4), "color": color})
                
        self.score = 0
        self.game_over = False
        self.won = False
        self.particles = []
        self.floating_texts = []
        self.ball_trail = []
        self.combo = 0

    def run(self):
        running = True
        high_score = get_high_score("BrickBreaker")
        bg_y = 0
        
        while running:
            clock.tick(FPS)
            bg_y = (bg_y + 1) % 40
            for t in self.floating_texts[:]:
                t['y'] -= 1
                t['alpha'] -= 5
                if t['alpha'] <= 0:
                    self.floating_texts.remove(t)
            for p in self.particles[:]:
                p['life'] -= 1
                p['x'] += p['vx']
                p['y'] += p['vy']
                p['vy'] += 0.2
                if p['life'] <= 0:
                    self.particles.remove(p)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    if event.key == pygame.K_SPACE and (self.game_over or self.won):
                        self.reset()

            if not self.game_over and not self.won:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT] and self.paddle.left > 0:
                    self.paddle.x -= 8
                    self.particles.append({'x': self.paddle.right - 10, 'y': self.paddle.bottom, 'vx': random.uniform(1, 3), 'vy': random.uniform(1, 3), 'life': 15, 'color': theme["TERTIARY"]})
                if keys[pygame.K_RIGHT] and self.paddle.right < WIDTH:
                    self.paddle.x += 8
                    self.particles.append({'x': self.paddle.left + 10, 'y': self.paddle.bottom, 'vx': random.uniform(-3, -1), 'vy': random.uniform(1, 3), 'life': 15, 'color': theme["TERTIARY"]})
                
                if random.random() < 0.3:
                    self.particles.append({'x': self.paddle.centerx + random.uniform(-20, 20), 'y': self.paddle.bottom, 'vx': random.uniform(-1, 1), 'vy': random.uniform(1, 3), 'life': 10, 'color': theme["SECONDARY"]})
                    
                self.ball.x += self.ball_vel[0]
                self.ball.y += self.ball_vel[1]
                
                self.ball_trail.append(self.ball.copy())
                if len(self.ball_trail) > 10:
                    self.ball_trail.pop(0)
                
                if self.ball.left <= 0 or self.ball.right >= WIDTH:
                    self.ball_vel[0] *= -1
                if self.ball.top <= 0:
                    self.ball_vel[1] *= -1
                    
                if self.ball.bottom >= HEIGHT:
                    self.game_over = True
                    if self.score > high_score:
                        set_high_score("BrickBreaker", self.score)
                        
                if self.ball.colliderect(self.paddle) and self.ball_vel[1] > 0:
                    offset = (self.ball.centerx - self.paddle.centerx) / (self.paddle.width / 2)
                    speed = max(3.5, min(12.0, math.hypot(self.ball_vel[0], self.ball_vel[1])))
                    self.ball_vel[0] = offset * speed * 0.8
                    self.ball_vel[1] = -math.sqrt(abs(speed**2 - self.ball_vel[0]**2))
                    self.combo = 0
                    
                hit_index = self.ball.collidelist([b["rect"] for b in self.bricks])
                if hit_index != -1:
                    brick = self.bricks.pop(hit_index)
                    self.ball_vel[0] *= 1.02
                    self.ball_vel[1] *= 1.02
                    self.combo += 1
                    pts = 10 * self.combo
                    self.score += pts
                    
                    self.floating_texts.append({'x': brick["rect"].centerx, 'y': brick["rect"].centery, 'text': f"+{pts}", 'alpha': 255})
                    for _ in range(20):
                        self.particles.append({
                            'x': brick["rect"].centerx, 'y': brick["rect"].centery, 
                            'vx': random.uniform(-6, 6), 'vy': random.uniform(-6, 6),
                            'life': random.randint(20, 40), 'color': brick["color"]
                        })
                    
                    if abs(self.ball.bottom - brick["rect"].top) < 5 and self.ball_vel[1] > 0:
                        self.ball_vel[1] *= -1
                    elif abs(self.ball.top - brick["rect"].bottom) < 5 and self.ball_vel[1] < 0:
                        self.ball_vel[1] *= -1
                    else:
                        self.ball_vel[0] *= -1
                    if len(self.bricks) == 0:
                        self.won = True
                        if self.score > high_score:
                            set_high_score("BrickBreaker", self.score)

            screen.fill(theme["BG_COLOR"])
            for x in range(0, WIDTH, 40):
                pygame.draw.line(screen, (*theme["SHADOW"][:3], 100), (x, 0), (x, HEIGHT))
            for y in range(0, HEIGHT+40, 40):
                pygame.draw.line(screen, (*theme["SHADOW"][:3], 100), (0, y - 40 + bg_y), (WIDTH, y - 40 + bg_y))
            
            for b in self.bricks:
                draw_brick_face(screen, b["rect"], self.ball.y, theme, b["color"])
                
            draw_spaceship_paddle(screen, self.paddle, theme, False)
            for tr in self.ball_trail:
                tr_surf = pygame.Surface((16, 16), pygame.SRCALPHA)
                pygame.draw.ellipse(tr_surf, (*theme["TEXT"], 50), (0,0,16,16))
                screen.blit(tr_surf, (tr.x, tr.y))
                
            draw_energy_ball(screen, self.ball, theme)
            
            for p in self.particles:
                pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), 4)
            for t in self.floating_texts:
                draw_text(screen, t['text'], 20, t['x'], int(t['y']), theme["TEXT"], shadow=False)
                
            if self.combo > 1:
                draw_text(screen, f"{self.combo}x COMBO!", 30, WIDTH//2, HEIGHT//2, theme["TERTIARY"])
            
            draw_text(screen, f"SCORE: {self.score}", 30, 100, 20, theme["TEXT"])
            draw_text(screen, f"HIGH: {max(self.score, high_score)}", 30, WIDTH - 100, 20, theme["TEXT_MUTED"])
            draw_text(screen, "Press ESC to exit", 20, 80, HEIGHT - 20, theme["TEXT_MUTED"], shadow=False)

            if self.game_over or self.won:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                screen.blit(overlay, (0, 0))
                
                draw_panel(screen, 400, 200, theme["PRIMARY"])
                
                msg = "YOU WON!" if self.won else "GAME OVER"
                draw_text(screen, msg, 60, WIDTH//2, HEIGHT//2 - 30, theme["PRIMARY"])
                draw_text(screen, "Press SPACE to restart", 20, WIDTH//2, HEIGHT//2 + 40, theme["TEXT_MUTED"])

            pygame.display.update()

# --- FLAPPY BIRD ---
# Flappy constants (we use existing ones but center in our 800x600 screen if we want, or just draw it taking up the whole screen)
# To make it simple, we adapt it to run on the 800x600 screen.

GRAVITY = 0.35
BIRD_JUMP = -6.5
PIPE_SPEED = 3
PIPE_GAP = 160
PIPE_FREQUENCY = 1500 # ms
GROUND_HEIGHT = 80

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN_PIPE = (115, 191, 46)
GREEN_PIPE_L = (153, 229, 80)
GREEN_PIPE_D = (85, 140, 34)
YELLOW_BIRD = (246, 215, 68)
ORANGE_BEAK = (240, 100, 40)
BROWN_GROUND = (222, 216, 149)
GREEN_GROUND = (115, 191, 46)
GOLD = (255, 215, 0)

class FlappyParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = random.uniform(2, 5)
        self.alpha = 255
        self.vx = random.uniform(-1, 0)
        self.vy = random.uniform(-1, 1)

    def move(self):
        self.x += self.vx
        self.y += self.vy
        self.alpha -= 10
        self.radius -= 0.1

    def draw(self, surface):
        if self.alpha > 0 and self.radius > 0:
            s = pygame.Surface((int(self.radius*2), int(self.radius*2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 255, self.alpha), (int(self.radius), int(self.radius)), int(self.radius))
            surface.blit(s, (int(self.x - self.radius), int(self.y - self.radius)))

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 12
        self.anim_timer = random.uniform(0, math.pi)
        self.collected = False

    def move(self):
        self.x -= PIPE_SPEED
        self.anim_timer += 0.1

    def draw(self, surface):
        if not self.collected:
            offset_y = math.sin(self.anim_timer) * 5
            draw_y = int(self.y + offset_y)
            pygame.draw.circle(surface, (255, 215, 0, 150), (int(self.x), draw_y), self.radius + 3)
            pygame.draw.circle(surface, GOLD, (int(self.x), draw_y), self.radius)
            pygame.draw.circle(surface, WHITE, (int(self.x), draw_y), self.radius - 2, 2)
            pygame.draw.rect(surface, WHITE, (int(self.x - 2), draw_y - 6, 4, 12))
            pygame.draw.rect(surface, WHITE, (int(self.x - 6), draw_y - 2, 12, 4))

    def collide(self, bird):
        if not self.collected:
            dist = math.hypot(self.x - bird.x, self.y - bird.y)
            if dist < self.radius + bird.radius:
                self.collected = True
                return True
        return False

class Bird:
    def __init__(self):
        self.x = int(WIDTH * 0.2)
        self.y = HEIGHT // 2
        self.velocity = 0
        self.radius = 15
        self.angle = 0
        self.anim_timer = 0
        self.particles = []

    def jump(self):
        self.velocity = BIRD_JUMP
        for _ in range(8):
            self.particles.append(FlappyParticle(self.x, self.y + self.radius))

    def move(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.angle = -self.velocity * 3
        if self.angle < -90: self.angle = -90
        elif self.angle > 20: self.angle = 20
        for p in self.particles: p.move()
        self.particles = [p for p in self.particles if p.alpha > 0]

    def hover(self):
        self.anim_timer += 0.1
        self.y = HEIGHT // 2 + math.sin(self.anim_timer) * 10
        self.angle = 0

    def draw(self, surface):
        for p in self.particles: p.draw(surface)
        self.anim_timer += 0.2
        wing_offset = math.sin(self.anim_timer) * 5
        bird_surf = pygame.Surface((50, 50), pygame.SRCALPHA)
        center = (25, 25)
        pygame.draw.circle(bird_surf, BLACK, center, self.radius + 2)
        pygame.draw.circle(bird_surf, YELLOW_BIRD, center, self.radius)
        pygame.draw.polygon(bird_surf, YELLOW_BIRD, [(25, 10), (20, 2), (22, 10)])
        pygame.draw.polygon(bird_surf, YELLOW_BIRD, [(25, 10), (30, 0), (28, 10)])
        pygame.draw.circle(bird_surf, WHITE, (30, 20), 7)
        pygame.draw.circle(bird_surf, BLACK, (32, 20), 3)
        pygame.draw.line(bird_surf, BLACK, (26, 13), (35, 15), 2)
        beak_rect = pygame.Rect(32, 22, 14, 10)
        pygame.draw.ellipse(bird_surf, BLACK, pygame.Rect(31, 21, 16, 12))
        pygame.draw.ellipse(bird_surf, ORANGE_BEAK, beak_rect)
        pygame.draw.line(bird_surf, BLACK, (32, 27), (44, 27), 2)
        wing_rect = pygame.Rect(8, 22 + wing_offset, 16, 10)
        pygame.draw.ellipse(bird_surf, BLACK, pygame.Rect(7, 21 + wing_offset, 18, 12))
        pygame.draw.ellipse(bird_surf, WHITE, wing_rect)
        rotated_bird = pygame.transform.rotate(bird_surf, self.angle)
        new_rect = rotated_bird.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated_bird, new_rect.topleft)

class Pipe:
    def __init__(self):
        self.x = WIDTH
        self.bottom_height = random.randint(50, HEIGHT - GROUND_HEIGHT - PIPE_GAP - 50)
        self.top_height = HEIGHT - GROUND_HEIGHT - self.bottom_height - PIPE_GAP
        self.width = 60
        self.passed = False

    def move(self):
        self.x -= PIPE_SPEED

    def draw_single_pipe(self, surface, x, y, width, height, is_top):
        pygame.draw.rect(surface, BLACK, (x-2, y, width+4, height))
        pygame.draw.rect(surface, GREEN_PIPE, (x, y, width, height))
        pygame.draw.rect(surface, GREEN_PIPE_L, (x + 4, y, 8, height))
        pygame.draw.rect(surface, GREEN_PIPE_D, (x + width - 12, y, 10, height))
        pygame.draw.rect(surface, BLACK, (x + width - 2, y, 2, height))
        cap_height = 26
        cap_width = width + 12
        cap_x = x - 6
        cap_y = y + height - cap_height if is_top else y
        pygame.draw.rect(surface, BLACK, (cap_x-2, cap_y-2, cap_width+4, cap_height+4))
        pygame.draw.rect(surface, GREEN_PIPE, (cap_x, cap_y, cap_width, cap_height))
        pygame.draw.rect(surface, GREEN_PIPE_L, (cap_x + 4, cap_y, 8, cap_height))
        pygame.draw.rect(surface, GREEN_PIPE_D, (cap_x + cap_width - 12, cap_y, 10, cap_height))
        pygame.draw.rect(surface, BLACK, (cap_x + cap_width - 2, cap_y, 2, cap_height))

    def draw(self, surface):
        self.draw_single_pipe(surface, self.x, 0, self.width, self.top_height, True)
        self.draw_single_pipe(surface, self.x, HEIGHT - GROUND_HEIGHT - self.bottom_height, self.width, self.bottom_height, False)

    def collide(self, bird):
        hitbox_radius = bird.radius - 2
        if bird.x + hitbox_radius > self.x and bird.x - hitbox_radius < self.x + self.width:
            if bird.y - hitbox_radius < self.top_height or bird.y + hitbox_radius > HEIGHT - GROUND_HEIGHT - self.bottom_height:
                return True
        return False

class Cloud:
    def __init__(self):
        self.x = random.randint(WIDTH, WIDTH + 200)
        self.y = random.randint(50, 250)
        self.speed = random.uniform(0.5, 1.5)
        self.scale = random.uniform(0.6, 1.2)

    def move(self):
        self.x -= self.speed
        if self.x < -100:
            self.x = WIDTH + random.randint(10, 100)
            self.y = random.randint(50, 250)

    def draw(self, surface):
        circles = [(0, 0, 20), (20, -10, 25), (40, 0, 20), (20, 10, 20)]
        for cx, cy, r in circles:
            pygame.draw.circle(surface, WHITE, (int(self.x + cx * self.scale), int(self.y + cy * self.scale)), int(r * self.scale))

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT//2)
        self.size = random.randint(1, 2)
        self.twinkle_speed = random.uniform(0.02, 0.05)
        self.timer = random.uniform(0, math.pi*2)

    def draw(self, surface, darkness):
        if darkness > 0:
            self.timer += self.twinkle_speed
            alpha = int(darkness * (150 + math.sin(self.timer) * 100))
            s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 255, alpha), (self.size, self.size), self.size)
            surface.blit(s, (self.x, self.y))

class Cityscape:
    def __init__(self):
        self.buildings = []
        x = 0
        while x < WIDTH * 2:
            width = random.randint(40, 100)
            height = random.randint(100, 300)
            self.buildings.append({"x": x, "w": width, "h": height, "windows": [random.random() > 0.3 for _ in range(10)]})
            x += width

    def move(self):
        for b in self.buildings:
            b["x"] -= PIPE_SPEED * 0.3
        if self.buildings[0]["x"] + self.buildings[0]["w"] < 0:
            b = self.buildings.pop(0)
            b["x"] = self.buildings[-1]["x"] + self.buildings[-1]["w"]
            self.buildings.append(b)

    def draw(self, surface, darkness):
        ground_y = HEIGHT - GROUND_HEIGHT
        b_color = (max(20, 100 - int(80*darkness)), max(20, 100 - int(80*darkness)), max(30, 120 - int(90*darkness)))
        for b in self.buildings:
            pygame.draw.rect(surface, b_color, (b["x"], ground_y - b["h"], b["w"], b["h"]))
            if darkness > 0.5:
                window_w = 8
                window_h = 12
                wx = b["x"] + 10
                wy = ground_y - b["h"] + 20
                for i, w_on in enumerate(b["windows"]):
                    if w_on:
                        pygame.draw.rect(surface, (255, 255, 100, int((darkness - 0.5) * 2 * 255)), (wx, wy, window_w, window_h))
                    wy += 25
                    if wy > ground_y - 20:
                        break

def draw_celestial(surface, score):
    cycle = (score % 40) / 40.0
    sun_x = int(WIDTH - (cycle * WIDTH * 2)) + WIDTH//2
    moon_x = int(WIDTH - ((cycle - 0.5) * WIDTH * 2)) + WIDTH//2
    sun_y = int(200 + math.sin(cycle * math.pi * 2) * 150)
    moon_y = int(200 + math.sin((cycle - 0.5) * math.pi * 2) * 150)
    pygame.draw.circle(surface, (255, 255, 150), (sun_x, sun_y), 40)
    pygame.draw.circle(surface, (255, 200, 50, 100), (sun_x, sun_y), 50)
    pygame.draw.circle(surface, (220, 220, 240), (moon_x, moon_y), 35)
    pygame.draw.circle(surface, (180, 180, 200), (moon_x+10, moon_y-10), 8)
    pygame.draw.circle(surface, (180, 180, 200), (moon_x-5, moon_y+15), 5)
    pygame.draw.circle(surface, (180, 180, 200), (moon_x-15, moon_y-5), 10)

def get_sky_time_factors(score):
    cycle = (score % 40) / 40.0
    darkness = 0.0
    if cycle < 0.25:
        progress = cycle / 0.25
        r = int(112 + (255 - 112) * progress)
        g = int(197 - (197 - 100) * progress)
        b = int(206 - (206 - 100) * progress)
        darkness = progress * 0.5
    elif cycle < 0.5:
        progress = (cycle - 0.25) / 0.25
        r = int(255 - (255 - 10) * progress)
        g = int(100 - (100 - 15) * progress)
        b = int(100 - (100 - 40) * progress)
        darkness = 0.5 + progress * 0.5
    elif cycle < 0.75:
        progress = (cycle - 0.5) / 0.25
        r = int(10 + (255 - 10) * progress)
        g = int(15 + (150 - 15) * progress)
        b = int(40 + (100 - 40) * progress)
        darkness = 1.0 - progress * 0.5
    else:
        progress = (cycle - 0.75) / 0.25
        r = int(255 - (255 - 112) * progress)
        g = int(150 + (197 - 150) * progress)
        b = int(100 + (206 - 100) * progress)
        darkness = 0.5 - progress * 0.5
    return (r, g, b), darkness

def draw_ground(surface, scroll):
    ground_y = HEIGHT - GROUND_HEIGHT
    pygame.draw.rect(surface, BROWN_GROUND, (0, ground_y, WIDTH, GROUND_HEIGHT))
    pygame.draw.rect(surface, GREEN_GROUND, (0, ground_y, WIDTH, 15))
    pygame.draw.rect(surface, BLACK, (0, ground_y-2, WIDTH, 2))
    pygame.draw.rect(surface, BLACK, (0, ground_y+15, WIDTH, 2))
    stripe_width = 20
    for i in range(-1, WIDTH // stripe_width + 2):
        x = i * stripe_width - (scroll % stripe_width)
        pygame.draw.line(surface, GREEN_PIPE_D, (x, ground_y), (x - 10, ground_y + 15), 3)

class FlappyGame:
    def run(self):
        bird = Bird()
        pipes = []
        clouds = [Cloud() for _ in range(4)]
        stars = [Star() for _ in range(40)]
        cityscape = Cityscape()
        coins = []
        score = 0
        high_score = get_high_score("Flappy")
        game_state = 0 
        last_pipe_time = pygame.time.get_ticks()
        ground_scroll = 0
        running = True
        speed_lines = [{'y': random.randint(0, HEIGHT), 'speed': random.uniform(5, 15), 'length': random.randint(20, 100), 'x': random.randint(0, WIDTH)} for _ in range(10)]
        flash_alpha = 0

        while running:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if game_state == 1:
                            game_state = 3 
                        else:
                            return # Exit to main menu
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        if game_state == 0:
                            game_state = 1
                            bird.jump()
                            last_pipe_time = pygame.time.get_ticks()
                        elif game_state == 1:
                            bird.jump()
                        elif game_state == 2:
                            bird = Bird()
                            pipes.clear()
                            coins.clear()
                            score = 0
                            game_state = 0
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if game_state == 0:
                        game_state = 1
                        bird.jump()
                        last_pipe_time = pygame.time.get_ticks()
                    elif game_state == 1:
                        bird.jump()
                    elif game_state == 2:
                        bird = Bird()
                        pipes.clear()
                        coins.clear()
                        score = 0
                        game_state = 0

            if game_state == 0: 
                bird.hover()
                ground_scroll += PIPE_SPEED
                for cloud in clouds: cloud.move()
                cityscape.move()

            elif game_state == 1: 
                bird.move()
                ground_scroll += PIPE_SPEED
                for cloud in clouds: cloud.move()
                cityscape.move()
                
                for sl in speed_lines:
                    sl['x'] -= sl['speed']
                    if sl['x'] + sl['length'] < 0:
                        sl['x'] = WIDTH + random.randint(10, 50)
                        sl['y'] = random.randint(0, HEIGHT)

                if bird.y + bird.radius >= HEIGHT - GROUND_HEIGHT or bird.y - bird.radius <= 0:
                    game_state = 2
                    flash_alpha = 255

                time_now = pygame.time.get_ticks()
                if time_now - last_pipe_time > PIPE_FREQUENCY:
                    new_pipe = Pipe()
                    pipes.append(new_pipe)
                    if random.random() > 0.5:
                        coins.append(Coin(new_pipe.x + new_pipe.width//2, new_pipe.top_height + PIPE_GAP//2))
                    last_pipe_time = time_now

                for pipe in pipes:
                    pipe.move()
                    if pipe.collide(bird): 
                        game_state = 2
                        flash_alpha = 255
                    if pipe.x + pipe.width < bird.x and not pipe.passed:
                        score += 1
                        pipe.passed = True
                
                for coin in coins:
                    coin.move()
                    if coin.collide(bird):
                        score += 5 
                
                pipes = [pipe for pipe in pipes if pipe.x + pipe.width > -50]
                coins = [coin for coin in coins if coin.x + coin.radius > -50 and not coin.collected]

            elif game_state == 2: 
                if bird.y + bird.radius < HEIGHT - GROUND_HEIGHT:
                    bird.move()
                if score > high_score:
                    high_score = score
                    set_high_score("Flappy", high_score)

            sky_color, darkness = get_sky_time_factors(score)
            for y in range(HEIGHT):
                r = min(255, max(0, sky_color[0] - int(y * 0.1)))
                g = min(255, max(0, sky_color[1] - int(y * 0.1)))
                b = min(255, max(0, sky_color[2] - int(y * 0.05)))
                pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
                
            draw_celestial(screen, score)
            for star in stars: star.draw(screen, darkness)
                
            if game_state == 1:
                sl_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                for sl in speed_lines:
                    pygame.draw.line(sl_surf, (255, 255, 255, 50), (sl['x'], sl['y']), (sl['x'] + sl['length'], sl['y']), 2)
                screen.blit(sl_surf, (0, 0))
                
            cityscape.draw(screen, darkness)
            for cloud in clouds: cloud.draw(screen)
            for pipe in pipes: pipe.draw(screen)
            for coin in coins: coin.draw(screen)
            
            draw_ground(screen, ground_scroll)
            bird.draw(screen)
            
            if game_state == 0:
                draw_text(screen, "FLAPPY BIRD", 60, WIDTH//2, HEIGHT//2 - 100, YELLOW_BIRD, BLACK)
                draw_text(screen, "Press SPACE to fly", 30, WIDTH//2, HEIGHT//2 + 80, WHITE, BLACK)
                draw_text(screen, "Press ESC to return to Hub", 20, 100, 20, WHITE, BLACK)
            elif game_state == 1:
                draw_text(screen, str(score), 80, WIDTH//2, 100, WHITE, BLACK)
            elif game_state == 2:
                panel_rect = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 - 100, 240, 200)
                pygame.draw.rect(screen, (222, 216, 149), panel_rect, border_radius=15)
                pygame.draw.rect(screen, BLACK, panel_rect, width=4, border_radius=15)
                draw_text(screen, "GAME OVER", 50, WIDTH//2, HEIGHT//2 - 150, (255, 50, 50), BLACK)
                draw_text(screen, "SCORE", 25, WIDTH//2, HEIGHT//2 - 60, (240, 100, 40), shadow=False)
                draw_text(screen, str(score), 50, WIDTH//2, HEIGHT//2 - 20, WHITE, BLACK)
                draw_text(screen, "BEST", 25, WIDTH//2, HEIGHT//2 + 30, (240, 100, 40), shadow=False)
                draw_text(screen, str(high_score), 50, WIDTH//2, HEIGHT//2 + 70, WHITE, BLACK)
                draw_text(screen, "Press SPACE to Restart", 20, WIDTH//2, HEIGHT//2 + 150, WHITE, BLACK)
                draw_text(screen, "Press ESC to return to Hub", 20, WIDTH//2, HEIGHT//2 + 180, WHITE, BLACK)
            elif game_state == 3: 
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                screen.blit(overlay, (0, 0))
                draw_text(screen, "PAUSED", 70, WIDTH//2, HEIGHT//2, WHITE, BLACK)
                draw_text(screen, "Press ESC to Resume", 25, WIDTH//2, HEIGHT//2 + 60, WHITE, BLACK)

            if flash_alpha > 0:
                flash_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                flash_surf.fill((255, 0, 0, int(flash_alpha)))
                screen.blit(flash_surf, (0, 0))
                flash_alpha = max(0, flash_alpha - 15)

            pygame.display.update()

# --- SPACE SHOOTER ---
class SpaceShooterGame:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.player = pygame.Rect(WIDTH//2 - 25, HEIGHT - 60, 50, 20)
        self.bullets = []
        self.aliens = []
        self.particles = []
        self.floating_texts = []
        self.score = 0
        self.game_state = 0
        self.alien_speed = 2.0
        self.last_shot = 0
        self.anim_timer = 0
        self.stars_bg = [{'x': random.randint(0, WIDTH), 'y': random.randint(0, HEIGHT), 'speed': random.uniform(0.5, 1.5), 'size': random.uniform(1, 2)} for _ in range(60)]
        self.stars_fg = [{'x': random.randint(0, WIDTH), 'y': random.randint(0, HEIGHT), 'speed': random.uniform(3, 6), 'size': random.uniform(2, 4)} for _ in range(30)]

    def spawn_alien(self):
        x = random.randint(50, WIDTH - 50)
        self.aliens.append({'rect': pygame.Rect(x, -40, 40, 30), 'hp': 1})

    def run(self):
        running = True
        high_score = get_high_score("SpaceShooter")
        spawn_timer = 0
        
        while running:
            clock.tick(FPS)
            self.anim_timer += 0.1
            
            for t in self.floating_texts[:]:
                t['y'] -= 1
                t['alpha'] -= 5
                if t['alpha'] <= 0: self.floating_texts.remove(t)
            for p in self.particles[:]:
                p['life'] -= 1
                if p.get('type') == 'shockwave':
                    p['radius'] = p.get('radius', 5) + 5
                elif p.get('type') == 'muzzle':
                    p['radius'] = p.get('radius', 15) - 3
                else:
                    p['x'] += p['vx']
                    p['y'] += p['vy']
                    if p.get('type') == 'thruster': p['life'] -= 1
                if p['life'] <= 0 or p.get('radius', 1) <= 0: self.particles.remove(p)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: return
                    if event.key == pygame.K_SPACE:
                        if self.game_state == 0:
                            self.game_state = 1
                        elif self.game_state == 2:
                            self.reset()
            
            if self.game_state == 1:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT] and self.player.left > 0: self.player.x -= 7
                if keys[pygame.K_RIGHT] and self.player.right < WIDTH: self.player.x += 7
                
                self.particles.append({'x': self.player.centerx + random.uniform(-10, 10), 'y': self.player.bottom, 'vx': random.uniform(-1, 1), 'vy': random.uniform(3, 8), 'life': random.randint(10, 20), 'color': (255, 150, 50), 'type': 'thruster'})

                if keys[pygame.K_SPACE]:
                    now = pygame.time.get_ticks()
                    if now - self.last_shot > 250:
                        self.bullets.append(pygame.Rect(self.player.centerx - 3, self.player.top - 15, 6, 15))
                        self.particles.append({'x': self.player.centerx, 'y': self.player.top, 'vx': 0, 'vy': 0, 'life': 5, 'color': (0, 255, 255), 'radius': 15, 'type': 'muzzle'})
                        self.last_shot = now

                spawn_timer += 1
                if spawn_timer > max(20, 60 - self.score // 50):
                    self.spawn_alien()
                    spawn_timer = 0
                    self.alien_speed = min(8.0, 2.0 + self.score / 500.0)

                for b in self.bullets[:]:
                    b.y -= 10
                    if b.bottom < 0: self.bullets.remove(b)

                for a in self.aliens[:]:
                    a['rect'].y += self.alien_speed
                    if a['rect'].colliderect(self.player):
                        self.game_state = 2
                        if self.score > high_score: set_high_score("SpaceShooter", self.score)
                    elif a['rect'].top > HEIGHT:
                        self.aliens.remove(a)
                        
                    for b in self.bullets[:]:
                        if b.colliderect(a['rect']):
                            if b in self.bullets: self.bullets.remove(b)
                            if a in self.aliens: self.aliens.remove(a)
                            self.score += 10
                            self.floating_texts.append({'x': a['rect'].centerx, 'y': a['rect'].centery, 'text': "+10", 'alpha': 255})
                            self.particles.append({'x': a['rect'].centerx, 'y': a['rect'].centery, 'vx': 0, 'vy': 0, 'life': 20, 'radius': 5, 'color': theme["SECONDARY"], 'type': 'shockwave'})
                            for _ in range(25):
                                self.particles.append({'x': a['rect'].centerx, 'y': a['rect'].centery, 'vx': random.uniform(-8, 8), 'vy': random.uniform(-8, 8), 'life': random.randint(15, 30), 'color': theme["SECONDARY"]})
                            break

            screen.fill((10, 10, 20))
            for star in self.stars_bg:
                star['y'] += star['speed']
                if star['y'] > HEIGHT: star['y'] = 0
                pygame.draw.circle(screen, (150, 150, 200, 100), (star['x'], int(star['y'])), int(star['size']))
            for star in self.stars_fg:
                star['y'] += star['speed']
                if star['y'] > HEIGHT: star['y'] = 0
                pygame.draw.circle(screen, (255, 255, 255, 200), (star['x'], int(star['y'])), int(star['size']))

            for b in self.bullets:
                pygame.draw.rect(screen, (0, 255, 255), b, border_radius=3)
                pygame.draw.rect(screen, (255, 255, 255), (b.x+1, b.y+1, b.width-2, b.height-2), border_radius=3)

            for a in self.aliens:
                draw_alien(screen, a['rect'], theme, self.anim_timer)

            if self.game_state == 1:
                draw_spaceship_paddle(screen, self.player, theme, False)

            for p in self.particles:
                if p.get('type') == 'shockwave':
                    pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), int(p.get('radius', 5)), max(1, 5 - int(p.get('radius', 5)/15)))
                elif p.get('type') == 'muzzle':
                    pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), int(p.get('radius', 5)))
                else:
                    pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), int(p.get('radius', 4)))
            for t in self.floating_texts:
                draw_text(screen, t['text'], 20, int(t['x']), int(t['y']), theme["TEXT"], shadow=False)

            if self.game_state == 0:
                draw_text(screen, "SPACE SHOOTER", 60, WIDTH//2, HEIGHT//2 - 50, theme["SECONDARY"], theme["SHADOW"])
                draw_text(screen, "Press SPACE to start", 30, WIDTH//2, HEIGHT//2 + 50, theme["TEXT"])
                draw_text(screen, "Press ESC to return to Hub", 20, 100, 20, theme["TEXT_MUTED"])
            elif self.game_state == 1:
                draw_text(screen, f"{self.score}", 60, WIDTH//2, 50, theme["TEXT"], theme["SHADOW"])
            elif self.game_state == 2:
                draw_panel(screen, 300, 240, theme["SECONDARY"])
                draw_text(screen, "GAME OVER", 50, WIDTH//2, HEIGHT//2 - 160, theme["SECONDARY"], theme["SHADOW"])
                draw_text(screen, "SCORE", 25, WIDTH//2, HEIGHT//2 - 80, theme["TEXT_MUTED"], shadow=False)
                draw_text(screen, str(self.score), 50, WIDTH//2, HEIGHT//2 - 40, theme["TEXT"])
                draw_text(screen, "BEST", 25, WIDTH//2, HEIGHT//2 + 10, theme["TEXT_MUTED"], shadow=False)
                draw_text(screen, str(high_score), 50, WIDTH//2, HEIGHT//2 + 50, theme["TEXT"])
                draw_text(screen, "Press SPACE to Restart", 20, WIDTH//2, HEIGHT//2 + 150, theme["TEXT"])
                draw_text(screen, "Press ESC to return to Hub", 20, WIDTH//2, HEIGHT//2 + 180, theme["TEXT_MUTED"])

            pygame.display.update()

# --- NEON TETRIS ---
TETROMINOS = {
    'I': [[1, 1, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'Z': [[1, 1, 0], [0, 1, 1]]
}
TETROMINO_COLORS = {
    'I': (0, 255, 255), 'J': (0, 0, 255), 'L': (255, 165, 0),
    'O': (255, 255, 0), 'S': (0, 255, 0), 'T': (128, 0, 128), 'Z': (255, 0, 0)
}

class TetrisGame:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.grid_w = 10
        self.grid_h = 20
        self.cell_size = 25
        self.grid = [[None for _ in range(self.grid_w)] for _ in range(self.grid_h)]
        self.score = 0
        self.game_state = 0
        self.particles = []
        self.floating_texts = []
        self.spawn_piece()
        self.drop_timer = 0
        self.drop_speed = 30
        self.anim_timer = 0
        self.flash_alpha = 0

    def spawn_piece(self):
        shape_name = random.choice(list(TETROMINOS.keys()))
        self.current_piece = {
            'shape': TETROMINOS[shape_name],
            'color': TETROMINO_COLORS[shape_name],
            'x': self.grid_w // 2 - len(TETROMINOS[shape_name][0]) // 2,
            'y': 0
        }
        if self.check_collision(0, 0, self.current_piece['shape']):
            self.game_state = 2

    def check_collision(self, dx, dy, shape):
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = self.current_piece['x'] + x + dx
                    new_y = self.current_piece['y'] + y + dy
                    if new_x < 0 or new_x >= self.grid_w or new_y >= self.grid_h:
                        return True
                    if new_y >= 0 and self.grid[new_y][new_x]:
                        return True
        return False

    def rotate_piece(self):
        shape = self.current_piece['shape']
        new_shape = [[shape[y][x] for y in range(len(shape)-1, -1, -1)] for x in range(len(shape[0]))]
        if not self.check_collision(0, 0, new_shape):
            self.current_piece['shape'] = new_shape
        elif not self.check_collision(1, 0, new_shape):
            self.current_piece['x'] += 1
            self.current_piece['shape'] = new_shape
        elif not self.check_collision(-1, 0, new_shape):
            self.current_piece['x'] -= 1
            self.current_piece['shape'] = new_shape

    def lock_piece(self):
        for y, row in enumerate(self.current_piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece['y'] + y][self.current_piece['x'] + x] = self.current_piece['color']
        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self):
        lines_cleared = 0
        y = self.grid_h - 1
        while y >= 0:
            if all(self.grid[y]):
                lines_cleared += 1
                for x in range(self.grid_w):
                    color = self.grid[y][x]
                    px = WIDTH//2 - (self.grid_w*self.cell_size)//2 + x*self.cell_size + self.cell_size//2
                    py = HEIGHT//2 - (self.grid_h*self.cell_size)//2 + y*self.cell_size + self.cell_size//2
                    for _ in range(5):
                        self.particles.append({'x': px, 'y': py, 'vx': random.uniform(-4, 4), 'vy': random.uniform(-4, 4), 'life': 20, 'color': color})
                del self.grid[y]
                self.grid.insert(0, [None for _ in range(self.grid_w)])
            else:
                y -= 1
        if lines_cleared > 0:
            pts = [0, 100, 300, 500, 800][lines_cleared]
            self.score += pts
            self.drop_speed = max(5, 30 - self.score // 500)
            self.floating_texts.append({'x': WIDTH//2, 'y': HEIGHT//2, 'text': f"+{pts}", 'alpha': 255})
            self.flash_alpha = 255

    def run(self):
        running = True
        high_score = get_high_score("Tetris")
        
        while running:
            clock.tick(FPS)
            self.anim_timer += 0.1
            
            for p in self.particles[:]:
                p['x'] += p['vx']
                p['y'] += p['vy']
                p['life'] -= 1
                if p['life'] <= 0: self.particles.remove(p)
            for t in self.floating_texts[:]:
                t['y'] -= 1
                t['alpha'] -= 5
                if t['alpha'] <= 0: self.floating_texts.remove(t)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: return
                    if event.key == pygame.K_SPACE:
                        if self.game_state == 0: self.game_state = 1
                        elif self.game_state == 2: self.reset()
                        elif self.game_state == 1:
                            start_y = self.current_piece['y']
                            while not self.check_collision(0, 1, self.current_piece['shape']):
                                self.current_piece['y'] += 1
                                
                            for y, row in enumerate(self.current_piece['shape']):
                                for x, cell in enumerate(row):
                                    if cell:
                                        px = WIDTH//2 - (self.grid_w*self.cell_size)//2 + (self.current_piece['x'] + x) * self.cell_size + self.cell_size//2
                                        for drop_y in range(start_y, self.current_piece['y'], max(1, (self.current_piece['y']-start_y)//5)):
                                            py = HEIGHT//2 - (self.grid_h*self.cell_size)//2 + (drop_y + y) * self.cell_size + self.cell_size//2
                                            self.particles.append({'x': px, 'y': py, 'vx': 0, 'vy': -2, 'life': 10, 'color': self.current_piece['color']})
                                            
                            self.lock_piece()
                            if self.game_state == 2 and self.score > high_score:
                                set_high_score("Tetris", self.score)
                    if self.game_state == 1:
                        if event.key == pygame.K_LEFT and not self.check_collision(-1, 0, self.current_piece['shape']):
                            self.current_piece['x'] -= 1
                        if event.key == pygame.K_RIGHT and not self.check_collision(1, 0, self.current_piece['shape']):
                            self.current_piece['x'] += 1
                        if event.key == pygame.K_UP:
                            self.rotate_piece()
                        if event.key == pygame.K_DOWN and not self.check_collision(0, 1, self.current_piece['shape']):
                            self.current_piece['y'] += 1

            if self.game_state == 1:
                self.drop_timer += 1
                if self.drop_timer >= self.drop_speed:
                    self.drop_timer = 0
                    if not self.check_collision(0, 1, self.current_piece['shape']):
                        self.current_piece['y'] += 1
                    else:
                        self.lock_piece()
                        if self.game_state == 2 and self.score > high_score:
                            set_high_score("Tetris", self.score)

            screen.fill((10, 10, 20))
            
            grid_px_w = self.grid_w * self.cell_size
            grid_px_h = self.grid_h * self.cell_size
            offset_x = WIDTH//2 - grid_px_w//2
            offset_y = HEIGHT//2 - grid_px_h//2
            
            pygame.draw.rect(screen, (30, 30, 50), (offset_x, offset_y, grid_px_w, grid_px_h))
            for x in range(self.grid_w + 1):
                pygame.draw.line(screen, (50, 50, 70), (offset_x + x * self.cell_size, offset_y), (offset_x + x * self.cell_size, offset_y + grid_px_h))
            for y in range(self.grid_h + 1):
                pygame.draw.line(screen, (50, 50, 70), (offset_x, offset_y + y * self.cell_size), (offset_x + grid_px_w, offset_y + y * self.cell_size))

            for y in range(self.grid_h):
                for x in range(self.grid_w):
                    if self.grid[y][x]:
                        pygame.draw.rect(screen, self.grid[y][x], (offset_x + x*self.cell_size + 1, offset_y + y*self.cell_size + 1, self.cell_size-2, self.cell_size-2), border_radius=3)
                        pygame.draw.rect(screen, (255, 255, 255), (offset_x + x*self.cell_size + 2, offset_y + y*self.cell_size + 2, self.cell_size-4, self.cell_size-4), width=1, border_radius=3)

            if self.game_state == 1:
                ghost_y = self.current_piece['y']
                while not self.check_collision(0, ghost_y - self.current_piece['y'] + 1, self.current_piece['shape']):
                    ghost_y += 1

                for y, row in enumerate(self.current_piece['shape']):
                    for x, cell in enumerate(row):
                        if cell:
                            px = offset_x + (self.current_piece['x'] + x) * self.cell_size
                            
                            py_ghost = offset_y + (ghost_y + y) * self.cell_size
                            pygame.draw.rect(screen, (*self.current_piece['color'][:3], 50), (px + 1, py_ghost + 1, self.cell_size-2, self.cell_size-2), border_radius=3)
                            
                            py = offset_y + (self.current_piece['y'] + y) * self.cell_size
                            pygame.draw.rect(screen, self.current_piece['color'], (px + 1, py + 1, self.cell_size-2, self.cell_size-2), border_radius=3)
                            pygame.draw.rect(screen, (255, 255, 255), (px + 2, py + 2, self.cell_size-4, self.cell_size-4), width=1, border_radius=3)

            for p in self.particles:
                pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), 4)
            for t in self.floating_texts:
                draw_text(screen, t['text'], 30, int(t['x']), int(t['y']), theme["SECONDARY"], shadow=False)

            if self.game_state == 0:
                draw_text(screen, "NEON TETRIS", 60, WIDTH//2, HEIGHT//2 - 50, theme["TERTIARY"], theme["SHADOW"])
                draw_text(screen, "Press SPACE to start", 30, WIDTH//2, HEIGHT//2 + 50, theme["TEXT"])
                draw_text(screen, "Press ESC to return to Hub", 20, 100, 20, theme["TEXT_MUTED"])
            elif self.game_state == 1:
                draw_text(screen, f"SCORE: {self.score}", 30, 100, 30, theme["TEXT"])
                draw_text(screen, f"HIGH: {high_score}", 30, WIDTH - 100, 30, theme["TEXT_MUTED"])
            elif self.game_state == 2:
                draw_panel(screen, 300, 240, theme["TERTIARY"])
                draw_text(screen, "GAME OVER", 50, WIDTH//2, HEIGHT//2 - 160, theme["TERTIARY"], theme["SHADOW"])
                draw_text(screen, "SCORE", 25, WIDTH//2, HEIGHT//2 - 80, theme["TEXT_MUTED"], shadow=False)
                draw_text(screen, str(self.score), 50, WIDTH//2, HEIGHT//2 - 40, theme["TEXT"])
                draw_text(screen, "BEST", 25, WIDTH//2, HEIGHT//2 + 10, theme["TEXT_MUTED"], shadow=False)
                draw_text(screen, str(high_score), 50, WIDTH//2, HEIGHT//2 + 50, theme["TEXT"])
                draw_text(screen, "Press SPACE to Restart", 20, WIDTH//2, HEIGHT//2 + 150, theme["TEXT"])
                draw_text(screen, "Press ESC to return to Hub", 20, WIDTH//2, HEIGHT//2 + 180, theme["TEXT_MUTED"])

            if getattr(self, 'flash_alpha', 0) > 0:
                flash_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                flash_surf.fill((255, 255, 255, int(self.flash_alpha)))
                screen.blit(flash_surf, (0, 0))
                self.flash_alpha = max(0, self.flash_alpha - 15)

            pygame.display.update()

# ==========================================
# MAIN HUB
# ==========================================

class Button:
    def __init__(self, x, y, width, height, text, color, subtext="", text_color=None, font_size=24):
        self.rect = pygame.Rect(x - width//2, y - height//2, width, height)
        self.shadow_rect = pygame.Rect(self.rect.x + 5, self.rect.y + 5, width, height)
        self.text = text
        self.subtext = subtext
        self.base_color = color
        self.text_color = text_color
        self.font_size = font_size
        self.is_hovered = False
        self.anim_offset = 0
        self.particles = []

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)

        if self.is_hovered and random.random() < 0.2:
            self.particles.append({'x': random.uniform(self.rect.left, self.rect.right), 'y': self.rect.bottom, 'vy': random.uniform(-2, -0.5), 'life': 20})


        hover_color = (min(self.base_color[0] + 50, 255), min(self.base_color[1] + 50, 255), min(self.base_color[2] + 50, 255))
        
        if self.is_hovered:
            self.anim_offset = max(self.anim_offset - 1, -3)
            current_color = hover_color
        else:
            self.anim_offset = min(self.anim_offset + 1, 0)
            current_color = self.base_color

        shadow = self.shadow_rect.copy()
        shadow.y += self.anim_offset if not self.is_hovered else 0
        pygame.draw.rect(surface, theme["SHADOW"], shadow, border_radius=20)
        
        active_rect = self.rect.copy()
        active_rect.y += self.anim_offset
        
        pygame.draw.rect(surface, current_color, active_rect, border_radius=20)
        
        # Sleek glow outline when hovered
        if self.is_hovered:
            pygame.draw.rect(surface, theme["TEXT"], active_rect, width=2, border_radius=20)
        
        txt_col = self.text_color if self.text_color else theme["BG_COLOR"]
        
        if self.subtext:
            draw_text(surface, self.text, self.font_size, active_rect.centerx, active_rect.centery - (self.font_size//2 - 2), txt_col, shadow=False)
            draw_text(surface, self.subtext, max(12, self.font_size//2), active_rect.centerx, active_rect.centery + (self.font_size//2 + 2), txt_col, shadow=False)
        else:
            draw_text(surface, self.text, self.font_size, active_rect.centerx, active_rect.centery, txt_col, shadow=False)
            
        for p in self.particles[:]:
            p['y'] += p['vy']
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)
            else:
                pygame.draw.circle(surface, self.base_color, (int(p['x']), int(p['y'])), 3)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class MenuParticle:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.uniform(1, 3)
        self.speed_y = random.uniform(-1, -0.2)
        self.alpha = random.randint(50, 200)

    def update(self):
        self.y += self.speed_y
        if self.y < 0:
            self.y = HEIGHT
            self.x = random.randint(0, WIDTH)

    def draw(self, surface):
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, self.alpha), (self.size, self.size), self.size)
        surface.blit(s, (self.x, self.y))

def draw_game_logo(surface, x, y, game_id, anim_timer, theme):
    pygame.draw.circle(surface, (20, 20, 30), (x, y), 35)
    pygame.draw.circle(surface, theme["SHADOW"], (x, y), 35, width=2)
    
    if game_id == "SNAKE":
        pygame.draw.rect(surface, theme["SNAKE_BODY"], (x-15, y-5, 10, 10))
        pygame.draw.rect(surface, theme["PRIMARY"], (x-5, y-5, 10, 10))
        pygame.draw.circle(surface, theme["FOOD"], (x+10, y), 4)
    elif game_id == "PONG":
        pygame.draw.rect(surface, theme["TERTIARY"], (x-15, y-15, 6, 30))
        pygame.draw.rect(surface, theme["SECONDARY"], (x+9, y-15, 6, 30))
        ball_y = y + math.sin(anim_timer * 2) * 10
        pygame.draw.circle(surface, theme["TEXT"], (x, int(ball_y)), 4)
    elif game_id == "TICTACTOE":
        pygame.draw.line(surface, theme["PRIMARY"], (x-5, y-15), (x-5, y+15), 2)
        pygame.draw.line(surface, theme["PRIMARY"], (x+5, y-15), (x+5, y+15), 2)
        pygame.draw.line(surface, theme["PRIMARY"], (x-15, y-5), (x+15, y-5), 2)
        pygame.draw.line(surface, theme["PRIMARY"], (x-15, y+5), (x+15, y+5), 2)
        pygame.draw.line(surface, theme["TERTIARY"], (x-12, y-12), (x-6, y-6), 2)
        pygame.draw.line(surface, theme["TERTIARY"], (x-12, y-6), (x-6, y-12), 2)
        pygame.draw.circle(surface, theme["SECONDARY"], (x+10, y+10), 4, 2)
    elif game_id == "FLAPPY":
        pygame.draw.circle(surface, (246, 215, 68), (x-5, int(y + math.sin(anim_timer*3)*5)), 8)
        pygame.draw.rect(surface, (115, 191, 46), (x+5, y-15, 10, 30))
    elif game_id == "BRICK":
        pygame.draw.rect(surface, theme["PRIMARY"], (x-15, y-15, 10, 6))
        pygame.draw.rect(surface, theme["SECONDARY"], (x-3, y-15, 10, 6))
        pygame.draw.rect(surface, theme["TERTIARY"], (x+9, y-15, 10, 6))
        pygame.draw.rect(surface, theme["TEXT"], (x-12, y+10, 24, 4))
        pygame.draw.circle(surface, theme["TEXT"], (x, y), 3)
    elif game_id == "SHOOTER":
        points = [(x, y-12), (x+10, y+10), (x-10, y+10)]
        pygame.draw.polygon(surface, theme["SECONDARY"], points)
        pygame.draw.line(surface, theme["TERTIARY"], (x, y-15), (x, y-25), 2)
    elif game_id == "TETRIS":
        pygame.draw.rect(surface, (0, 255, 255), (x-10, y-10, 8, 8))
        pygame.draw.rect(surface, (0, 255, 255), (x-2, y-10, 8, 8))
        pygame.draw.rect(surface, (0, 255, 255), (x-2, y-2, 8, 8))
        pygame.draw.rect(surface, (255, 165, 0), (x+6, y-2, 8, 8))
        pygame.draw.rect(surface, (255, 165, 0), (x+6, y+6, 8, 8))

class GameCard:
    def __init__(self, x, y, width, height, title, game_id, color, high_score):
        self.rect = pygame.Rect(x - width//2, y - height//2, width, height)
        self.shadow_rect = pygame.Rect(self.rect.x + 8, self.rect.y + 8, width, height)
        self.title = title
        self.game_id = game_id
        self.base_color = color
        self.high_score = high_score
        self.is_hovered = False
        self.anim_offset = 0
        self.play_btn = Button(x, y + height//2 - 20, 100, 30, "PLAY", color, font_size=16)
        self.play_btn.shadow_rect = pygame.Rect(self.play_btn.rect.x + 3, self.play_btn.rect.y + 3, 100, 30)

    def draw(self, surface, anim_timer):
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        if self.is_hovered:
            self.anim_offset = max(self.anim_offset - 1, -6)
        else:
            self.anim_offset = min(self.anim_offset + 1, 0)
            
        shadow = self.shadow_rect.copy()
        shadow.y += self.anim_offset if not self.is_hovered else 0
        
        # Glow shadow
        if self.is_hovered:
            glow = pygame.Surface((self.rect.width + 30, self.rect.height + 30), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*self.base_color, 40), glow.get_rect(), border_radius=20)
            surface.blit(glow, (self.rect.x - 15, self.rect.y + self.anim_offset - 15))

        pygame.draw.rect(surface, theme["SHADOW"], shadow, border_radius=15)
        
        active_rect = self.rect.copy()
        active_rect.y += self.anim_offset
        
        # Glassmorphism base
        glass = pygame.Surface((active_rect.width, active_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(glass, (*theme["PANEL"], 220), glass.get_rect(), border_radius=15)
        
        # Inner gradient
        gradient = pygame.Surface((active_rect.width, active_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(gradient, (*self.base_color, 30), gradient.get_rect(), border_radius=15)
        glass.blit(gradient, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        
        # Top highlight
        pygame.draw.line(glass, (255, 255, 255, 100), (10, 2), (active_rect.width - 10, 2), 2)
        
        surface.blit(glass, active_rect.topleft)
        
        if self.is_hovered:
            pygame.draw.rect(surface, self.base_color, active_rect, width=2, border_radius=15)
        else:
            pygame.draw.rect(surface, theme["SHADOW"], active_rect, width=2, border_radius=15)
            
        draw_game_logo(surface, active_rect.centerx, active_rect.y + 40, self.game_id, anim_timer, theme)
        draw_text(surface, self.title, 18, active_rect.centerx, active_rect.y + 85, theme["TEXT"], shadow=False)
        draw_text(surface, self.high_score, 12, active_rect.centerx, active_rect.y + 105, theme["TEXT_MUTED"], shadow=False)
        
        self.play_btn.rect.centerx = active_rect.centerx
        self.play_btn.rect.centery = active_rect.y + self.rect.height - 25
        self.play_btn.shadow_rect.x = self.play_btn.rect.x + 3
        self.play_btn.shadow_rect.y = self.play_btn.rect.y + 3
        self.play_btn.draw(surface)

    def is_clicked(self, event):
        return self.play_btn.is_clicked(event)

class SynthGrid:
    def __init__(self):
        self.scroll = 0
    def draw(self, surface, theme):
        self.scroll = (self.scroll + 1.5) % 40
        horizon_y = 200
        for i in range(-15, 16):
            x_bottom = WIDTH//2 + i * 80
            x_top = WIDTH//2 + i * 20
            pygame.draw.aaline(surface, theme["SHADOW"], (x_top, horizon_y), (x_bottom, HEIGHT))
        for i in range(15):
            offset = (i * 40 + self.scroll)
            y = horizon_y + (offset ** 2) / 800
            if y < HEIGHT:
                pygame.draw.aaline(surface, theme["SHADOW"], (0, y), (WIDTH, y))

def screen_transition(surface, theme):
    max_radius = int(math.hypot(WIDTH//2, HEIGHT//2)) + 10
    step = max_radius // 15
    for radius in range(0, max_radius, step):
        pygame.draw.circle(surface, theme["BG_COLOR"], (WIDTH//2, HEIGHT//2), radius)
        pygame.display.update()
        clock.tick(60)

def main_menu():
    global theme_name, theme
    
    synth_grid = SynthGrid()
    anim_timer = 0
    
    # Modern Game Card layout (7 Games)
    cards = []
    
    running = True
    while running:
        scores = load_data().get("high_scores", {})
        
        # Re-initialize cards every frame to easily handle score updates & theme changes
        # Width: 220, Height: 140
        cards = [
            GameCard(WIDTH//2 - 250, 220, 220, 140, "SNAKE", "SNAKE", theme["PRIMARY"], f"HIGH SCORE: {scores.get('Snake', 0)}"),
            GameCard(WIDTH//2, 220, 220, 140, "PONG", "PONG", theme["SECONDARY"], f"MOST WINS: {scores.get('Pong', 0)}"),
            GameCard(WIDTH//2 + 250, 220, 220, 140, "TIC-TAC-TOE", "TICTACTOE", theme["TERTIARY"], f"WINS: {scores.get('TicTacToe', 0)}"),
            GameCard(WIDTH//2 - 250, 375, 220, 140, "FLAPPY BIRD", "FLAPPY", (246, 215, 68), f"HIGH SCORE: {scores.get('Flappy', 0)}"),
            GameCard(WIDTH//2, 375, 220, 140, "BRICK BREAKER", "BRICK", theme["PRIMARY"], f"HIGH SCORE: {scores.get('BrickBreaker', 0)}"),
            GameCard(WIDTH//2 + 250, 375, 220, 140, "SPACE SHOOTER", "SHOOTER", theme["SECONDARY"], f"HIGH SCORE: {scores.get('SpaceShooter', 0)}"),
            GameCard(WIDTH//2, 530, 220, 140, "NEON TETRIS", "TETRIS", theme["TERTIARY"], f"HIGH SCORE: {scores.get('Tetris', 0)}")
        ]

        clock.tick(FPS)
        anim_timer += 0.05
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            game_to_launch = None
            if cards[0].is_clicked(event): game_to_launch = SnakeGame()
            elif cards[1].is_clicked(event): game_to_launch = PongGame()
            elif cards[2].is_clicked(event): game_to_launch = TicTacToeGame()
            elif cards[3].is_clicked(event): game_to_launch = FlappyGame()
            elif cards[4].is_clicked(event): game_to_launch = BrickBreakerGame()
            elif cards[5].is_clicked(event): game_to_launch = SpaceShooterGame()
            elif cards[6].is_clicked(event): game_to_launch = TetrisGame()
                
            if game_to_launch:
                screen_transition(screen, theme)
                game_to_launch.run()
                screen_transition(screen, theme)

        screen.fill(theme["BG_COLOR"])
        
        synth_grid.draw(screen, theme)
            
        title_y = 65 + math.sin(anim_timer) * 6
        glow_size = int(abs(math.sin(anim_timer * 2)) * 5)
        draw_text(screen, "A R C A D E // H U B", 45, WIDTH//2 - glow_size, title_y, theme["TEXT"], theme["PRIMARY"])
        draw_text(screen, "A R C A D E // H U B", 45, WIDTH//2 + glow_size, title_y, theme["TEXT"], theme["SECONDARY"])
        draw_text(screen, "A R C A D E // H U B", 45, WIDTH//2, title_y, theme["TEXT"], theme["SHADOW"])
        draw_text(screen, "select your vibe", 14, WIDTH//2, title_y + 35, theme["TEXT_MUTED"], shadow=False)
        
        for card in cards:
            card.draw(screen, anim_timer)

        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_menu()
