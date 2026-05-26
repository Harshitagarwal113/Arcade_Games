import pygame
import os

if not pygame.mixer.get_init():
    pygame.mixer.init()

try:
    base_dir = os.path.dirname(os.path.dirname(__file__))
    assets_dir = os.path.join(base_dir, 'assets', 'sounds')
    
    sound_eat = pygame.mixer.Sound(os.path.join(assets_dir, 'eat.wav'))
    sound_hit = pygame.mixer.Sound(os.path.join(assets_dir, 'hit.wav'))
    sound_jump = pygame.mixer.Sound(os.path.join(assets_dir, 'jump.wav'))
    sound_score = pygame.mixer.Sound(os.path.join(assets_dir, 'score.wav'))
    sound_shoot = pygame.mixer.Sound(os.path.join(assets_dir, 'shoot.wav'))
    sound_explosion = pygame.mixer.Sound(os.path.join(assets_dir, 'explosion.wav'))
    sound_click = pygame.mixer.Sound(os.path.join(assets_dir, 'click.wav'))
except Exception as e:
    print("Warning: Could not load sounds.", e)
    class DummySound:
        def play(self): pass
    sound_eat = sound_hit = sound_jump = sound_score = sound_shoot = sound_explosion = sound_click = DummySound()
