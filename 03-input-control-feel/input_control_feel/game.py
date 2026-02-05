from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import pygame

# ---- Key bindings ----
MOVE_LEFT  = pygame.K_a
MOVE_RIGHT = pygame.K_d
MOVE_UP    = pygame.K_w
MOVE_DOWN  = pygame.K_s

ARROW_LEFT  = pygame.K_LEFT
ARROW_RIGHT = pygame.K_RIGHT
ARROW_UP    = pygame.K_UP
ARROW_DOWN  = pygame.K_DOWN

JUMP_KEY = pygame.K_SPACE
DASH_KEYS = {pygame.K_LSHIFT, pygame.K_RSHIFT}

class BoundaryMode(str, Enum):
    CLAMP = "clamp"
    WRAP = "wrap"
    BOUNCE = "bounce"


class ControlScheme(str, Enum):
    WASD = "WASD"
    ARROWS = "ARROWS"
    IJKL = "IJKL"

class InputMapping(str, Enum):
    MOVE_LEFT = "left"

@dataclass(frozen=True)
class FeelPreset:
    name: str

    # Top-down feel
    accel: float
    max_speed: float
    friction: float

    # Platformer feel
    gravity: float
    jump_speed: float


class Game:
    fps = 60

    SCREEN_W, SCREEN_H = 960, 540
    HUD_H = 54
    PLAYFIELD_PADDING = 10

    PLAYER_SIZE = 32

    DASH_IMPULSE = 5000
    DASH_COOLDOWN = 0.65

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
        self.state = "title"  # title | play

        self.player_rect = pygame.Rect(0, 0, self.PLAYER_SIZE, self.PLAYER_SIZE)
        self.player_pos = pygame.Vector2(self.playfield.center)
        self.player_vel = pygame.Vector2(0, 0)
        self.player_rect.center = self.player_pos

        self.on_ground = True
        self.jump_requested = False
        self.jump_held = False
        self.jumps_left = 2  # double jump counter

        self.control_scheme = ControlScheme.WASD
        self.debug = False

        self.presets = [
            FeelPreset(
                name="tight",
                accel=3200.0,
                max_speed=520.0,
                friction=14.0,
                gravity=2600.0,
                jump_speed=860.0,
            ),
            FeelPreset(
                name="floaty",
                accel=1900.0,
                max_speed=560.0,
                friction=6.0,
                gravity=1700.0,
                jump_speed=760.0,
            ),
            FeelPreset(
                name="heavy",
                accel=1400.0,
                max_speed=440.0,
                friction=4.2,
                gravity=3200.0,
                jump_speed=820.0,
            ),
            #fast but slippery
            FeelPreset(
                name="slick",
                accel=5200.0, #quick acceleration
                max_speed=900.0, #high top speed
                friction=2.0,  #slides a lot
                gravity=2600.0,
                jump_speed=880.0,
            ),
            #low gravity extreme float
            FeelPreset(
                name="moon",
                accel=1400.0,
                max_speed=480.0,
                friction=4.0,
                gravity=600.0,  # super low gravity
                jump_speed=1200.0,  # huge jumps
            )
        ]
        self.preset_idx = 0

        self.dash_cooldown_left = 0.0
        self.last_move_dir = pygame.Vector2(1, 0)

    @property
    def preset(self) -> FeelPreset:
        return self.presets[self.preset_idx]

    def _cycle_boundary_mode(self) -> None:
        modes = list(BoundaryMode)
        idx = modes.index(self.boundary_mode)
        self.boundary_mode = modes[(idx + 1) % len(modes)]

    def _cycle_control_scheme(self) -> None:
        schemes = list(ControlScheme)
        idx = schemes.index(self.control_scheme)
        self.control_scheme = schemes[(idx + 1) % len(schemes)]

    def _reset(self, keep_state: bool = False) -> None:
        self.player_pos = pygame.Vector2(self.playfield.center)
        self.player_vel = pygame.Vector2(0, 0)
        self.player_rect.center = self.player_pos
        self.on_ground = True
        self.jump_requested = False
        self.dash_cooldown_left = 0.0
        self.last_move_dir = pygame.Vector2(1, 0)

        if not keep_state:
            self.state = "play"

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type not in {pygame.KEYDOWN, pygame.KEYUP} :
            return
        if event.type == pygame.KEYUP :
            if event.key in {MOVE_UP, ARROW_UP, JUMP_KEY}:
                self.jump_held = False
            return

        if event.key == pygame.K_ESCAPE:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            return

        if event.key == pygame.K_F1:
            self.debug = not self.debug
            return

        if event.key == pygame.K_TAB:
            self._cycle_boundary_mode()
            return

        if event.key == pygame.K_c:
            self._cycle_control_scheme()
            return

        if event.key == pygame.K_p:
            self.platformer_mode = not self.platformer_mode
            if self.state != "title":
                self._reset(keep_state=True)
            return

        if event.key == pygame.K_r:
            self._reset(keep_state=(self.state == "title"))
            return

        if self.state == "title" and event.key == pygame.K_SPACE:
            self.state = "play"
            self._reset(keep_state=True)
            return

        if event.key == pygame.K_1:
            self.preset_idx = 0
            return
        if event.key == pygame.K_2:
            self.preset_idx = 1
            return
        if event.key == pygame.K_3:
            self.preset_idx = 2
            return
        if event.key == pygame.K_4:
            self.preset_idx = 3
        if event.key == pygame.K_5:
            self.preset_idx = 4

        if self.state != "play":
            return

        # Discrete actions
        if event.key in DASH_KEYS:
            self._try_dash()
            return

        if self.platformer_mode and event.key in {MOVE_UP, ARROW_UP, JUMP_KEY}:
            self.jump_requested = True
            self.jump_held = True

    def _scheme_keys(self) -> dict[str, set[int]]:
        if self.control_scheme == ControlScheme.WASD:
            return {
                "left":  {MOVE_LEFT},
                "right": {MOVE_RIGHT},
                "up":    {MOVE_UP},
                "down":  {MOVE_DOWN},
            }
        if self.control_scheme == ControlScheme.IJKL:
            return {
                "left": {pygame.K_j},
                "right": {pygame.K_l},
                "up": {pygame.K_i},
                "down": {pygame.K_k},
            }
        return {
            "left":  {ARROW_LEFT},
            "right": {ARROW_RIGHT},
            "up":    {ARROW_UP},
            "down":  {ARROW_DOWN},
        }

    def _read_direction(self) -> pygame.Vector2:
        keys = pygame.key.get_pressed()
        mapping = self._scheme_keys()

        x = 0
        y = 0

        if any(keys[k] for k in mapping["left"]):
            x -= 1
        if any(keys[k] for k in mapping["right"]):
            x += 1
        if any(keys[k] for k in mapping["up"]):
            y -= 1
        if any(keys[k] for k in mapping["down"]):
            y += 1

        direction = pygame.Vector2(x, y)
        if direction.length_squared() > 0:
            direction = direction.normalize()
            self.last_move_dir.update(direction)

        # Always allow arrows as an alternate scheme (accessibility / convenience)
        if direction.length_squared() == 0:
            x2 = 0
            y2 = 0
            if keys[ARROW_LEFT]:
                x2 -= 1
            if keys[ARROW_RIGHT]:
                x2 += 1
            if keys[ARROW_UP]:
                y2 -= 1
            if keys[ARROW_DOWN]:
                y2 += 1
            direction2 = pygame.Vector2(x2, y2)
            if direction2.length_squared() > 0:
                direction2 = direction2.normalize()
                self.last_move_dir.update(direction2)
                return direction2

        return direction

    def _read_horizontal(self) -> float:
        keys = pygame.key.get_pressed()
        mapping = self._scheme_keys()

        x = 0
        if any(keys[k] for k in mapping["left"]) or keys[pygame.K_LEFT]:
            x -= 1
        if any(keys[k] for k in mapping["right"]) or keys[pygame.K_RIGHT]:
            x += 1

        if x != 0:
            self.last_move_dir.update(pygame.Vector2(x, 0).normalize())

        return float(x)

    def _apply_platformer_vertical_bounds(self) -> None:
        # Treat the bottom of the playfield as "ground".
        if self.player_rect.bottom >= self.playfield.bottom:
            self.player_rect.bottom = self.playfield.bottom
            self.player_vel.y = 0
            self.on_ground = True
            self.jumps_left = 2

        # Prevent leaving the top of the playfield.
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

    def _try_dash(self) -> None:
        if self.dash_cooldown_left > 0:
            return

        dash_dir = pygame.Vector2(self.last_move_dir)
        if dash_dir.length_squared() == 0:
            dash_dir = pygame.Vector2(1, 0)
        dash_dir = dash_dir.normalize()

        # Impulse dash: a discrete action that modifies velocity once.
        self.player_vel += dash_dir * self.DASH_IMPULSE
        self.dash_cooldown_left = self.DASH_COOLDOWN

    def update(self, dt: float) -> None:
        if self.state != "play":
            return

        if self.dash_cooldown_left > 0:
            self.dash_cooldown_left = max(0.0, self.dash_cooldown_left - dt)

        p = self.preset

        if self.platformer_mode:
            x = self._read_horizontal()

            # Horizontal accel; no vertical input (gravity handles Y).
            self.player_vel.x += x * p.accel * dt
            if x == 0:
                self.player_vel.x -= self.player_vel.x * min(1.0, p.friction * dt)
            self.player_vel.x = max(-p.max_speed, min(p.max_speed, self.player_vel.x))

            # Jump can be held
            should_jump = False
            if self.jump_requested == True:
                should_jump = True
            elif self.jump_held and self.player_vel.y > 0:
                should_jump = True
            if should_jump and self.jumps_left > 0:
                self.player_vel.y = -p.jump_speed
                self.on_ground = False
                self.jumps_left -= 1
                self.jump_requested = False
            self.jump_requested = False

            # Gravity.
            self.player_vel.y += p.gravity * dt

            self.player_pos += self.player_vel * dt
            self.player_rect.center = (int(self.player_pos.x), int(self.player_pos.y))

            # Use the existing boundary mode for horizontal bounds.
            prev_y = self.player_rect.centery
            self._apply_bounds_player()
            self.player_rect.centery = prev_y
            self.player_pos.y = prev_y

            # Then apply platformer-specific vertical bounds.
            self._apply_platformer_vertical_bounds()
        else:
            direction = self._read_direction()

            # Accelerate toward direction.
            self.player_vel += direction * p.accel * dt

            # Friction: nudge velocity toward zero when no input.
            if direction.length_squared() == 0:
                self.player_vel -= self.player_vel * min(1.0, p.friction * dt)

            if self.player_vel.length() > p.max_speed:
                self.player_vel.scale_to_length(p.max_speed)

            self.player_pos += self.player_vel * dt
            self.player_rect.center = (int(self.player_pos.x), int(self.player_pos.y))

            self._apply_bounds_player()

    def _draw_hud(self) -> None:
        pygame.draw.rect(self.screen, (46, 52, 64), pygame.Rect(0, 0, self.SCREEN_W, self.HUD_H))

        control = "PLATFORMER" if self.platformer_mode else "TOPDOWN"
        left = (
            f"Bounds: {self.boundary_mode.value.upper()}   Control: {control}   "
            f"Scheme: {self.control_scheme.value}   Feel: {self.preset.name}"
        )

        dash = "READY" if self.dash_cooldown_left <= 0 else f"CD {self.dash_cooldown_left:0.2f}s"
        right = f"Dash: {dash}"

        left_surf = self.font.render(left, True, (216, 222, 233))
        right_surf = self.font.render(right, True, (216, 222, 233))

        self.screen.blit(left_surf, (14, 16))
        self.screen.blit(right_surf, (self.SCREEN_W - right_surf.get_width() - 14, 16))

        #display feedback for double jump
        if self.platformer_mode:
            jump_text = f"Jumps: {self.jumps_left}"
            jump_surf = self.font.render(jump_text, True, (216, 222, 233))

            # top-right corner under dash
            self.screen.blit(
                jump_surf,
                (self.SCREEN_W - jump_surf.get_width() - 14, 34)
            )

    def _draw_debug(self) -> None:
        p = self.preset
        lines = [
            f"vel=({self.player_vel.x:0.1f}, {self.player_vel.y:0.1f})",
            f"accel={p.accel:0.1f}  friction={p.friction:0.1f}  max={p.max_speed:0.1f}",
            f"gravity={p.gravity:0.1f}  jump={p.jump_speed:0.1f}",
            f"last_dir=({self.last_move_dir.x:0.2f},{self.last_move_dir.y:0.2f})",
        ]

        x = 14
        y = self.HUD_H + 10
        for line in lines:
            surf = self.font.render(line, True, (229, 233, 240))
            self.screen.blit(surf, (x, y))
            y += 18

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
        self.screen.fill((20, 24, 30))

        # Playfield
        pygame.draw.rect(self.screen, (10, 12, 16), self.playfield)
        pygame.draw.rect(self.screen, (76, 86, 106), self.playfield, width=2)

        # Player
        pygame.draw.rect(self.screen, (136, 192, 208), self.player_rect, border_radius=6)

        self._draw_hud()

        if self.debug:
            self._draw_debug()

        if self.state == "title":
            self._draw_center_message(
                "Week 3",
                "Space: start   Shift: dash   1/2/3/4/5: feel   C: scheme   P: mode   F1: debug",
            )
