from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum

import pygame


class BoundaryMode(str, Enum):
    CLAMP = "clamp"
    WRAP = "wrap"
    BOUNCE = "bounce"


@dataclass
class Goal:
    pos: pygame.Vector2
    radius: int = 16


@dataclass
class Teleporter:
    rect: pygame.Rect


@dataclass
class Platform:
    """A moving platform that bounces the player."""
    rect: pygame.Rect
    velocity: pygame.Vector2  # Direction and speed of movement
    min_pos: pygame.Vector2  # Boundary for movement
    max_pos: pygame.Vector2  # Boundary for movement
    bounce_strength: float = 800.0  # Speed to bounce player upward


@dataclass
class Checkpoint:
    """A checkpoint that the player can reach to save progress."""
    rect: pygame.Rect
    is_active: bool = False
    stage: int = 0


class Game:
    fps = 60

    SCREEN_W, SCREEN_H = 960, 540
    HUD_H = 54
    PLAYFIELD_PADDING = 10

    PLAYER_SIZE = 32
    PLAYER_ACCEL = 2400.0
    PLAYER_MAX_SPEED = 520.0
    PLAYER_FRICTION = 10.0

    # Platformer-style vertical movement
    GRAVITY = 2200.0
    JUMP_SPEED = 820.0

    TIMER_SECONDS = 30.0

    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((self.SCREEN_W, self.SCREEN_H))
        self.font = pygame.font.SysFont(None, 22)
        self.big_font = pygame.font.SysFont(None, 48)

        self.screen_rect = pygame.Rect(0, 0, self.SCREEN_W, self.SCREEN_H)
        self.playfield = pygame.Rect(
            self.PLAYFIELD_PADDING,
            self.HUD_H + self.PLAYFIELD_PADDING,
            self.SCREEN_W - 2 * self.PLAYFIELD_PADDING,
            self.SCREEN_H - self.HUD_H - 2 * self.PLAYFIELD_PADDING,
        )

        self.boundary_mode = BoundaryMode.CLAMP
        self.platformer_mode = False
        self.level = 1
        self.state = "title"  # title | play | win | lose

        self.player_rect = pygame.Rect(0, 0, self.PLAYER_SIZE, self.PLAYER_SIZE)
        self.player_pos = pygame.Vector2(0, 0)
        self.player_vel = pygame.Vector2(0, 0)

        self.on_ground = True
        self.jump_requested = False

        self.time_left = self.TIMER_SECONDS

        self.goal = Goal(pos=pygame.Vector2(0, 0))
        self.teleporter = Teleporter(rect=pygame.Rect(0, 0, 40, 40))

        # Moving platforms
        self.platforms: list[Platform] = []

        # Checkpoint system
        self.checkpoints: list[Checkpoint] = []
        self.current_stage = 0
        self.checkpoint_spawn_pos = pygame.Vector2(0, 0)

        self._reset_level(keep_state=True)

    def _random_point_in_playfield(self, margin: int) -> pygame.Vector2:
        x = random.randint(self.playfield.left + margin, self.playfield.right - margin)
        y = random.randint(self.playfield.top + margin, self.playfield.bottom - margin)
        return pygame.Vector2(x, y)

    def _setup_level(self) -> None:
        """Configure the current level layout."""
        if self.level == 1:
            # Level 1: Simple single stage with random goal
            self.current_stage = 0
            self.checkpoints = []
            self.platforms = []
            self.goal.pos = self._random_point_in_playfield(margin=60)

        elif self.level == 2:
            # Level 2: Moving platforms with checkpoints (3 platforms, 2 checkpoints)
            self.current_stage = 0

            # Create two checkpoints
            cp1 = Checkpoint(
                rect=pygame.Rect(0, 0, 50, 50),
                stage=0
            )
            cp1.rect.center = (self.playfield.centerx - 200, self.playfield.centery - 80)

            cp2 = Checkpoint(
                rect=pygame.Rect(0, 0, 50, 50),
                stage=1
            )
            cp2.rect.center = (self.playfield.centerx + 200, self.playfield.centery - 80)

            self.checkpoints = [cp1, cp2]

            # Create moving platforms that guide the player
            # Platform 1: Moves left-right in the lower area
            p1 = Platform(
                rect=pygame.Rect(0, 0, 100, 16),
                velocity=pygame.Vector2(150, 0),  # Moves right at 150 px/s
                min_pos=pygame.Vector2(self.playfield.left + 100, self.playfield.centery + 120),
                max_pos=pygame.Vector2(self.playfield.centerx - 100, self.playfield.centery + 120),
                bounce_strength=600.0
            )
            p1.rect.center = (int(p1.min_pos.x), int(p1.min_pos.y))

            # Platform 2: Moves up-down on the right side, lower position
            p2 = Platform(
                rect=pygame.Rect(0, 0, 100, 16),
                velocity=pygame.Vector2(0, 120),  # Moves down at 120 px/s
                min_pos=pygame.Vector2(self.playfield.centerx + 100, self.playfield.centery),
                max_pos=pygame.Vector2(self.playfield.centerx + 100, self.playfield.bottom - 80),
                bounce_strength=700.0
            )
            p2.rect.center = (int(p2.min_pos.x), int(p2.min_pos.y))

            # Platform 3: Moves left-right on the left side, lower position
            p3 = Platform(
                rect=pygame.Rect(0, 0, 100, 16),
                velocity=pygame.Vector2(-140, 0),  # Moves left at 140 px/s
                min_pos=pygame.Vector2(self.playfield.left + 150, self.playfield.bottom - 100),
                max_pos=pygame.Vector2(self.playfield.centerx - 50, self.playfield.bottom - 100),
                bounce_strength=650.0
            )
            p3.rect.center = (int(p3.max_pos.x), int(p3.max_pos.y))

            self.platforms = [p1, p2, p3]

            # First goal is at the first checkpoint location
            self.goal.pos = pygame.Vector2(cp1.rect.center)

        elif self.level == 3:
            # Level 3: More challenging with 5 moving platforms and 3 checkpoints
            self.current_stage = 0

            # Create three checkpoints
            cp1 = Checkpoint(
                rect=pygame.Rect(0, 0, 50, 50),
                stage=0
            )
            cp1.rect.center = (self.playfield.left + 120, self.playfield.centery - 100)

            cp2 = Checkpoint(
                rect=pygame.Rect(0, 0, 50, 50),
                stage=1
            )
            cp2.rect.center = (self.playfield.centerx, self.playfield.centery - 80)

            cp3 = Checkpoint(
                rect=pygame.Rect(0, 0, 50, 50),
                stage=2
            )
            cp3.rect.center = (self.playfield.right - 120, self.playfield.centery - 100)

            self.checkpoints = [cp1, cp2, cp3]

            # Create 5 moving platforms for increased challenge
            # Platform 1: Horizontal on left side
            p1 = Platform(
                rect=pygame.Rect(0, 0, 90, 14),
                velocity=pygame.Vector2(120, 0),
                min_pos=pygame.Vector2(self.playfield.left + 80, self.playfield.bottom - 120),
                max_pos=pygame.Vector2(self.playfield.centerx - 80, self.playfield.bottom - 120),
                bounce_strength=650.0
            )
            p1.rect.center = (int(p1.min_pos.x), int(p1.min_pos.y))

            # Platform 2: Vertical on left-center area
            p2 = Platform(
                rect=pygame.Rect(0, 0, 80, 16),
                velocity=pygame.Vector2(0, 140),
                min_pos=pygame.Vector2(self.playfield.centerx - 150, self.playfield.centery - 20),
                max_pos=pygame.Vector2(self.playfield.centerx - 150, self.playfield.bottom - 90),
                bounce_strength=680.0
            )
            p2.rect.center = (int(p2.min_pos.x), int(p2.min_pos.y))

            # Platform 3: Horizontal in center
            p3 = Platform(
                rect=pygame.Rect(0, 0, 100, 16),
                velocity=pygame.Vector2(-160, 0),
                min_pos=pygame.Vector2(self.playfield.centerx - 100, self.playfield.centery),
                max_pos=pygame.Vector2(self.playfield.centerx + 100, self.playfield.centery),
                bounce_strength=700.0
            )
            p3.rect.center = (int(p3.max_pos.x), int(p3.max_pos.y))

            # Platform 4: Vertical on right-center area (moving up and down)
            p4 = Platform(
                rect=pygame.Rect(0, 0, 80, 16),
                velocity=pygame.Vector2(0, -130),
                min_pos=pygame.Vector2(self.playfield.centerx + 150, self.playfield.centery + 20),
                max_pos=pygame.Vector2(self.playfield.centerx + 150, self.playfield.bottom - 100),
                bounce_strength=690.0
            )
            p4.rect.center = (int(p4.min_pos.x), int(p4.min_pos.y))

            # Platform 5: Horizontal on right side
            p5 = Platform(
                rect=pygame.Rect(0, 0, 90, 14),
                velocity=pygame.Vector2(-130, 0),
                min_pos=pygame.Vector2(self.playfield.centerx + 80, self.playfield.bottom - 110),
                max_pos=pygame.Vector2(self.playfield.right - 80, self.playfield.bottom - 110),
                bounce_strength=660.0
            )
            p5.rect.center = (int(p5.max_pos.x), int(p5.max_pos.y))

            self.platforms = [p1, p2, p3, p4, p5]

            # First goal is at the first checkpoint location
            self.goal.pos = pygame.Vector2(cp1.rect.center)

    def _reset_level(self, keep_state: bool = False) -> None:
        self.player_pos = pygame.Vector2(self.playfield.center)
        self.player_vel = pygame.Vector2(0, 0)
        self.player_rect.center = self.player_pos
        self.on_ground = True
        self.jump_requested = False

        self._setup_level()

        tp_center = self._random_point_in_playfield(margin=70)
        self.teleporter.rect.center = (int(tp_center.x), int(tp_center.y))

        self.time_left = self.TIMER_SECONDS
        self.checkpoint_spawn_pos = self.player_pos.copy()

        if not keep_state:
            self.state = "play"

    def _cycle_boundary_mode(self) -> None:
        modes = list(BoundaryMode)
        idx = modes.index(self.boundary_mode)
        self.boundary_mode = modes[(idx + 1) % len(modes)]

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            return

        if event.key == pygame.K_TAB:
            self._cycle_boundary_mode()
            return

        if event.key == pygame.K_p:
            self.platformer_mode = not self.platformer_mode
            if self.state != "title":
                self._reset_level(keep_state=True)
            return

        if event.key == pygame.K_r:
            self.level = 1
            self._reset_level(keep_state=(self.state == "title"))
            if self.state != "title":
                self.state = "play"
            return

        if self.state == "title" and event.key == pygame.K_SPACE:
            self.level = 1
            self.state = "play"
            self._reset_level(keep_state=True)
            return

        if self.state in {"win", "lose"} and event.key == pygame.K_SPACE:
            self.state = "play"
            self._reset_level(keep_state=True)
            return

        if self.state == "play" and self.platformer_mode:
            if event.key in {pygame.K_UP, pygame.K_w}:
                self.jump_requested = True

    def _read_direction(self) -> pygame.Vector2:
        keys = pygame.key.get_pressed()
        x = 0
        y = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            y += 1

        direction = pygame.Vector2(x, y)
        if direction.length_squared() > 0:
            direction = direction.normalize()
        return direction

    def _read_horizontal(self) -> float:
        keys = pygame.key.get_pressed()
        x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            x += 1
        return float(x)

    def _apply_platformer_vertical_bounds(self) -> None:
        if self.player_rect.bottom >= self.playfield.bottom:
            self.player_rect.bottom = self.playfield.bottom
            self.player_vel.y = 0
            self.on_ground = True

        if self.player_rect.top < self.playfield.top:
            self.player_rect.top = self.playfield.top
            if self.player_vel.y < 0:
                self.player_vel.y = 0

        self.player_pos.update(self.player_rect.center)

    def _apply_bounds_player(self) -> None:
        if self.boundary_mode == BoundaryMode.CLAMP:
            self.player_rect.clamp_ip(self.playfield)
            self.player_pos.update(self.player_rect.center)
            return

        if self.boundary_mode == BoundaryMode.WRAP:
            if self.player_rect.right < self.playfield.left:
                self.player_rect.left = self.playfield.right
            elif self.player_rect.left > self.playfield.right:
                self.player_rect.right = self.playfield.left

            if self.player_rect.bottom < self.playfield.top:
                self.player_rect.top = self.playfield.bottom
            elif self.player_rect.top > self.playfield.bottom:
                self.player_rect.bottom = self.playfield.top

            self.player_pos.update(self.player_rect.center)
            return

        # BOUNCE
        bounced = False
        if self.player_rect.left < self.playfield.left:
            self.player_rect.left = self.playfield.left
            self.player_vel.x *= -1
            bounced = True
        elif self.player_rect.right > self.playfield.right:
            self.player_rect.right = self.playfield.right
            self.player_vel.x *= -1
            bounced = True

        if self.player_rect.top < self.playfield.top:
            self.player_rect.top = self.playfield.top
            self.player_vel.y *= -1
            bounced = True
        elif self.player_rect.bottom > self.playfield.bottom:
            self.player_rect.bottom = self.playfield.bottom
            self.player_vel.y *= -1
            bounced = True

        if bounced:
            self.player_pos.update(self.player_rect.center)

    def _player_reaches_goal(self) -> bool:
        dx = self.player_pos.x - self.goal.pos.x
        dy = self.player_pos.y - self.goal.pos.y
        return (dx * dx + dy * dy) <= (self.goal.radius + self.PLAYER_SIZE * 0.3) ** 2

    def _check_checkpoint_collision(self) -> None:
        """Check if player touches a checkpoint and advance level state."""
        for checkpoint in self.checkpoints:
            if self.player_rect.colliderect(checkpoint.rect):
                # Only trigger checkpoints in the correct stage
                if checkpoint.stage == self.current_stage and not checkpoint.is_active:
                    checkpoint.is_active = True
                    self.checkpoint_spawn_pos = self.player_pos.copy()
                    self.current_stage += 1

                    # Update goal to next checkpoint or final goal
                    if self.current_stage < len(self.checkpoints):
                        self.goal.pos = pygame.Vector2(self.checkpoints[self.current_stage].rect.center)
                    else:
                        # Final stage: place goal at a random location
                        self.goal.pos = self._random_point_in_playfield(margin=60)

    def _update_platforms(self, dt: float) -> None:
        """Update platform positions and handle collisions with player."""
        for platform in self.platforms:
            # Update platform position
            platform.rect.x += platform.velocity.x * dt
            platform.rect.y += platform.velocity.y * dt

            # Reverse direction if platform hits boundary
            if platform.velocity.x > 0:  # Moving right
                if platform.rect.right >= platform.max_pos.x:
                    platform.velocity.x *= -1
                    platform.rect.right = int(platform.max_pos.x)
            elif platform.velocity.x < 0:  # Moving left
                if platform.rect.left <= platform.min_pos.x:
                    platform.velocity.x *= -1
                    platform.rect.left = int(platform.min_pos.x)

            if platform.velocity.y > 0:  # Moving down
                if platform.rect.bottom >= platform.max_pos.y:
                    platform.velocity.y *= -1
                    platform.rect.bottom = int(platform.max_pos.y)
            elif platform.velocity.y < 0:  # Moving up
                if platform.rect.top <= platform.min_pos.y:
                    platform.velocity.y *= -1
                    platform.rect.top = int(platform.min_pos.y)

            # Check collision with player (only from above)
            if self.player_rect.colliderect(platform.rect):
                # Check if player is coming from above
                if self.player_vel.y >= 0 and self.player_rect.bottom - self.player_vel.y * dt <= platform.rect.top + 10:
                    # Bounce the player
                    self.player_rect.bottom = platform.rect.top
                    self.player_vel.y = -platform.bounce_strength
                    self.on_ground = True
                    self.player_pos.update(self.player_rect.center)

    def update(self, dt: float) -> None:
        if self.state != "play":
            return

        self.time_left -= dt
        if self.time_left <= 0:
            self.time_left = 0
            self.state = "lose"
            return

        if self.platformer_mode:
            x = self._read_horizontal()

            self.player_vel.x += x * self.PLAYER_ACCEL * dt
            if x == 0:
                self.player_vel.x -= self.player_vel.x * min(1.0, self.PLAYER_FRICTION * dt)
            self.player_vel.x = max(-self.PLAYER_MAX_SPEED, min(self.PLAYER_MAX_SPEED, self.player_vel.x))

            if self.jump_requested and self.on_ground:
                self.player_vel.y = -self.JUMP_SPEED
                self.on_ground = False
            self.jump_requested = False

            self.player_vel.y += self.GRAVITY * dt

            self.player_pos += self.player_vel * dt
            self.player_rect.center = (int(self.player_pos.x), int(self.player_pos.y))

            prev_y = self.player_rect.centery
            self._apply_bounds_player()
            self.player_rect.centery = prev_y
            self.player_pos.y = prev_y

            self._apply_platformer_vertical_bounds()
        else:
            direction = self._read_direction()

            self.player_vel += direction * self.PLAYER_ACCEL * dt

            if direction.length_squared() == 0:
                self.player_vel -= self.player_vel * min(1.0, self.PLAYER_FRICTION * dt)

            if self.player_vel.length() > self.PLAYER_MAX_SPEED:
                self.player_vel.scale_to_length(self.PLAYER_MAX_SPEED)

            self.player_pos += self.player_vel * dt
            self.player_rect.center = (int(self.player_pos.x), int(self.player_pos.y))

            self._apply_bounds_player()

        # Teleporter collision
        if self.player_rect.colliderect(self.teleporter.rect):
            new_pos = self._random_point_in_playfield(margin=80)
            self.player_pos.update(new_pos)
            self.player_rect.center = (int(new_pos.x), int(new_pos.y))

        # Update moving platforms
        self._update_platforms(dt)

        # Check checkpoint collisions
        self._check_checkpoint_collision()

        # Check goal collision
        if self._player_reaches_goal():
            self.level += 1
            self.state = "win"

    def _draw_hud(self) -> None:
        pygame.draw.rect(self.screen, (46, 52, 64), pygame.Rect(0, 0, self.SCREEN_W, self.HUD_H))

        control = "PLATFORMER" if self.platformer_mode else "TOPDOWN"

        # Show stage progress on level 2
        stage_info = ""
        if self.level == 2:
            stage_info = f"  Stage: {self.current_stage + 1}/{len(self.checkpoints) + 1}"

        left = f"Level {self.level}{stage_info}   Bounds: {self.boundary_mode.value.upper()}   Control: {control}"
        right = f"Time: {self.time_left:0.1f}s"

        left_surf = self.font.render(left, True, (216, 222, 233))
        right_surf = self.font.render(right, True, (216, 222, 233))

        self.screen.blit(left_surf, (14, 16))
        self.screen.blit(right_surf, (self.SCREEN_W - right_surf.get_width() - 14, 16))

    def _draw_center_message(self, title: str, subtitle: str) -> None:
        title_surf = self.big_font.render(title, True, (236, 239, 244))
        sub_surf = self.font.render(subtitle, True, (216, 222, 233))

        self.screen.blit(
            title_surf,
            (
                self.SCREEN_W // 2 - title_surf.get_width() // 2,
                self.SCREEN_H // 2 - 60,
            ),
        )
        self.screen.blit(
            sub_surf,
            (
                self.SCREEN_W // 2 - sub_surf.get_width() // 2,
                self.SCREEN_H // 2,
            ),
        )

    def draw(self) -> None:
        # Background
        self.screen.fill((20, 24, 30))

        # Playfield
        pygame.draw.rect(self.screen, (10, 12, 16), self.playfield)
        pygame.draw.rect(self.screen, (76, 86, 106), self.playfield, width=2)

        # Goal
        pygame.draw.circle(
            self.screen,
            (163, 190, 140),
            (int(self.goal.pos.x), int(self.goal.pos.y)),
            self.goal.radius,
        )

        # Moving platforms
        for platform in self.platforms:
            pygame.draw.rect(self.screen, (200, 160, 100), platform.rect, border_radius=4)
            # Draw a border to show it's interactive
            pygame.draw.rect(self.screen, (220, 180, 120), platform.rect, width=2, border_radius=4)

        # Checkpoints
        for checkpoint in self.checkpoints:
            color = (200, 200, 100) if checkpoint.is_active else (100, 100, 60)
            pygame.draw.rect(self.screen, color, checkpoint.rect, border_radius=4)
            pygame.draw.rect(self.screen, (220, 220, 150), checkpoint.rect, width=2, border_radius=4)

        # Teleporter
        pygame.draw.rect(self.screen, (180, 142, 173), self.teleporter.rect, border_radius=6)

        # Player
        pygame.draw.rect(self.screen, (136, 192, 208), self.player_rect, border_radius=6)

        self._draw_hud()

        if self.state == "title":
            self._draw_center_message("Week 2", "Space: start   P: toggle control   Tab: bounds   Esc: quit")
        elif self.state == "win":
            self._draw_center_message("Level complete", "Space: next   P: toggle control   R: reset   Tab: bounds")
        elif self.state == "lose":
            self._draw_center_message("Time up", "Space: retry   R: reset   Tab: mode")


def main() -> None:
    pygame.init()
    clock = pygame.time.Clock()
    game = Game()

    pygame.display.set_caption("Week 2 Game - Moving Platforms & Checkpoints")

    while True:
        dt = clock.tick(game.fps) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            game.handle_event(event)

        game.update(dt)
        game.draw()
        pygame.display.flip()


if __name__ == "__main__":
    main()