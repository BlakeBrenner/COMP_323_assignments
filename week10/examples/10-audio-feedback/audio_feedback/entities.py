from __future__ import annotations

from dataclasses import dataclass
import random

import pygame


@dataclass
class Bounds:
    rect: pygame.Rect

    def clamp_ip(self, r: pygame.Rect) -> None:
        r.clamp_ip(self.rect)


class Player(pygame.sprite.Sprite):
    def __init__(self, center: tuple[int, int], *, color: pygame.Color, bounds: Bounds) -> None:
        super().__init__()

        self.image = pygame.Surface((46, 28), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, color, [(3, 25), (23, 3), (43, 25)])
        self.rect = self.image.get_rect(center=center)

        self.pos = pygame.Vector2(self.rect.center)
        self.bounds = bounds
        self.speed = 360.0

        self.max_hp = 6
        self.hp = 6

        self.invincible_after_hit = 0.55
        self.invincible_for = 0.0

        self.fire_cooldown = 0.18
        self.fire_for = 0.0

    def can_fire(self) -> bool:
        return self.fire_for <= 0.0

    def mark_fired(self) -> None:
        self.fire_for = self.fire_cooldown

    @property
    def is_invincible(self) -> bool:
        return self.invincible_for > 0.0

    def take_hit(self, damage: int = 1) -> bool:
        if self.is_invincible:
            return False

        self.hp = max(0, self.hp - int(damage))
        self.invincible_for = self.invincible_after_hit
        return True

    def update(self, dt: float) -> None:
        if self.invincible_for > 0.0:
            self.invincible_for = max(0.0, self.invincible_for - dt)

        if self.fire_for > 0.0:
            self.fire_for = max(0.0, self.fire_for - dt)

        keys = pygame.key.get_pressed()
        axis = pygame.Vector2(0, 0)

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            axis.x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            axis.x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            axis.y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            axis.y += 1

        if axis.length_squared() > 0:
            axis = axis.normalize()

        self.pos += axis * self.speed * dt
        self.rect.center = (int(round(self.pos.x)), int(round(self.pos.y)))
        self.bounds.clamp_ip(self.rect)
        self.pos.xy = self.rect.center


class Mob(pygame.sprite.Sprite):
    def __init__(self, *, color: pygame.Color, playfield: pygame.Rect, rng: random.Random) -> None:
        super().__init__()

        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, self.image.get_rect(), border_radius=7)
        self.rect = self.image.get_rect()

        self.playfield = playfield
        self.rng = rng
        self.speed_x = 0.0
        self.speed_y = 0.0
        self.respawn()

    def respawn(self) -> None:
        self.rect.x = self.rng.randrange(self.playfield.left, self.playfield.right - self.rect.width)
        self.rect.y = self.rng.randrange(self.playfield.top - 130, self.playfield.top - 30)
        self.speed_x = float(self.rng.randrange(-70, 71))
        self.speed_y = float(self.rng.randrange(120, 260))

    def update(self, dt: float) -> None:
        self.rect.x += int(round(self.speed_x * dt))
        self.rect.y += int(round(self.speed_y * dt))

        if (
            self.rect.top > self.playfield.bottom + 20
            or self.rect.right < self.playfield.left - 20
            or self.rect.left > self.playfield.right + 20
        ):
            self.respawn()


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, *, color: pygame.Color, top_limit: int) -> None:
        super().__init__()

        self.image = pygame.Surface((6, 16), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, self.image.get_rect(), border_radius=2)
        self.rect = self.image.get_rect(centerx=x, bottom=y)

        self.speed_y = -520.0
        self.top_limit = top_limit

    def update(self, dt: float) -> None:
        self.rect.y += int(round(self.speed_y * dt))
        if self.rect.bottom < self.top_limit:
            self.kill()