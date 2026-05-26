import pygame
import sys
import math
import random
import time
from core.config import WIDTH, HEIGHT, FPS
import core.data as data
from core.display import screen, clock
from core.utils import draw_text, draw_panel
from core.sounds import *
from graphics.drawing import *


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
        sound_hit.play()
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
            sound_score.play()
            pts = [0, 100, 300, 500, 800][lines_cleared]
            self.score += pts
            self.drop_speed = max(5, 30 - self.score // 500)
            self.floating_texts.append({'x': WIDTH//2, 'y': HEIGHT//2, 'text': f"+{pts}", 'alpha': 255})
            self.flash_alpha = 255

    def run(self):
        running = True
        high_score = data.get_high_score("Tetris")
        
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
                                data.set_high_score("Tetris", self.score)
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
                            data.set_high_score("Tetris", self.score)

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
                draw_text(screen, t['text'], 30, int(t['x']), int(t['y']), data.theme["SECONDARY"], shadow=False)

            if self.game_state == 0:
                draw_text(screen, "NEON TETRIS", 60, WIDTH//2, HEIGHT//2 - 50, data.theme["TERTIARY"], data.theme["SHADOW"])
                draw_text(screen, "Press SPACE to start", 30, WIDTH//2, HEIGHT//2 + 50, data.theme["TEXT"])
                draw_text(screen, "Press ESC to return to Hub", 20, 100, 20, data.theme["TEXT_MUTED"])
            elif self.game_state == 1:
                draw_text(screen, f"SCORE: {self.score}", 30, 100, 30, data.theme["TEXT"])
                draw_text(screen, f"HIGH: {high_score}", 30, WIDTH - 100, 30, data.theme["TEXT_MUTED"])
            elif self.game_state == 2:
                draw_panel(screen, 300, 240, data.theme["TERTIARY"])
                draw_text(screen, "GAME OVER", 50, WIDTH//2, HEIGHT//2 - 160, data.theme["TERTIARY"], data.theme["SHADOW"])
                draw_text(screen, "SCORE", 25, WIDTH//2, HEIGHT//2 - 80, data.theme["TEXT_MUTED"], shadow=False)
                draw_text(screen, str(self.score), 50, WIDTH//2, HEIGHT//2 - 40, data.theme["TEXT"])
                draw_text(screen, "BEST", 25, WIDTH//2, HEIGHT//2 + 10, data.theme["TEXT_MUTED"], shadow=False)
                draw_text(screen, str(high_score), 50, WIDTH//2, HEIGHT//2 + 50, data.theme["TEXT"])
                draw_text(screen, "Press SPACE to Restart", 20, WIDTH//2, HEIGHT//2 + 150, data.theme["TEXT"])
                draw_text(screen, "Press ESC to return to Hub", 20, WIDTH//2, HEIGHT//2 + 180, data.theme["TEXT_MUTED"])

            if getattr(self, 'flash_alpha', 0) > 0:
                flash_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                flash_surf.fill((255, 255, 255, int(self.flash_alpha)))
                screen.blit(flash_surf, (0, 0))
                self.flash_alpha = max(0, self.flash_alpha - 15)

            pygame.display.update()

