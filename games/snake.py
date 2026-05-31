import pygame
import asyncio
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

    async def run(self):
        running = True
        pulse_anim = 0
        high_score = data.get_high_score("Snake")
        
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
                            high_score = data.get_high_score("Snake")

            if not self.game_over:
                if time.time() - self.last_move > self.move_delay:
                    head_x, head_y = self.snake[0]
                    new_head = (head_x + self.dir[0], head_y + self.dir[1])

                    if (new_head[0] < 0 or new_head[0] >= WIDTH or 
                        new_head[1] < 0 or new_head[1] >= HEIGHT or 
                        new_head in self.snake):
                        self.game_over = True
                        sound_explosion.play()
                        data.set_high_score("Snake", self.score)
                    else:
                        self.snake.insert(0, new_head)
                        if new_head == self.food:
                            sound_eat.play()
                            self.score += 10
                            self.move_delay = max(0.04, self.move_delay - 0.005)
                            self.shake_timer = 10
                            self.floating_texts.append({'x': self.food[0], 'y': self.food[1], 'alpha': 255})
                            self.particles.append({'x': self.food[0]+12, 'y': self.food[1]+12, 'vx': 0, 'vy': 0, 'life': 20, 'radius': 5, 'color': data.theme["PRIMARY"], 'is_ring': True})
                            for _ in range(15):
                                self.particles.append({
                                    'x': self.food[0]+12, 'y': self.food[1]+12, 
                                    'vx': random.uniform(-6, 6), 'vy': random.uniform(-6, 6),
                                    'life': 30, 'radius': random.uniform(3, 8), 'color': data.theme["FOOD"]
                                })
                            self.food = self.spawn_food()
                        else:
                            tail = self.snake.pop()
                            self.particles.append({
                                'x': tail[0]+12, 'y': tail[1]+12,
                                'vx': 0, 'vy': 0, 'life': 15, 'radius': 8, 'color': data.theme["SNAKE_BODY"]
                            })
                    self.last_dir = self.dir
                    self.last_move = time.time()

            screen.fill(data.theme["BG_COLOR"])
            grid_color = (min(255, data.theme["BG_COLOR"][0] + 15), min(255, data.theme["BG_COLOR"][1] + 15), min(255, data.theme["BG_COLOR"][2] + 15))
            offset = int(pulse_anim * 15) % self.grid_size
            for x in range(offset - self.grid_size, WIDTH, self.grid_size):
                pygame.draw.line(screen, grid_color, (x, 0), (x, HEIGHT))
            for y in range(offset - self.grid_size, HEIGHT, self.grid_size):
                pygame.draw.line(screen, grid_color, (0, y), (WIDTH, y))

            food_glow = int(abs(math.sin(pulse_anim * 2)) * 8)
            pygame.draw.rect(screen, data.theme["PRIMARY"], (self.food[0] - food_glow, self.food[1] - food_glow, self.grid_size + food_glow*2, self.grid_size + food_glow*2), border_radius=5)
            draw_apple(screen, self.food[0], self.food[1], self.grid_size)
            
            tongue_out = (math.sin(pulse_anim * 3) > 0.5)
            for i, segment in enumerate(self.snake):
                pulse_scale = math.sin(pulse_anim * 2 - i * 0.5) * 2
                size_mod = int(pulse_scale) if self.move_delay < 0.14 else 0
                if i == 0:
                    draw_snake_head(screen, segment[0]-size_mod, segment[1]-size_mod, self.grid_size+size_mod*2, self.dir[0], self.dir[1], tongue_out, data.theme)
                else:
                    color = data.theme["SNAKE_BODY"]
                    pygame.draw.rect(screen, color, (segment[0]+1-size_mod, segment[1]+1-size_mod, self.grid_size-2+size_mod*2, self.grid_size-2+size_mod*2), border_radius=4)
                    pygame.draw.line(screen, data.theme["SHADOW"], (segment[0]+4, segment[1]+self.grid_size//2), (segment[0]+self.grid_size-4, segment[1]+self.grid_size//2), 2)

            for p in self.particles:
                if p.get('is_ring'):
                    pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), int(p['radius']), max(1, 6 - int(p['radius']/10)))
                else:
                    pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), int(max(1, p['radius'])))
            for t in self.floating_texts:
                draw_text(screen, "+10", 20, t['x'], int(t['y']), data.theme["PRIMARY"], shadow=False)

            draw_text(screen, f"SCORE: {self.score}", 40, WIDTH//2, 40, data.theme["PRIMARY"])
            draw_text(screen, f"HIGH SCORE: {max(self.score, high_score)}", 20, WIDTH//2, 80, data.theme["TEXT_MUTED"])
            draw_text(screen, "Press ESC to exit", 20, 80, 20, data.theme["TEXT_MUTED"], shadow=False)

            if self.game_over:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                screen.blit(overlay, (0, 0))
                
                draw_panel(screen, 400, 240, data.theme["SECONDARY"])
                
                draw_text(screen, "GAME OVER", 60, WIDTH//2, HEIGHT//2 - 40, data.theme["SECONDARY"])
                draw_text(screen, f"Final Score: {self.score}", 30, WIDTH//2, HEIGHT//2 + 20, data.theme["TEXT"])
                draw_text(screen, "Press SPACE to restart", 20, WIDTH//2, HEIGHT//2 + 70, data.theme["TEXT_MUTED"])

            if self.shake_timer > 0:
                shake_x = random.randint(-4, 4)
                shake_y = random.randint(-4, 4)
                shook_surface = screen.copy()
                screen.fill(data.theme["BG_COLOR"])
                screen.blit(shook_surface, (shake_x, shake_y))

            pygame.display.update()
            await asyncio.sleep(0)

