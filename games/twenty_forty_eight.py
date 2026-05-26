import pygame
import sys
import random
import math
from core.config import WIDTH, HEIGHT, FPS
import core.data as data
from core.display import screen, clock
from core.utils import draw_text, draw_panel
from core.sounds import *
from graphics.drawing import *

class TwentyFortyEightGame:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.grid = [[0]*4 for _ in range(4)]
        self.score = 0
        self.game_over = False
        self.add_new_tile()
        self.add_new_tile()

    def add_new_tile(self):
        empty_cells = [(r, c) for r in range(4) for c in range(4) if self.grid[r][c] == 0]
        if empty_cells:
            r, c = random.choice(empty_cells)
            self.grid[r][c] = 2 if random.random() < 0.9 else 4

    def compress(self, mat):
        changed = False
        new_mat = [[0]*4 for _ in range(4)]
        for i in range(4):
            pos = 0
            for j in range(4):
                if mat[i][j] != 0:
                    new_mat[i][pos] = mat[i][j]
                    if j != pos:
                        changed = True
                    pos += 1
        return new_mat, changed

    def merge(self, mat):
        changed = False
        for i in range(4):
            for j in range(3):
                if mat[i][j] == mat[i][j + 1] and mat[i][j] != 0:
                    mat[i][j] = mat[i][j] * 2
                    mat[i][j + 1] = 0
                    self.score += mat[i][j]
                    changed = True
                    sound_score.play()
        return mat, changed

    def reverse(self, mat):
        new_mat = []
        for i in range(4):
            new_mat.append(list(reversed(mat[i])))
        return new_mat

    def transpose(self, mat):
        new_mat = [[0]*4 for _ in range(4)]
        for i in range(4):
            for j in range(4):
                new_mat[i][j] = mat[j][i]
        return new_mat

    def move_left(self):
        mat, changed1 = self.compress(self.grid)
        mat, changed2 = self.merge(mat)
        changed = changed1 or changed2
        mat, temp = self.compress(mat)
        self.grid = mat
        return changed

    def move_right(self):
        mat = self.reverse(self.grid)
        mat, changed1 = self.compress(mat)
        mat, changed2 = self.merge(mat)
        changed = changed1 or changed2
        mat, temp = self.compress(mat)
        self.grid = self.reverse(mat)
        return changed

    def move_up(self):
        mat = self.transpose(self.grid)
        mat, changed1 = self.compress(mat)
        mat, changed2 = self.merge(mat)
        changed = changed1 or changed2
        mat, temp = self.compress(mat)
        self.grid = self.transpose(mat)
        return changed

    def move_down(self):
        mat = self.transpose(self.grid)
        mat = self.reverse(mat)
        mat, changed1 = self.compress(mat)
        mat, changed2 = self.merge(mat)
        changed = changed1 or changed2
        mat, temp = self.compress(mat)
        mat = self.reverse(mat)
        self.grid = self.transpose(mat)
        return changed

    def get_current_state(self):
        for i in range(4):
            for j in range(4):
                if self.grid[i][j] == 2048:
                    return 'WON'
        for i in range(4):
            for j in range(4):
                if self.grid[i][j] == 0:
                    return 'GAME NOT OVER'
        for i in range(3):
            for j in range(3):
                if self.grid[i][j] == self.grid[i + 1][j] or self.grid[i][j] == self.grid[i][j + 1]:
                    return 'GAME NOT OVER'
        for j in range(3):
            if self.grid[3][j] == self.grid[3][j + 1]:
                return 'GAME NOT OVER'
        for i in range(3):
            if self.grid[i][3] == self.grid[i + 1][3]:
                return 'GAME NOT OVER'
        return 'LOST'

    def run(self):
        running = True
        high_score = data.get_high_score("2048")
        
        while running:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    if self.game_over:
                        if event.key == pygame.K_SPACE:
                            self.reset()
                        continue
                        
                    changed = False
                    if event.key == pygame.K_LEFT:
                        changed = self.move_left()
                    elif event.key == pygame.K_RIGHT:
                        changed = self.move_right()
                    elif event.key == pygame.K_UP:
                        changed = self.move_up()
                    elif event.key == pygame.K_DOWN:
                        changed = self.move_down()

                    if changed:
                        sound_hit.play()
                        self.add_new_tile()
                        state = self.get_current_state()
                        if state != 'GAME NOT OVER':
                            self.game_over = True
                            if state == 'LOST':
                                sound_explosion.play()
                            if self.score > high_score:
                                data.set_high_score("2048", self.score)
                                high_score = self.score

            screen.fill(data.theme["BG_COLOR"])
            draw_text(screen, f"SCORE: {self.score}", 30, 100, 20, data.theme["TEXT"])
            draw_text(screen, f"HIGH: {max(self.score, high_score)}", 30, WIDTH - 100, 20, data.theme["TEXT_MUTED"])
            draw_text(screen, "Press ESC to exit", 20, 80, HEIGHT - 20, data.theme["TEXT_MUTED"], shadow=False)

            # Draw grid
            cell_size = 100
            padding = 10
            grid_size = cell_size * 4 + padding * 5
            start_x = WIDTH // 2 - grid_size // 2
            start_y = HEIGHT // 2 - grid_size // 2

            pygame.draw.rect(screen, data.theme["SHADOW"], (start_x, start_y, grid_size, grid_size), border_radius=10)

            for i in range(4):
                for j in range(4):
                    val = self.grid[i][j]
                    x = start_x + padding + j * (cell_size + padding)
                    y = start_y + padding + i * (cell_size + padding)
                    
                    bg_color = data.theme["PANEL"]
                    text_color = data.theme["TEXT"]
                    
                    if val > 0:
                        colors = [
                            data.theme["PRIMARY"],
                            data.theme["SECONDARY"],
                            data.theme["TERTIARY"],
                            (255, 165, 0),
                            (255, 69, 0),
                            (255, 0, 0),
                            (255, 215, 0),
                            (0, 255, 255),
                            (255, 0, 255),
                            (0, 255, 0),
                            (0, 0, 255)
                        ]
                        bg_color = colors[int(math.log2(val)) % len(colors)]
                        if sum(bg_color) > 500:
                            text_color = (0,0,0)
                        else:
                            text_color = (255,255,255)
                            
                    pygame.draw.rect(screen, bg_color, (x, y, cell_size, cell_size), border_radius=5)
                    if val > 0:
                        draw_text(screen, str(val), 36, x + cell_size//2, y + cell_size//2, text_color, shadow=False)

            if self.game_over:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                screen.blit(overlay, (0, 0))
                
                draw_panel(screen, 400, 200, data.theme["PRIMARY"])
                
                msg = "YOU WON!" if self.get_current_state() == 'WON' else "GAME OVER"
                draw_text(screen, msg, 60, WIDTH//2, HEIGHT//2 - 30, data.theme["PRIMARY"])
                draw_text(screen, "Press SPACE to restart", 20, WIDTH//2, HEIGHT//2 + 40, data.theme["TEXT_MUTED"])

            pygame.display.update()
