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
                color = data.theme["PRIMARY"] if r < 2 else (data.theme["SECONDARY"] if r < 4 else data.theme["TERTIARY"])
                self.bricks.append({"rect": pygame.Rect(c * b_width + 2, r * b_height + 50 + 2, b_width - 4, b_height - 4), "color": color})
                
        self.score = 0
        self.game_over = False
        self.won = False
        self.particles = []
        self.floating_texts = []
        self.ball_trail = []
        self.combo = 0

    async def run(self):
        running = True
        high_score = data.get_high_score("BrickBreaker")
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
                    self.particles.append({'x': self.paddle.right - 10, 'y': self.paddle.bottom, 'vx': random.uniform(1, 3), 'vy': random.uniform(1, 3), 'life': 15, 'color': data.theme["TERTIARY"]})
                if keys[pygame.K_RIGHT] and self.paddle.right < WIDTH:
                    self.paddle.x += 8
                    self.particles.append({'x': self.paddle.left + 10, 'y': self.paddle.bottom, 'vx': random.uniform(-3, -1), 'vy': random.uniform(1, 3), 'life': 15, 'color': data.theme["TERTIARY"]})
                
                if random.random() < 0.3:
                    self.particles.append({'x': self.paddle.centerx + random.uniform(-20, 20), 'y': self.paddle.bottom, 'vx': random.uniform(-1, 1), 'vy': random.uniform(1, 3), 'life': 10, 'color': data.theme["SECONDARY"]})
                    
                self.ball.x += self.ball_vel[0]
                self.ball.y += self.ball_vel[1]
                
                self.ball_trail.append(self.ball.copy())
                if len(self.ball_trail) > 10:
                    self.ball_trail.pop(0)
                
                if self.ball.left <= 0 or self.ball.right >= WIDTH:
                    self.ball_vel[0] *= -1
                    sound_hit.play()
                if self.ball.top <= 0:
                    self.ball_vel[1] *= -1
                    sound_hit.play()
                    
                if self.ball.bottom >= HEIGHT:
                    self.game_over = True
                    sound_explosion.play()
                    if self.score > high_score:
                        data.set_high_score("BrickBreaker", self.score)
                        
                if self.ball.colliderect(self.paddle) and self.ball_vel[1] > 0:
                    sound_hit.play()
                    offset = (self.ball.centerx - self.paddle.centerx) / (self.paddle.width / 2)
                    speed = max(3.5, min(12.0, math.hypot(self.ball_vel[0], self.ball_vel[1])))
                    self.ball_vel[0] = offset * speed * 0.8
                    self.ball_vel[1] = -math.sqrt(abs(speed**2 - self.ball_vel[0]**2))
                    self.combo = 0
                    
                hit_index = self.ball.collidelist([b["rect"] for b in self.bricks])
                if hit_index != -1:
                    brick = self.bricks.pop(hit_index)
                    sound_hit.play()
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
                        sound_score.play()
                        if self.score > high_score:
                            data.set_high_score("BrickBreaker", self.score)

            screen.fill(data.theme["BG_COLOR"])
            for x in range(0, WIDTH, 40):
                pygame.draw.line(screen, (*data.theme["SHADOW"][:3], 100), (x, 0), (x, HEIGHT))
            for y in range(0, HEIGHT+40, 40):
                pygame.draw.line(screen, (*data.theme["SHADOW"][:3], 100), (0, y - 40 + bg_y), (WIDTH, y - 40 + bg_y))
            
            for b in self.bricks:
                draw_brick_face(screen, b["rect"], self.ball.y, data.theme, b["color"])
                
            draw_spaceship_paddle(screen, self.paddle, data.theme, False)
            for tr in self.ball_trail:
                tr_surf = pygame.Surface((16, 16), pygame.SRCALPHA)
                pygame.draw.ellipse(tr_surf, (*data.theme["TEXT"], 50), (0,0,16,16))
                screen.blit(tr_surf, (tr.x, tr.y))
                
            draw_energy_ball(screen, self.ball, data.theme)
            
            for p in self.particles:
                pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), 4)
            for t in self.floating_texts:
                draw_text(screen, t['text'], 20, t['x'], int(t['y']), data.theme["TEXT"], shadow=False)
                
            if self.combo > 1:
                draw_text(screen, f"{self.combo}x COMBO!", 30, WIDTH//2, HEIGHT//2, data.theme["TERTIARY"])
            
            draw_text(screen, f"SCORE: {self.score}", 30, 100, 20, data.theme["TEXT"])
            draw_text(screen, f"HIGH: {max(self.score, high_score)}", 30, WIDTH - 100, 20, data.theme["TEXT_MUTED"])
            draw_text(screen, "Press ESC to exit", 20, 80, HEIGHT - 20, data.theme["TEXT_MUTED"], shadow=False)

            if self.game_over or self.won:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                screen.blit(overlay, (0, 0))
                
                draw_panel(screen, 400, 200, data.theme["PRIMARY"])
                
                msg = "YOU WON!" if self.won else "GAME OVER"
                draw_text(screen, msg, 60, WIDTH//2, HEIGHT//2 - 30, data.theme["PRIMARY"])
                draw_text(screen, "Press SPACE to restart", 20, WIDTH//2, HEIGHT//2 + 40, data.theme["TEXT_MUTED"])

            pygame.display.update()
            await asyncio.sleep(0)

