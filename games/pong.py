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

    async def run(self):
        running = True
        high_score = data.get_high_score("Pong")
        
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
                sound_hit.play()
                self.add_particles(self.ball.centerx, self.ball.centery, data.theme["TEXT"])
            
            if self.ball.colliderect(self.p1) and self.ball_vel[0] < 0:
                self.ball_vel[0] *= -1.05
                sound_hit.play()
                if self.ball_vel[0] > 15: self.ball_vel[0] = 15
                self.shake_timer = 8
                self.add_particles(self.ball.left, self.ball.centery, data.theme["TERTIARY"], dir_x=1)
            if self.ball.colliderect(self.p2) and self.ball_vel[0] > 0:
                self.ball_vel[0] *= -1.05
                sound_hit.play()
                if self.ball_vel[0] < -15: self.ball_vel[0] = -15
                self.shake_timer = 8
                self.add_particles(self.ball.right, self.ball.centery, data.theme["SECONDARY"], dir_x=-1)

            if self.ball.left <= -50:
                self.score[1] += 1
                sound_score.play()
                self.ball.center = (WIDTH//2, HEIGHT//2)
                self.ball_vel = [4.0, random.choice([-4.0, 4.0])]
                self.ball_trail.clear()
                if self.score[1] > high_score:
                    high_score = self.score[1]
                    data.set_high_score("Pong", high_score)
            if self.ball.right >= WIDTH + 50:
                self.score[0] += 1
                sound_score.play()
                self.ball.center = (WIDTH//2, HEIGHT//2)
                self.ball_vel = [-4.0, random.choice([-4.0, 4.0])]
                self.ball_trail.clear()
                if self.score[0] > high_score:
                    high_score = self.score[0]
                    data.set_high_score("Pong", high_score)

            screen.fill(data.theme["BG_COLOR"])
            
            bg_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            grid_spacing = 40
            bg_alpha = int(20 + math.sin(self.pulse_anim * 0.5) * 15)
            for x in range(0, WIDTH, grid_spacing):
                pygame.draw.line(bg_surf, (*data.theme["PRIMARY"], bg_alpha), (x, 0), (x, HEIGHT))
            for y in range(0, HEIGHT, grid_spacing):
                pygame.draw.line(bg_surf, (*data.theme["PRIMARY"], bg_alpha), (0, y), (WIDTH, y))
            screen.blit(bg_surf, (0,0))
            
            pulse_alpha = int(150 + math.sin(self.pulse_anim * 2) * 100)
            net_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            for y in range(0, HEIGHT, 40):
                pygame.draw.rect(net_surface, (*data.theme["SECONDARY"], pulse_alpha), (WIDTH//2 - 2, y + 10, 4, 20), border_radius=2)
            screen.blit(net_surface, (0,0))
                
            draw_spaceship_paddle(screen, self.p1, data.theme, True)
            draw_spaceship_paddle(screen, self.p2, data.theme, True)
            
            for i, tr in enumerate(self.ball_trail):
                alpha = int(100 + 155 * (i / max(1, len(self.ball_trail))))
                radius = int(4 + 8 * (i / max(1, len(self.ball_trail))))
                blend = i / max(1, len(self.ball_trail))
                c1, c2 = data.theme["TEXT"], data.theme["PRIMARY"]
                color = (int(c1[0]*(1-blend) + c2[0]*blend), int(c1[1]*(1-blend) + c2[1]*blend), int(c1[2]*(1-blend) + c2[2]*blend), alpha)
                
                tr_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                pygame.draw.circle(tr_surf, color, (radius, radius), radius)
                screen.blit(tr_surf, (tr.centerx - radius, tr.centery - radius))
                
            draw_energy_ball(screen, self.ball, data.theme)
            
            for p in self.particles[:]:
                p[0][0] += p[1][0]
                p[0][1] += p[1][1]
                p[2] -= 0.2
                if p[2] <= 0:
                    self.particles.remove(p)
                else:
                    pygame.draw.circle(screen, p[3], (int(p[0][0]), int(p[0][1])), int(p[2]))

            draw_text(screen, str(self.score[0]), 100, WIDTH//4, 100, data.theme["TERTIARY"])
            draw_text(screen, str(self.score[1]), 100, 3*WIDTH//4, 100, data.theme["SECONDARY"])
            draw_text(screen, "P1: W/S | P2: UP/DOWN | ESC: Exit", 20, WIDTH//2, HEIGHT - 30, data.theme["TEXT_MUTED"])

            if self.shake_timer > 0:
                shake_x = random.randint(-5, 5)
                shake_y = random.randint(-5, 5)
                shook_surface = screen.copy()
                screen.fill(data.theme["BG_COLOR"])
                screen.blit(shook_surface, (shake_x, shake_y))

            pygame.display.update()
            await asyncio.sleep(0)

