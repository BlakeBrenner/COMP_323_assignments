from __future__ import annotations

from array import array
import math

import pygame


class AudioBank:
    def __init__(self) -> None:
        self.enabled = False
        self.muted = False

        self.music_volume = 0.14
        self.sfx_volume = 0.34
        self.ui_volume = 0.28

        self._sounds: dict[str, pygame.mixer.Sound] = {}
        self._loop_channel: pygame.mixer.Channel | None = None
        self._ui_channel: pygame.mixer.Channel | None = None
        self._warning_channel: pygame.mixer.Channel | None = None

        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=256)

            pygame.mixer.set_num_channels(8)
            pygame.mixer.set_reserved(3)
            self._loop_channel = pygame.mixer.Channel(0)
            self._ui_channel = pygame.mixer.Channel(1)
            self._warning_channel = pygame.mixer.Channel(2)
            self.enabled = True
            self._build_sounds()
            self._apply_volumes()
        except pygame.error:
            self.enabled = False

    def _build_sounds(self) -> None:
        self._sounds = {
            "start": self._make_tone(523.25, 120, 0.9, wave="sine"),
            "ui_confirm": self._make_tone(740.0, 70, 0.45, wave="triangle"),
            "ui_cancel": self._make_tone(293.66, 95, 0.45, wave="saw"),
            "fire": self._make_tone(880.0, 55, 0.6, wave="square"),
            "hit": self._make_tone(659.25, 80, 0.55, wave="triangle"),
            "hurt": self._make_tone(220.0, 140, 0.65, wave="saw"),
            "warn": self._make_tone(329.63, 180, 0.6, wave="square"),
            "gameover": self._make_tone(164.81, 260, 0.75, wave="sine"),
            "title_loop": self._make_tone(196.0, 700, 0.18, wave="sine"),
            "play_loop": self._make_tone(246.94, 480, 0.14, wave="triangle"),
        }

    def _make_tone(self, frequency: float, duration_ms: int, volume: float, *, wave: str) -> pygame.mixer.Sound:
        init = pygame.mixer.get_init()
        if init is None:
            raise pygame.error("Mixer not initialized")

        sample_rate, _fmt, channels = init
        sample_count = max(1, int(sample_rate * duration_ms / 1000))
        fade_len = max(1, min(sample_count // 8, int(sample_rate * 0.02)))
        max_amp = int(32767 * max(0.0, min(1.0, volume)))

        buf = array("h")
        for index in range(sample_count):
            phase = (index / sample_rate) * frequency
            frac = phase - math.floor(phase)

            if wave == "square":
                sample = 1.0 if frac < 0.5 else -1.0
            elif wave == "triangle":
                sample = 4.0 * abs(frac - 0.5) - 1.0
            elif wave == "saw":
                sample = 2.0 * frac - 1.0
            else:
                sample = math.sin(2.0 * math.pi * phase)

            envelope = 1.0
            if index < fade_len:
                envelope *= index / fade_len
            if index >= sample_count - fade_len:
                envelope *= (sample_count - index - 1) / fade_len

            amp = int(sample * envelope * max_amp)
            if channels == 2:
                buf.append(amp)
                buf.append(amp)
            else:
                buf.append(amp)

        return pygame.mixer.Sound(buffer=buf.tobytes())

    def _apply_volumes(self) -> None:
        if not self.enabled:
            return

        if self._loop_channel is not None:
            self._loop_channel.set_volume(0.0 if self.muted else self.music_volume)
        if self._ui_channel is not None:
            self._ui_channel.set_volume(0.0 if self.muted else self.ui_volume)
        if self._warning_channel is not None:
            self._warning_channel.set_volume(0.0 if self.muted else self.sfx_volume)

        for key, sound in self._sounds.items():
            if key.endswith("_loop"):
                base = self.music_volume
            elif key.startswith("ui_"):
                base = self.ui_volume
            else:
                base = self.sfx_volume
            sound.set_volume(0.0 if self.muted else base)

    def toggle_mute(self) -> None:
        self.muted = not self.muted
        self._apply_volumes()

    def play(self, name: str) -> None:
        if not self.enabled or self.muted:
            return

        sound = self._sounds.get(name)
        if sound is None:
            return

        if name.startswith("ui_") and self._ui_channel is not None:
            self._ui_channel.play(sound)
            return

        if name == "warn" and self._warning_channel is not None:
            if self._warning_channel.get_busy():
                return
            self._warning_channel.play(sound)
            return

        sound.play()

    def play_loop(self, name: str) -> None:
        if not self.enabled or self._loop_channel is None:
            return

        sound = self._sounds.get(name)
        if sound is None:
            return

        if self._loop_channel.get_sound() is sound:
            return

        self._loop_channel.stop()
        self._loop_channel.play(sound, loops=-1)
        self._apply_volumes()

    def stop_loop(self) -> None:
        if self._loop_channel is not None:
            self._loop_channel.stop()

    def shutdown(self) -> None:
        if not self.enabled:
            return
        self.stop_loop()
        if self._ui_channel is not None:
            self._ui_channel.stop()
        if self._warning_channel is not None:
            self._warning_channel.stop()