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
    async def run(self):
        bird = Bird()
        pipes = []
        clouds = [Cloud() for _ in range(4)]
        stars = [Star() for _ in range(40)]
        cityscape = Cityscape()
        coins = []
        score = 0
        high_score = data.get_high_score("Flappy")
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
                            sound_jump.play()
                            bird.jump()
                            last_pipe_time = pygame.time.get_ticks()
                        elif game_state == 1:
                            sound_jump.play()
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
                        sound_jump.play()
                        bird.jump()
                        last_pipe_time = pygame.time.get_ticks()
                    elif game_state == 1:
                        sound_jump.play()
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
                    if game_state == 1: sound_hit.play()
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
                        if game_state == 1: sound_hit.play()
                        game_state = 2
                        flash_alpha = 255
                    if pipe.x + pipe.width < bird.x and not pipe.passed:
                        score += 1
                        sound_score.play()
                        pipe.passed = True
                
                for coin in coins:
                    coin.move()
                    if coin.collide(bird):
                        sound_eat.play()
                        score += 5 
                
                pipes = [pipe for pipe in pipes if pipe.x + pipe.width > -50]
                coins = [coin for coin in coins if coin.x + coin.radius > -50 and not coin.collected]

            elif game_state == 2: 
                if bird.y + bird.radius < HEIGHT - GROUND_HEIGHT:
                    bird.move()
                if score > high_score:
                    high_score = score
                    data.set_high_score("Flappy", high_score)

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
            await asyncio.sleep(0)

