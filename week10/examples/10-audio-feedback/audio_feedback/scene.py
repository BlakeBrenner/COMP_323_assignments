from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pygame


class Scene(Protocol):
    name: str

    def on_enter(self) -> None: ...

    def on_exit(self) -> None: ...

    def handle_event(self, event: pygame.event.Event) -> None: ...

    def update(self, dt: float) -> None: ...

    def draw(self) -> None: ...


@dataclass
class SceneManager:
    current: Scene

    def enter_current(self) -> None:
        self.current.on_enter()

    def switch_to(self, scene: Scene) -> None:
        self.current.on_exit()
        self.current = scene
        self.current.on_enter()