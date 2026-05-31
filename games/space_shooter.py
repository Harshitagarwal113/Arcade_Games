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

    async def run(self):
        running = True
        high_score = data.get_high_score("SpaceShooter")
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
                        sound_shoot.play()
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
                        if self.game_state == 1: sound_explosion.play()
                        self.game_state = 2
                        if self.score > high_score: data.set_high_score("SpaceShooter", self.score)
                    elif a['rect'].top > HEIGHT:
                        self.aliens.remove(a)
                        
                    for b in self.bullets[:]:
                        if b.colliderect(a['rect']):
                            sound_explosion.play()
                            if b in self.bullets: self.bullets.remove(b)
                            if a in self.aliens: self.aliens.remove(a)
                            self.score += 10
                            self.floating_texts.append({'x': a['rect'].centerx, 'y': a['rect'].centery, 'text': "+10", 'alpha': 255})
                            self.particles.append({'x': a['rect'].centerx, 'y': a['rect'].centery, 'vx': 0, 'vy': 0, 'life': 20, 'radius': 5, 'color': data.theme["SECONDARY"], 'type': 'shockwave'})
                            for _ in range(25):
                                self.particles.append({'x': a['rect'].centerx, 'y': a['rect'].centery, 'vx': random.uniform(-8, 8), 'vy': random.uniform(-8, 8), 'life': random.randint(15, 30), 'color': data.theme["SECONDARY"]})
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
                draw_alien(screen, a['rect'], data.theme, self.anim_timer)

            if self.game_state == 1:
                draw_spaceship_paddle(screen, self.player, data.theme, False)

            for p in self.particles:
                if p.get('type') == 'shockwave':
                    pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), int(p.get('radius', 5)), max(1, 5 - int(p.get('radius', 5)/15)))
                elif p.get('type') == 'muzzle':
                    pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), int(p.get('radius', 5)))
                else:
                    pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), int(p.get('radius', 4)))
            for t in self.floating_texts:
                draw_text(screen, t['text'], 20, int(t['x']), int(t['y']), data.theme["TEXT"], shadow=False)

            if self.game_state == 0:
                draw_text(screen, "SPACE SHOOTER", 60, WIDTH//2, HEIGHT//2 - 50, data.theme["SECONDARY"], data.theme["SHADOW"])
                draw_text(screen, "Press SPACE to start", 30, WIDTH//2, HEIGHT//2 + 50, data.theme["TEXT"])
                draw_text(screen, "Press ESC to return to Hub", 20, 100, 20, data.theme["TEXT_MUTED"])
            elif self.game_state == 1:
                draw_text(screen, f"{self.score}", 60, WIDTH//2, 50, data.theme["TEXT"], data.theme["SHADOW"])
            elif self.game_state == 2:
                draw_panel(screen, 300, 240, data.theme["SECONDARY"])
                draw_text(screen, "GAME OVER", 50, WIDTH//2, HEIGHT//2 - 160, data.theme["SECONDARY"], data.theme["SHADOW"])
                draw_text(screen, "SCORE", 25, WIDTH//2, HEIGHT//2 - 80, data.theme["TEXT_MUTED"], shadow=False)
                draw_text(screen, str(self.score), 50, WIDTH//2, HEIGHT//2 - 40, data.theme["TEXT"])
                draw_text(screen, "BEST", 25, WIDTH//2, HEIGHT//2 + 10, data.theme["TEXT_MUTED"], shadow=False)
                draw_text(screen, str(high_score), 50, WIDTH//2, HEIGHT//2 + 50, data.theme["TEXT"])
                draw_text(screen, "Press SPACE to Restart", 20, WIDTH//2, HEIGHT//2 + 150, data.theme["TEXT"])
                draw_text(screen, "Press ESC to return to Hub", 20, WIDTH//2, HEIGHT//2 + 180, data.theme["TEXT_MUTED"])

            pygame.display.update()
            await asyncio.sleep(0)

