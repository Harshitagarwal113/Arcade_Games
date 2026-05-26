import pygame
import sys
import math
import random
from core.config import WIDTH, HEIGHT, FPS
import core.data as data
from core.display import screen, clock
from core.utils import draw_text, draw_panel
from core.sounds import *
from graphics.drawing import *
from games.snake import SnakeGame
from games.pong import PongGame
from games.tictactoe import TicTacToeGame
from games.brick_breaker import BrickBreakerGame
from games.flappy import FlappyGame
from games.space_shooter import SpaceShooterGame
from games.tetris import TetrisGame
from games.twenty_forty_eight import TwentyFortyEightGame
from games.frogger import FroggerGame



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
        pygame.draw.rect(surface, data.theme["SHADOW"], shadow, border_radius=20)
        
        active_rect = self.rect.copy()
        active_rect.y += self.anim_offset
        
        pygame.draw.rect(surface, current_color, active_rect, border_radius=20)
        
        # Sleek glow outline when hovered
        if self.is_hovered:
            pygame.draw.rect(surface, data.theme["TEXT"], active_rect, width=2, border_radius=20)
        
        txt_col = self.text_color if self.text_color else data.theme["BG_COLOR"]
        
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
    pygame.draw.circle(surface, data.theme["SHADOW"], (x, y), 35, width=2)
    
    if game_id == "SNAKE":
        pygame.draw.rect(surface, data.theme["SNAKE_BODY"], (x-15, y-5, 10, 10))
        pygame.draw.rect(surface, data.theme["PRIMARY"], (x-5, y-5, 10, 10))
        pygame.draw.circle(surface, data.theme["FOOD"], (x+10, y), 4)
    elif game_id == "PONG":
        pygame.draw.rect(surface, data.theme["TERTIARY"], (x-15, y-15, 6, 30))
        pygame.draw.rect(surface, data.theme["SECONDARY"], (x+9, y-15, 6, 30))
        ball_y = y + math.sin(anim_timer * 2) * 10
        pygame.draw.circle(surface, data.theme["TEXT"], (x, int(ball_y)), 4)
    elif game_id == "TICTACTOE":
        pygame.draw.line(surface, data.theme["PRIMARY"], (x-5, y-15), (x-5, y+15), 2)
        pygame.draw.line(surface, data.theme["PRIMARY"], (x+5, y-15), (x+5, y+15), 2)
        pygame.draw.line(surface, data.theme["PRIMARY"], (x-15, y-5), (x+15, y-5), 2)
        pygame.draw.line(surface, data.theme["PRIMARY"], (x-15, y+5), (x+15, y+5), 2)
        pygame.draw.line(surface, data.theme["TERTIARY"], (x-12, y-12), (x-6, y-6), 2)
        pygame.draw.line(surface, data.theme["TERTIARY"], (x-12, y-6), (x-6, y-12), 2)
        pygame.draw.circle(surface, data.theme["SECONDARY"], (x+10, y+10), 4, 2)
    elif game_id == "FLAPPY":
        pygame.draw.circle(surface, (246, 215, 68), (x-5, int(y + math.sin(anim_timer*3)*5)), 8)
        pygame.draw.rect(surface, (115, 191, 46), (x+5, y-15, 10, 30))
    elif game_id == "BRICK":
        pygame.draw.rect(surface, data.theme["PRIMARY"], (x-15, y-15, 10, 6))
        pygame.draw.rect(surface, data.theme["SECONDARY"], (x-3, y-15, 10, 6))
        pygame.draw.rect(surface, data.theme["TERTIARY"], (x+9, y-15, 10, 6))
        pygame.draw.rect(surface, data.theme["TEXT"], (x-12, y+10, 24, 4))
        pygame.draw.circle(surface, data.theme["TEXT"], (x, y), 3)
    elif game_id == "SHOOTER":
        points = [(x, y-12), (x+10, y+10), (x-10, y+10)]
        pygame.draw.polygon(surface, data.theme["SECONDARY"], points)
        pygame.draw.line(surface, data.theme["TERTIARY"], (x, y-15), (x, y-25), 2)
    elif game_id == "TETRIS":
        pygame.draw.rect(surface, (0, 255, 255), (x-10, y-10, 8, 8))
        pygame.draw.rect(surface, (0, 255, 255), (x-2, y-10, 8, 8))
        pygame.draw.rect(surface, (0, 255, 255), (x-2, y-2, 8, 8))
        pygame.draw.rect(surface, (255, 165, 0), (x+6, y-2, 8, 8))
        pygame.draw.rect(surface, (255, 165, 0), (x+6, y+6, 8, 8))
    elif game_id == "2048":
        pygame.draw.rect(surface, data.theme["TERTIARY"], (x-12, y-12, 11, 11), border_radius=2)
        pygame.draw.rect(surface, data.theme["SECONDARY"], (x+1, y-12, 11, 11), border_radius=2)
        pygame.draw.rect(surface, data.theme["PRIMARY"], (x-12, y+1, 11, 11), border_radius=2)
        pygame.draw.rect(surface, (255, 165, 0), (x+1, y+1, 11, 11), border_radius=2)
    elif game_id == "FROGGER":
        pygame.draw.circle(surface, (50, 200, 50), (x, y+5), 8)
        pygame.draw.rect(surface, data.theme["PRIMARY"], (x-15, y-10, 30, 6))

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

        pygame.draw.rect(surface, data.theme["SHADOW"], shadow, border_radius=15)
        
        active_rect = self.rect.copy()
        active_rect.y += self.anim_offset
        
        # Glassmorphism base
        glass = pygame.Surface((active_rect.width, active_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(glass, (*data.theme["PANEL"], 220), glass.get_rect(), border_radius=15)
        
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
            pygame.draw.rect(surface, data.theme["SHADOW"], active_rect, width=2, border_radius=15)
            
        draw_game_logo(surface, active_rect.centerx, active_rect.y + 40, self.game_id, anim_timer, data.theme)
        draw_text(surface, self.title, 18, active_rect.centerx, active_rect.y + 85, data.theme["TEXT"], shadow=False)
        draw_text(surface, self.high_score, 12, active_rect.centerx, active_rect.y + 105, data.theme["TEXT_MUTED"], shadow=False)
        
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
            pygame.draw.aaline(surface, data.theme["SHADOW"], (x_top, horizon_y), (x_bottom, HEIGHT))
        for i in range(15):
            offset = (i * 40 + self.scroll)
            y = horizon_y + (offset ** 2) / 800
            if y < HEIGHT:
                pygame.draw.aaline(surface, data.theme["SHADOW"], (0, y), (WIDTH, y))

def screen_transition(surface, theme):
    max_radius = int(math.hypot(WIDTH//2, HEIGHT//2)) + 10
    step = max_radius // 15
    for radius in range(0, max_radius, step):
        pygame.draw.circle(surface, data.theme["BG_COLOR"], (WIDTH//2, HEIGHT//2), radius)
        pygame.display.update()
        clock.tick(60)

def main_menu():
    
    
    synth_grid = SynthGrid()
    anim_timer = 0
    
    # Modern Game Card layout (7 Games)
    cards = []
    
    running = True
    while running:
        scores = data.load_data().get("high_scores", {})
        
        # Re-initialize cards every frame to easily handle score updates & theme changes
        # Width: 220, Height: 140
        cards = [
            GameCard(WIDTH//2 - 250, 220, 220, 140, "SNAKE", "SNAKE", data.theme["PRIMARY"], f"HIGH SCORE: {scores.get('Snake', 0)}"),
            GameCard(WIDTH//2, 220, 220, 140, "PONG", "PONG", data.theme["SECONDARY"], f"MOST WINS: {scores.get('Pong', 0)}"),
            GameCard(WIDTH//2 + 250, 220, 220, 140, "TIC-TAC-TOE", "TICTACTOE", data.theme["TERTIARY"], f"WINS: {scores.get('TicTacToe', 0)}"),
            GameCard(WIDTH//2 - 250, 375, 220, 140, "FLAPPY BIRD", "FLAPPY", (246, 215, 68), f"HIGH SCORE: {scores.get('Flappy', 0)}"),
            GameCard(WIDTH//2, 375, 220, 140, "BRICK BREAKER", "BRICK", data.theme["PRIMARY"], f"HIGH SCORE: {scores.get('BrickBreaker', 0)}"),
            GameCard(WIDTH//2 + 250, 375, 220, 140, "SPACE SHOOTER", "SHOOTER", data.theme["SECONDARY"], f"HIGH SCORE: {scores.get('SpaceShooter', 0)}"),
            GameCard(WIDTH//2 - 250, 530, 220, 140, "NEON TETRIS", "TETRIS", data.theme["TERTIARY"], f"HIGH SCORE: {scores.get('Tetris', 0)}"),
            GameCard(WIDTH//2, 530, 220, 140, "2048 PUZZLE", "2048", data.theme["PRIMARY"], f"HIGH SCORE: {scores.get('2048', 0)}"),
            GameCard(WIDTH//2 + 250, 530, 220, 140, "NEON FROGGER", "FROGGER", (50, 200, 50), f"HIGH SCORE: {scores.get('Frogger', 0)}")
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
            elif cards[7].is_clicked(event): game_to_launch = TwentyFortyEightGame()
            elif cards[8].is_clicked(event): game_to_launch = FroggerGame()
                
            if game_to_launch:
                sound_click.play()
                screen_transition(screen, data.theme)
                game_to_launch.run()
                screen_transition(screen, data.theme)

        screen.fill(data.theme["BG_COLOR"])
        
        synth_grid.draw(screen, data.theme)
            
        title_y = 65 + math.sin(anim_timer) * 6
        glow_size = int(abs(math.sin(anim_timer * 2)) * 5)
        draw_text(screen, "A R C A D E // H U B", 45, WIDTH//2 - glow_size, title_y, data.theme["TEXT"], data.theme["PRIMARY"])
        draw_text(screen, "A R C A D E // H U B", 45, WIDTH//2 + glow_size, title_y, data.theme["TEXT"], data.theme["SECONDARY"])
        draw_text(screen, "A R C A D E // H U B", 45, WIDTH//2, title_y, data.theme["TEXT"], data.theme["SHADOW"])
        draw_text(screen, "select your vibe", 14, WIDTH//2, title_y + 35, data.theme["TEXT_MUTED"], shadow=False)
        
        for card in cards:
            card.draw(screen, anim_timer)

        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_menu()
