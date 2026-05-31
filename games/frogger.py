import pygame
import asyncio
import sys
import random
from core.config import WIDTH, HEIGHT, FPS
import core.data as data
from core.display import screen, clock
from core.utils import draw_text, draw_panel
from core.sounds import *
from graphics.drawing import *

class FroggerGame:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.frog_size = 30
        self.start_x = WIDTH // 2
        self.start_y = HEIGHT - 50
        self.frog_x = self.start_x
        self.frog_y = self.start_y
        
        self.score = 0
        self.game_over = False
        
        self.lanes = []
        for i in range(10):
            y = HEIGHT - 100 - i * 50
            speed = random.uniform(2, 5) * random.choice([-1, 1])
            is_river = i > 4
            self.lanes.append({
                'y': y,
                'speed': speed,
                'is_river': is_river,
                'obstacles': []
            })
            
            # Add initial obstacles
            num_obs = random.randint(2, 4)
            for _ in range(num_obs):
                self.lanes[-1]['obstacles'].append(pygame.Rect(random.randint(0, WIDTH), y + 5, random.randint(40, 80), 40))

    async def run(self):
        running = True
        high_score = data.get_high_score("Frogger")
        
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
                        
                    if event.key == pygame.K_UP:
                        self.frog_y -= 50
                        sound_jump.play()
                        self.score += 10
                    elif event.key == pygame.K_DOWN and self.frog_y < self.start_y:
                        self.frog_y += 50
                        sound_jump.play()
                        self.score -= 10
                    elif event.key == pygame.K_LEFT and self.frog_x > 0:
                        self.frog_x -= 50
                        sound_jump.play()
                    elif event.key == pygame.K_RIGHT and self.frog_x < WIDTH - self.frog_size:
                        self.frog_x += 50
                        sound_jump.play()

            if not self.game_over:
                frog_rect = pygame.Rect(self.frog_x, self.frog_y, self.frog_size, self.frog_size)
                
                on_log = False
                in_river = False
                
                for lane in self.lanes:
                    if abs(self.frog_y - lane['y']) < 25:
                        if lane['is_river']:
                            in_river = True
                    
                    for obs in lane['obstacles']:
                        obs.x += lane['speed']
                        if lane['speed'] > 0 and obs.left > WIDTH:
                            obs.right = 0
                        elif lane['speed'] < 0 and obs.right < 0:
                            obs.left = WIDTH
                            
                        if frog_rect.colliderect(obs):
                            if lane['is_river']:
                                on_log = True
                                self.frog_x += lane['speed']
                            else:
                                self.game_over = True
                                sound_hit.play()
                
                if in_river and not on_log:
                    self.game_over = True
                    sound_explosion.play()
                
                if self.frog_x < 0 or self.frog_x > WIDTH:
                    self.game_over = True
                    sound_explosion.play()

                if self.frog_y < 50:
                    sound_eat.play()
                    self.score += 100
                    if self.score > high_score:
                        data.set_high_score("Frogger", self.score)
                        high_score = self.score
                    # Reset frog to start
                    self.frog_x = self.start_x
                    self.frog_y = self.start_y
                    
                    # Make lanes faster
                    for lane in self.lanes:
                        lane['speed'] *= 1.1

            screen.fill(data.theme["BG_COLOR"])
            
            # Draw lanes
            for lane in self.lanes:
                color = (0, 0, 50) if lane['is_river'] else (30, 30, 30)
                pygame.draw.rect(screen, color, (0, lane['y'], WIDTH, 50))
                
                for obs in lane['obstacles']:
                    obs_color = data.theme["SECONDARY"] if lane['is_river'] else data.theme["PRIMARY"]
                    pygame.draw.rect(screen, obs_color, obs, border_radius=5)
            
            # Draw frog
            pygame.draw.rect(screen, data.theme["TERTIARY"], (self.frog_x, self.frog_y, self.frog_size, self.frog_size), border_radius=5)

            draw_text(screen, f"SCORE: {self.score}", 30, 100, 20, data.theme["TEXT"])
            draw_text(screen, f"HIGH: {max(self.score, high_score)}", 30, WIDTH - 100, 20, data.theme["TEXT_MUTED"])
            draw_text(screen, "Press ESC to exit", 20, 80, HEIGHT - 20, data.theme["TEXT_MUTED"], shadow=False)

            if self.game_over:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                screen.blit(overlay, (0, 0))
                
                draw_panel(screen, 400, 200, data.theme["PRIMARY"])
                
                draw_text(screen, "GAME OVER", 60, WIDTH//2, HEIGHT//2 - 30, data.theme["PRIMARY"])
                draw_text(screen, "Press SPACE to restart", 20, WIDTH//2, HEIGHT//2 + 40, data.theme["TEXT_MUTED"])

            pygame.display.update()
            await asyncio.sleep(0)
