from __future__ import annotations

import random

import pygame

from audio_feedback.audio import AudioBank
from audio_feedback.entities import Bounds, Mob, Player, Projectile
from audio_feedback.palette import Palette
from audio_feedback.scene import Scene, SceneManager


class TitleScene:
    name = "title"

    def __init__(self, game: Game) -> None:
        self.game = game

    def on_enter(self) -> None:
        self.game.audio.play_loop("title_loop")

    def on_exit(self) -> None:
        return

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_SPACE:
            self.game.audio.play("ui_confirm")
            self.game.audio.play("start")
            self.game.scenes.switch_to(PlayScene(self.game))

    def update(self, dt: float) -> None:
        return

    def draw(self) -> None:
        screen = self.game.screen
        pal = self.game.palette
        screen.fill(pal.bg)

        title = self.game.font(54).render("Week 10: Audio + Feedback", True, pal.text)
        hint = self.game.font(28).render("Press Space to start", True, pal.subtle)
        mute = self.game.font(22).render(self.game.audio_status_text(), True, pal.accent)
        body = self.game.font(26).render("Audio should confirm action, danger, and state change.", True, pal.subtle)

        screen.blit(title, title.get_rect(center=(self.game.SCREEN_W // 2, 180)))
        screen.blit(body, body.get_rect(center=(self.game.SCREEN_W // 2, 248)))
        screen.blit(hint, hint.get_rect(center=(self.game.SCREEN_W // 2, 318)))
        screen.blit(mute, mute.get_rect(center=(self.game.SCREEN_W // 2, 360)))


class GameOverScene:
    name = "gameover"

    def __init__(self, game: Game, *, score: int) -> None:
        self.game = game
        self.score = score

    def on_enter(self) -> None:
        self.game.audio.stop_loop()
        self.game.audio.play("gameover")

    def on_exit(self) -> None:
        return

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_SPACE:
            self.game.audio.play("ui_confirm")
            self.game.audio.play("start")
            self.game.scenes.switch_to(PlayScene(self.game))

    def update(self, dt: float) -> None:
        return

    def draw(self) -> None:
        screen = self.game.screen
        pal = self.game.palette
        screen.fill(pal.bg)

        title = self.game.font(72).render("GAME OVER", True, pal.text)
        score = self.game.font(32).render(f"Score: {self.score}", True, pal.warn)
        hint = self.game.font(28).render("Press Space to restart", True, pal.subtle)
        mute = self.game.font(22).render(self.game.audio_status_text(), True, pal.accent)

        screen.blit(title, title.get_rect(center=(self.game.SCREEN_W // 2, 190)))
        screen.blit(score, score.get_rect(center=(self.game.SCREEN_W // 2, 275)))
        screen.blit(hint, hint.get_rect(center=(self.game.SCREEN_W // 2, 340)))
        screen.blit(mute, mute.get_rect(center=(self.game.SCREEN_W // 2, 380)))


class PlayScene:
    name = "play"
    MOB_COUNT = 9

    def __init__(self, game: Game) -> None:
        self.game = game
        self.score = 0
        self.warn_for = 0.0

        self.all_sprites: pygame.sprite.Group[pygame.sprite.Sprite] = pygame.sprite.Group()
        self.mobs: pygame.sprite.Group[Mob] = pygame.sprite.Group()
        self.projectiles: pygame.sprite.Group[Projectile] = pygame.sprite.Group()

        bounds = Bounds(self.game.playfield.copy())
        self.player = Player(self.game.playfield.midbottom, color=self.game.palette.player, bounds=bounds)
        self.player.rect.y -= 18
        self.player.pos.xy = self.player.rect.center
        self.all_sprites.add(self.player)

        for _ in range(self.MOB_COUNT):
            mob = Mob(color=self.game.palette.mob, playfield=self.game.playfield, rng=self.game.rng)
            self.mobs.add(mob)
            self.all_sprites.add(mob)

    def on_enter(self) -> None:
        self.game.audio.play_loop("play_loop")

    def on_exit(self) -> None:
        self.game.audio.stop_loop()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_SPACE and self.player.can_fire():
            self.player.mark_fired()
            projectile = Projectile(
                self.player.rect.centerx,
                self.player.rect.top,
                color=self.game.palette.projectile,
                top_limit=self.game.playfield.top - 40,
            )
            self.projectiles.add(projectile)
            self.all_sprites.add(projectile)
            self.game.audio.play("fire")

    def update(self, dt: float) -> None:
        self.player.update(dt)
        self.mobs.update(dt)
        self.projectiles.update(dt)

        if self.warn_for > 0.0:
            self.warn_for = max(0.0, self.warn_for - dt)

        hits = pygame.sprite.groupcollide(self.projectiles, self.mobs, dokilla=True, dokillb=False)
        if hits:
            self.game.audio.play("hit")
            for mobs in hits.values():
                for mob in mobs:
                    mob.respawn()
                    self.score += 1

        bump = pygame.sprite.spritecollide(self.player, self.mobs, dokill=False)
        if bump:
            took_damage = self.player.take_hit(1)
            for mob in bump:
                mob.respawn()
            if took_damage:
                self.game.audio.play("hurt")

        if self.player.hp <= 2 and self.warn_for <= 0.0 and self.player.hp > 0:
            self.game.audio.play("warn")
            self.warn_for = 1.1

        if self.player.hp <= 0:
            self.game.scenes.switch_to(GameOverScene(self.game, score=self.score))

    def draw(self) -> None:
        screen = self.game.screen
        pal = self.game.palette

        screen.fill(pal.bg)

        pygame.draw.rect(screen, pal.panel, self.game.hud_rect)
        pygame.draw.rect(screen, pal.panel, self.game.playfield, border_radius=12)

        self.all_sprites.draw(screen)
        self._draw_hud()

    def _draw_hud(self) -> None:
        screen = self.game.screen
        pal = self.game.palette
        cy = self.game.hud_rect.centery
        left = self.game.hud_rect.left + 14

        score = self.game.font(28).render(f"Score: {self.score}", True, pal.text)
        scene = self.game.font(22).render("Scene: play", True, pal.subtle)
        audio = self.game.font(22).render(self.game.audio_status_text(), True, pal.accent)
        help_text = self.game.font(20).render("Space fire | M mute | Esc quit", True, pal.subtle)

        screen.blit(score, score.get_rect(midleft=(left, cy)))
        screen.blit(scene, scene.get_rect(midleft=(left + 170, cy)))
        screen.blit(audio, audio.get_rect(midleft=(left + 310, cy)))
        screen.blit(help_text, help_text.get_rect(midright=(self.game.hud_rect.right - 14, cy)))

        bar_w = 160
        bar_h = 16
        bar_x = self.game.playfield.right - bar_w - 18
        bar_y = self.game.playfield.top + 18

        pygame.draw.rect(screen, pal.bg, pygame.Rect(bar_x, bar_y, bar_w, bar_h), border_radius=5)
        pct = self.player.hp / self.player.max_hp
        fill_w = max(0, int(round(bar_w * pct)))
        fill_col = pal.ok if pct >= 0.4 else pal.bad
        pygame.draw.rect(screen, fill_col, pygame.Rect(bar_x, bar_y, fill_w, bar_h), border_radius=5)

        hp = self.game.font(22).render(f"HP {self.player.hp}/{self.player.max_hp}", True, pal.text)
        screen.blit(hp, hp.get_rect(midright=(bar_x - 10, bar_y + bar_h // 2)))

        tip = self.game.font(22).render("Audio map: start, fire, hit, hurt, warn, game over", True, pal.subtle)
        screen.blit(tip, tip.get_rect(midbottom=(self.game.playfield.centerx, self.game.playfield.bottom - 16)))


class Game:
    fps = 60

    SCREEN_W, SCREEN_H = 960, 540
    HUD_H = 64
    PADDING = 14

    def __init__(self) -> None:
        self.palette = Palette()
        self.screen = pygame.display.set_mode((self.SCREEN_W, self.SCREEN_H))
        self._fonts: dict[int, pygame.font.Font] = {}
        self._quit_delay = 0.0

        self.hud_rect = pygame.Rect(0, 0, self.SCREEN_W, self.HUD_H)
        self.playfield = pygame.Rect(
            self.PADDING,
            self.HUD_H + self.PADDING,
            self.SCREEN_W - 2 * self.PADDING,
            self.SCREEN_H - self.HUD_H - 2 * self.PADDING,
        )

        self.rng = random.Random(8)
        self.audio = AudioBank()

        start: Scene = TitleScene(self)
        self.scenes = SceneManager(current=start)
        self.scenes.enter_current()

    def font(self, size: int) -> pygame.font.Font:
        size = int(size)
        found = self._fonts.get(size)
        if found is None:
            found = pygame.font.SysFont(None, size)
            self._fonts[size] = found
        return found

    def audio_status_text(self) -> str:
        if not self.audio.enabled:
            return "Audio: unavailable (silent fallback)"
        if self.audio.muted:
            return "Audio: muted (press M)"
        return "Audio: on (press M to mute)"

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self._quit_delay <= 0.0:
                    self.audio.play("ui_cancel")
                    self._quit_delay = 0.12
                return
            if event.key == pygame.K_m:
                self.audio.toggle_mute()
                return

        if self._quit_delay > 0.0:
            return

        self.scenes.current.handle_event(event)

    def update(self, dt: float) -> None:
        if self._quit_delay > 0.0:
            self._quit_delay = max(0.0, self._quit_delay - dt)
            if self._quit_delay == 0.0:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            return

        self.scenes.current.update(dt)

    def draw(self) -> None:
        self.scenes.current.draw()

    def shutdown(self) -> None:
        self.audio.shutdown()