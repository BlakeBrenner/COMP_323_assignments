from __future__ import annotations

from dataclasses import dataclass, field

import pygame


@dataclass(frozen=True)
class Palette:
    bg: pygame.Color = field(default_factory=lambda: pygame.Color("#171b22"))
    panel: pygame.Color = field(default_factory=lambda: pygame.Color("#252b35"))
    text: pygame.Color = field(default_factory=lambda: pygame.Color("#edf2f7"))
    subtle: pygame.Color = field(default_factory=lambda: pygame.Color("#97a3b6"))

    player: pygame.Color = field(default_factory=lambda: pygame.Color("#7dd3fc"))
    mob: pygame.Color = field(default_factory=lambda: pygame.Color("#f87171"))
    projectile: pygame.Color = field(default_factory=lambda: pygame.Color("#fde68a"))

    accent: pygame.Color = field(default_factory=lambda: pygame.Color("#86efac"))
    warn: pygame.Color = field(default_factory=lambda: pygame.Color("#fca5a5"))
    ok: pygame.Color = field(default_factory=lambda: pygame.Color("#22c55e"))
    bad: pygame.Color = field(default_factory=lambda: pygame.Color("#b91c1c"))