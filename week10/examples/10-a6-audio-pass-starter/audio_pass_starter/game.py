from __future__ import annotations

from dataclasses import dataclass
import random

import pygame

import audio_pass_starter.audio as audio


BG        = pygame.Color("#11161d")
PANEL     = pygame.Color("#18222d")
PLAYFIELD = pygame.Color("#101a24")
TEXT      = pygame.Color("#ecf4ff")
SUBTLE    = pygame.Color("#9cb4c9")
ACCENT    = pygame.Color("#f5c96a")
PLAYER    = pygame.Color("#7dd3fc")
NODE      = pygame.Color("#6ee7b7")
HAZARD    = pygame.Color("#fb7185")
GOOD      = pygame.Color("#4ade80")
BAD       = pygame.Color("#ef4444")


@dataclass
class Player:
    pos: pygame.Vector2
    radius: int = 18
    speed: float = 280.0
    hp: int = 4
    invincible_for: float = 0.0
    scan_cooldown: float = 0.0
    scan_flash: float = 0.0

    def update(self, dt: float, playfield: pygame.Rect) -> None:
        if self.invincible_for > 0.0:
            self.invincible_for = max(0.0, self.invincible_for - dt)
        if self.scan_cooldown > 0.0:
            self.scan_cooldown = max(0.0, self.scan_cooldown - dt)
        if self.scan_flash > 0.0:
            self.scan_flash = max(0.0, self.scan_flash - dt)

        keys = pygame.key.get_pressed()
        axis = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: axis.x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: axis.x += 1
        if keys[pygame.K_UP]    or keys[pygame.K_w]: axis.y -= 1
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: axis.y += 1

        if axis.length_squared() > 0:
            axis = axis.normalize()

        self.pos += axis * self.speed * dt
        self.pos.x = max(playfield.left + self.radius, min(playfield.right  - self.radius, self.pos.x))
        self.pos.y = max(playfield.top  + self.radius, min(playfield.bottom - self.radius, self.pos.y))


@dataclass
class Node:
    pos: pygame.Vector2
    radius: int = 12


@dataclass
class Hazard:
    pos: pygame.Vector2
    velocity: pygame.Vector2
    radius: int = 16

    def update(self, dt: float, playfield: pygame.Rect) -> None:
        self.pos += self.velocity * dt

        if self.pos.x - self.radius <= playfield.left or self.pos.x + self.radius >= playfield.right:
            self.velocity.x *= -1
            self.pos.x = max(playfield.left + self.radius, min(playfield.right  - self.radius, self.pos.x))

        if self.pos.y - self.radius <= playfield.top or self.pos.y + self.radius >= playfield.bottom:
            self.velocity.y *= -1
            self.pos.y = max(playfield.top  + self.radius, min(playfield.bottom - self.radius, self.pos.y))


class TitleScene:
    name = "title"

    def __init__(self, game: Game) -> None:
        self.game = game

    def on_enter(self) -> None:
        audio.play_loop(self.game.sounds, "title_loop")

    def on_exit(self) -> None:
        return

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            audio.play(self.game.sounds, "start")
            self.game.switch_scene(PlayScene(self.game))

    def update(self, dt: float) -> None:
        return

    def draw(self) -> None:
        screen = self.game.screen
        screen.fill(BG)

        title = self.game.font(58).render("A6 Audio Pass Starter", True, TEXT)
        body  = self.game.font(28).render("Collect nodes, dodge hazards, scan on cooldown.", True, SUBTLE)
        hint  = self.game.font(28).render("Press Space to start", True, TEXT)
        mute  = self.game.font(22).render(self.game.audio_status_text(), True, SUBTLE)

        screen.blit(title, title.get_rect(center=(self.game.SCREEN_W // 2, 180)))
        screen.blit(body,  body.get_rect(center=(self.game.SCREEN_W // 2, 244)))
        screen.blit(hint,  hint.get_rect(center=(self.game.SCREEN_W // 2, 330)))
        screen.blit(mute,  mute.get_rect(center=(self.game.SCREEN_W // 2, 372)))


class EndScene:
    name = "end"

    def __init__(self, game: Game, *, won: bool, score: int) -> None:
        self.game  = game
        self.won   = won
        self.score = score

    def on_enter(self) -> None:
        audio.stop_loop()
        audio.play(self.game.sounds, "win" if self.won else "fail")

    def on_exit(self) -> None:
        return

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            audio.play(self.game.sounds, "start")
            self.game.switch_scene(PlayScene(self.game))

    def update(self, dt: float) -> None:
        return

    def draw(self) -> None:
        screen = self.game.screen
        screen.fill(BG)

        heading = "Signal Restored" if self.won else "Signal Lost"
        accent  = GOOD if self.won else BAD

        title = self.game.font(60).render(heading, True, TEXT)
        score = self.game.font(32).render(f"Score: {self.score}", True, accent)
        hint  = self.game.font(28).render("Press Space to restart", True, SUBTLE)

        screen.blit(title, title.get_rect(center=(self.game.SCREEN_W // 2, 180)))
        screen.blit(score, score.get_rect(center=(self.game.SCREEN_W // 2, 246)))
        screen.blit(hint,  hint.get_rect(center=(self.game.SCREEN_W // 2, 340)))


class PlayScene:
    name         = "play"
    TARGET_SCORE = 6

    def __init__(self, game: Game) -> None:
        self.game         = game
        self.player       = Player(pos=pygame.Vector2(self.game.playfield.center))
        self.nodes        = [Node(self._random_point(40)) for _ in range(4)]
        self.hazards      = [Hazard(self._random_point(70), self._random_velocity()) for _ in range(3)]
        self.score        = 0
        self.banner       = "Collect all nodes to win. Space to scan. M to mute."
        self.banner_for   = 2.5
        self.scan_hint_for= 0.0

    def on_enter(self) -> None:
        audio.play_loop(self.game.sounds, "play_loop")

    def on_exit(self) -> None:
        return

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_SPACE and self.player.scan_cooldown <= 0.0:
            self.player.scan_cooldown  = 0.45
            self.player.scan_flash     = 0.30
            self.scan_hint_for         = 0.45
            self.banner                = "Scan pulse fired."
            self.banner_for            = 0.9
            audio.play(self.game.sounds, "scan")

    def update(self, dt: float) -> None:
        self.player.update(dt, self.game.playfield)

        if self.banner_for    > 0.0: self.banner_for    = max(0.0, self.banner_for    - dt)
        if self.scan_hint_for > 0.0: self.scan_hint_for = max(0.0, self.scan_hint_for - dt)

        for hazard in self.hazards:
            hazard.update(dt, self.game.playfield)

        for node in self.nodes:
            if self._overlap(self.player.pos, self.player.radius, node.pos, node.radius):
                self.score     += 1
                node.pos        = self._random_point(40)
                self.banner     = f"Node collected! ({self.score}/{self.TARGET_SCORE})"
                self.banner_for = 0.9
                audio.play(self.game.sounds, "pickup")

        for hazard in self.hazards:
            if self.player.invincible_for > 0.0:
                break
            if self._overlap(self.player.pos, self.player.radius, hazard.pos, hazard.radius):
                self.player.hp             = max(0, self.player.hp - 1)
                self.player.invincible_for = 1.0
                self.banner                = f"Hit! HP remaining: {self.player.hp}"
                self.banner_for            = 0.9
                audio.play(self.game.sounds, "damage")

        if self.score >= self.TARGET_SCORE:
            self.game.switch_scene(EndScene(self.game, won=True,  score=self.score))
            return
        if self.player.hp <= 0:
            self.game.switch_scene(EndScene(self.game, won=False, score=self.score))

    def draw(self) -> None:
        screen = self.game.screen
        screen.fill(BG)

        pygame.draw.rect(screen, PANEL,     self.game.hud_rect)
        pygame.draw.rect(screen, PLAYFIELD, self.game.playfield, border_radius=14)

        for node in self.nodes:
            pygame.draw.circle(screen, NODE, node.pos, node.radius)
            pygame.draw.circle(screen, TEXT, node.pos, node.radius, width=2)

        for hazard in self.hazards:
            pygame.draw.circle(screen, HAZARD, hazard.pos, hazard.radius)

        if self.scan_hint_for > 0.0:
            nearest = self._nearest_node()
            if nearest is not None:
                pygame.draw.line(screen, ACCENT, self.player.pos, nearest.pos, width=3)

        self._draw_player(screen)
        self._draw_scan_ring(screen)
        self._draw_hud(screen)

    def _draw_player(self, screen: pygame.Surface) -> None:
        visible = self.player.invincible_for <= 0.0 or int(self.player.invincible_for * 12) % 2 == 0
        if visible:
            pygame.draw.circle(screen, PLAYER, self.player.pos, self.player.radius)
            pygame.draw.circle(screen, TEXT,   self.player.pos, self.player.radius, width=2)

    def _draw_scan_ring(self, screen: pygame.Surface) -> None:
        if self.player.scan_flash <= 0.0:
            return
        progress = 1.0 - self.player.scan_flash / 0.30
        pygame.draw.circle(screen, ACCENT, self.player.pos,
                           int(28 + progress * 120), width=max(1, int(5 - progress * 3)))

    def _draw_hud(self, screen: pygame.Surface) -> None:
        cy   = self.game.hud_rect.centery
        left = self.game.hud_rect.left + 16
        cd   = max(0.0, self.player.scan_cooldown)

        score    = self.game.font(26).render(f"Score: {self.score}/{self.TARGET_SCORE}", True, TEXT)
        hp       = self.game.font(26).render(f"HP: {self.player.hp}", True, GOOD if self.player.hp >= 2 else BAD)
        cooldown = self.game.font(22).render(f"Scan cooldown: {cd:.2f}s", True, SUBTLE)
        audio_lbl= self.game.font(22).render(self.game.audio_status_text(), True, ACCENT)

        screen.blit(score,     score.get_rect(midleft=(left, cy)))
        screen.blit(hp,        hp.get_rect(midleft=(left + 180, cy)))
        screen.blit(cooldown,  cooldown.get_rect(midleft=(left + 280, cy)))
        screen.blit(audio_lbl, audio_lbl.get_rect(midright=(self.game.hud_rect.right - 16, cy)))

        cx      = self.game.playfield.centerx
        help_t  = self.game.font(20).render("Move: WASD / arrows  |  Scan: Space  |  Mute: M", True, SUBTLE)
        banner  = self.banner if self.banner_for > 0.0 else "Collect all nodes to win!"
        todo_t  = self.game.font(21).render(banner, True, ACCENT)

        screen.blit(help_t, help_t.get_rect(midtop=(cx, self.game.playfield.top    + 14)))
        screen.blit(todo_t, todo_t.get_rect(midbottom=(cx, self.game.playfield.bottom - 16)))

    def _nearest_node(self) -> Node | None:
        if not self.nodes:
            return None
        return min(self.nodes, key=lambda n: self.player.pos.distance_squared_to(n.pos))

    def _random_point(self, margin: int) -> pygame.Vector2:
        pf = self.game.playfield
        return pygame.Vector2(
            self.game.rng.uniform(pf.left + margin, pf.right  - margin),
            self.game.rng.uniform(pf.top  + margin, pf.bottom - margin))

    def _random_velocity(self) -> pygame.Vector2:
        c = (-170.0, -140.0, 140.0, 170.0)
        return pygame.Vector2(self.game.rng.choice(c), self.game.rng.choice(c))

    @staticmethod
    def _overlap(ap: pygame.Vector2, ar: int, bp: pygame.Vector2, br: int) -> bool:
        lim = ar + br
        return ap.distance_squared_to(bp) <= lim * lim


class Game:
    fps      = 60
    SCREEN_W = 960
    SCREEN_H = 540
    HUD_H    = 66
    PADDING  = 14

    def __init__(self) -> None:
        self.screen    = pygame.display.set_mode((self.SCREEN_W, self.SCREEN_H))
        self._fonts: dict[int, pygame.font.Font] = {}
        self.rng       = random.Random(8)

        self.hud_rect  = pygame.Rect(0, 0, self.SCREEN_W, self.HUD_H)
        self.playfield = pygame.Rect(
            self.PADDING, self.HUD_H + self.PADDING,
            self.SCREEN_W - 2 * self.PADDING,
            self.SCREEN_H - self.HUD_H - 2 * self.PADDING)

        self.audio_ok = audio.init_audio()
        self.sounds   = audio.build_sounds() if self.audio_ok else {}

        self.current_scene: TitleScene | PlayScene | EndScene = TitleScene(self)
        self.current_scene.on_enter()

    def font(self, size: int) -> pygame.font.Font:
        size = int(size)
        if size not in self._fonts:
            self._fonts[size] = pygame.font.SysFont(None, size)
        return self._fonts[size]

    def audio_status_text(self) -> str:
        if not self.audio_ok:    return "Audio unavailable"
        if audio._muted:         return "Audio muted (M)"
        return "Audio on (M to mute)"

    def switch_scene(self, scene: TitleScene | PlayScene | EndScene) -> None:
        self.current_scene.on_exit()
        self.current_scene = scene
        self.current_scene.on_enter()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
                return
            if event.key == pygame.K_m:
                audio.toggle_mute(self.sounds)
                return
        self.current_scene.handle_event(event)

    def update(self, dt: float) -> None: self.current_scene.update(dt)
    def draw(self)           -> None: self.current_scene.draw()
    def shutdown(self)       -> None: audio.stop_loop()