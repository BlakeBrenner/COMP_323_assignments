# Week 11 — Content Pass Example
# Demonstrates: config extraction, spawn rate tuning, progressive difficulty
#
# This example builds on the course shooter pattern and shows how to
# organize difficulty variables into a config, tune spawn rate and speed,
# and add progressive scaling.

import pygame
import random
import sys
import os

# ---------------------------------------------------------------------------
# Game config — all tunable difficulty values live here
# ---------------------------------------------------------------------------
from game_config import *

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
game_dir = os.path.dirname(__file__)
assets_dir = os.path.join(game_dir, "assets")
img_dir = os.path.join(assets_dir, "images")
snd_dir = os.path.join(assets_dir, "sounds")

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Content Pass Demo — Week 11")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 22)

# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

# ---------------------------------------------------------------------------
# Audio helper (from Week 10 pattern)
# ---------------------------------------------------------------------------
class AudioBank:
    def __init__(self):
        self.enabled = True
        self.muted = False
        self.sounds = {}

    def load_sound(self, name, path):
        try:
            self.sounds[name] = pygame.mixer.Sound(path)
        except Exception:
            pass  # silent fallback

    def play_sfx(self, name):
        if self.enabled and not self.muted and name in self.sounds:
            self.sounds[name].play()

    def toggle_mute(self):
        self.muted = not self.muted

audio = AudioBank()

# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 30))
        self.image.fill(CYAN)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIN_WIDTH // 2
        self.rect.bottom = WIN_HEIGHT - 20
        self.speed = PLAYER_SPEED
        self.health = PLAYER_HEALTH
        self.last_fired = 0

    def update(self):
        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -self.speed
        if keys[pygame.K_RIGHT]:
            dx = self.speed
        self.rect.x += dx
        self.rect.clamp_ip(window.get_rect())

    def fire(self, group, all_sprites):
        now = pygame.time.get_ticks()
        if now - self.last_fired > FIRE_COOLDOWN_MS:
            self.last_fired = now
            p = Projectile(self.rect.centerx, self.rect.top)
            group.add(p)
            all_sprites.add(p)
            audio.play_sfx("fire")

# ---------------------------------------------------------------------------
# Enemy
# ---------------------------------------------------------------------------
class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed_override=None):
        super().__init__()
        size = random.randint(20, 40)
        self.image = pygame.Surface((size, size))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, WIN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-80, -20)
        if speed_override is not None:
            self.speed_y = speed_override
        else:
            self.speed_y = random.uniform(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > WIN_HEIGHT + 10:
            self.kill()

# ---------------------------------------------------------------------------
# Projectile
# ---------------------------------------------------------------------------
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 14))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -10

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0:
            self.kill()

# ---------------------------------------------------------------------------
# Spawn controller — demonstrates progressive difficulty
# ---------------------------------------------------------------------------
class SpawnController:
    def __init__(self):
        self.last_spawn = pygame.time.get_ticks()
        self.game_start = pygame.time.get_ticks()

    def current_delay(self):
        elapsed = (pygame.time.get_ticks() - self.game_start) / 1000
        return max(SPAWN_DELAY_MIN_MS,
                   SPAWN_DELAY_START_MS - elapsed * SPAWN_RAMP_PER_SEC)

    def current_speed_bonus(self):
        elapsed = (pygame.time.get_ticks() - self.game_start) / 1000
        return min(elapsed * ENEMY_SPEED_GROWTH, ENEMY_SPEED_MAX_BONUS)

    def try_spawn(self, enemy_group, all_sprites):
        now = pygame.time.get_ticks()
        if now - self.last_spawn < self.current_delay():
            return
        if len(enemy_group) >= MAX_ENEMIES:
            return
        self.last_spawn = now
        bonus = self.current_speed_bonus()
        speed = random.uniform(ENEMY_SPEED_MIN + bonus, ENEMY_SPEED_MAX + bonus)
        e = Enemy(speed_override=speed)
        enemy_group.add(e)
        all_sprites.add(e)

# ---------------------------------------------------------------------------
# HUD
# ---------------------------------------------------------------------------
def draw_hud(surface, player, score, spawner):
    # health bar
    bar_w = 200
    bar_h = 16
    fill = max(0, (player.health / PLAYER_HEALTH) * bar_w)
    pygame.draw.rect(surface, RED, (10, 10, bar_w, bar_h))
    pygame.draw.rect(surface, GREEN, (10, 10, fill, bar_h))

    # score
    txt = font.render(f"Score: {score}", True, WHITE)
    surface.blit(txt, (10, 32))

    # current difficulty info
    delay = int(spawner.current_delay())
    bonus = round(spawner.current_speed_bonus(), 1)
    info = font.render(f"Spawn: {delay}ms  Speed+: {bonus}", True, WHITE)
    surface.blit(info, (10, 56))

    # mute indicator
    if audio.muted:
        mute_txt = font.render("[MUTED]", True, YELLOW)
        surface.blit(mute_txt, (WIN_WIDTH - 100, 10))

# ---------------------------------------------------------------------------
# Main game loop
# ---------------------------------------------------------------------------
def main():
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    spawner = SpawnController()
    score = 0
    running = True

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.fire(projectiles, all_sprites)
                elif event.key == pygame.K_m:
                    audio.toggle_mute()
                elif event.key == pygame.K_ESCAPE:
                    running = False

        # spawn enemies with progressive difficulty
        spawner.try_spawn(enemies, all_sprites)

        # update
        all_sprites.update()

        # collision: projectiles vs enemies
        hits = pygame.sprite.groupcollide(enemies, projectiles, True, True)
        for hit in hits:
            score += 10
            audio.play_sfx("hit")

        # collision: enemies vs player
        damage_hits = pygame.sprite.spritecollide(player, enemies, True)
        for hit in damage_hits:
            player.health -= ENEMY_DAMAGE
            audio.play_sfx("damage")
            if player.health <= 0:
                running = False

        # draw
        window.fill(BLACK)
        all_sprites.draw(window)
        draw_hud(window, player, score, spawner)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
