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
        wins = data.get_high_score("TicTacToe")
        
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
                            sound_click.play()
                            self.turn = "O" if self.turn == "X" else "X"
                            self.winner = self.check_winner()
                            if self.winner:
                                if self.winner == "Draw":
                                    sound_hit.play()
                                else:
                                    sound_score.play()
                                    wins += 1
                                    data.set_high_score("TicTacToe", wins)

            screen.fill(data.theme["BG_COLOR"])
            
            # Draw subtle grid glow in background
            glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*data.theme["PANEL"][:3], 30), (WIDTH//2, HEIGHT//2), 300)
            screen.blit(glow_surf, (0, 0))
            
            mx, my = pygame.mouse.get_pos()
            for row in range(3):
                for col in range(3):
                    cx = self.offset_x + col * self.cell_size
                    cy = self.offset_y + row * self.cell_size
                    if cx < mx < cx + self.cell_size and cy < my < cy + self.cell_size and not self.winner and self.board[row][col] == "":
                        s = pygame.Surface((self.cell_size-10, self.cell_size-10), pygame.SRCALPHA)
                        pygame.draw.rect(s, (*data.theme["TEXT"][:3], 30), s.get_rect(), border_radius=15)
                        screen.blit(s, (cx+5, cy+5))

            glow_offset = math.sin(self.anim_timer) * 3
            grid_color = data.theme["PANEL"]
            for i in range(1, 3):
                pygame.draw.line(screen, grid_color, (self.offset_x + i * self.cell_size, self.offset_y), 
                                                (self.offset_x + i * self.cell_size, self.offset_y + 3 * self.cell_size), 10)
                pygame.draw.line(screen, data.theme["TEXT"], (self.offset_x + i * self.cell_size, self.offset_y), 
                                                (self.offset_x + i * self.cell_size, self.offset_y + 3 * self.cell_size), 4)
                pygame.draw.line(screen, grid_color, (self.offset_x, self.offset_y + i * self.cell_size), 
                                                (self.offset_x + 3 * self.cell_size, self.offset_y + i * self.cell_size), 10)
                pygame.draw.line(screen, data.theme["TEXT"], (self.offset_x, self.offset_y + i * self.cell_size), 
                                                (self.offset_x + 3 * self.cell_size, self.offset_y + i * self.cell_size), 4)

            for row in range(3):
                for col in range(3):
                    val = self.board[row][col]
                    cx = self.offset_x + col * self.cell_size + self.cell_size // 2
                    cy = self.offset_y + row * self.cell_size + self.cell_size // 2
                    scale = self.pieces_scale.get((row, col), 1.0)
                    if val == "X":
                        size = int((120 + glow_offset) * scale)
                        if size > 0: draw_tictactoe_piece(screen, "X", cx, cy, size, data.theme["SECONDARY"])
                    elif val == "O":
                        size = int((120 - glow_offset) * scale)
                        if size > 0: draw_tictactoe_piece(screen, "O", cx, cy, size, data.theme["TERTIARY"])

            draw_text(screen, "Press ESC to exit", 20, 80, 20, data.theme["TEXT_MUTED"])
            draw_text(screen, f"Total Wins: {wins}", 20, WIDTH - 80, 20, data.theme["TEXT_MUTED"])

            if self.winner:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                screen.blit(overlay, (0, 0))
                
                panel_color = data.theme["PRIMARY"] if self.winner == "Draw" else (data.theme["SECONDARY"] if self.winner == "X" else data.theme["TERTIARY"])
                
                draw_panel(screen, 400, 240, panel_color)
                
                text = "DRAW!" if self.winner == "Draw" else f"{self.winner} WINS!"
                draw_text(screen, text, 80, WIDTH//2, HEIGHT//2 - 30, panel_color)
                draw_text(screen, "Press SPACE to restart", 25, WIDTH//2, HEIGHT//2 + 50, data.theme["TEXT"])
            else:
                current_color = data.theme["SECONDARY"] if self.turn == "X" else data.theme["TERTIARY"]
                draw_text(screen, f"{self.turn}'s Turn", 30, WIDTH//2, 30, current_color)

            pygame.display.update()

