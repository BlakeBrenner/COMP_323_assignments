from __future__ import annotations

import math
from array import array

import pygame

MUSIC_VOL = 0.15
SFX_VOL   = 0.40

_muted   = False
_loop_ch: pygame.mixer.Channel | None = None


def _beep(freq: float, ms: int, vol: float = SFX_VOL) -> pygame.mixer.Sound:
    """Generate a simple sine-wave beep and return it as a Sound."""
    rate = 22050
    n    = int(rate * ms / 1000)
    fade = max(1, n // 10)
    amp  = int(32767 * vol)
    buf  = array("h")
    for i in range(n):
        s = math.sin(2 * math.pi * freq * i / rate)
        e = min(i, n - i, fade) / fade     # fade in/out envelope
        buf += array("h", [int(s * e * amp)] * 2)   # stereo (L, R)
    return pygame.mixer.Sound(buffer=buf.tobytes())


def _melody(notes: list[tuple[float | None, int]], vol: float = MUSIC_VOL) -> pygame.mixer.Sound:
    """Build a loopable melody from (freq_or_None, ms) pairs. None = silence."""
    rate = 22050
    buf  = array("h")
    for freq, ms in notes:
        n    = int(rate * ms / 1000)
        fade = max(1, n // 10)
        amp  = int(32767 * vol)
        for i in range(n):
            if freq is None:
                sample = 0
            else:
                s      = math.sin(2 * math.pi * freq * i / rate)
                e      = min(i, n - i, fade) / fade
                sample = int(s * e * amp)
            buf += array("h", [sample, sample])
    return pygame.mixer.Sound(buffer=buf.tobytes())


def init_audio() -> bool:
    """Set up mixer and reserve channel 0 for loops. Returns False on failure."""
    global _loop_ch
    try:
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.mixer.set_num_channels(8)
        pygame.mixer.set_reserved(1)
        _loop_ch = pygame.mixer.Channel(0)
        return True
    except pygame.error:
        return False


def build_sounds() -> dict[str, pygame.mixer.Sound]:
    """Build all sounds once at startup — never call this during active play."""
    return {
        "start":      _beep(523,  100),           # C5  — neutral blip
        "scan":       _beep(740,   80),           # mid — sonar ping
        "pickup":     _beep(1047,  90),           # C6  — high bright reward
        "damage":     _beep(131,  220),           # C3  — low thud
        "win":        _beep(880,  400),           # A5  — victorious
        "fail":       _beep(185,  400, 0.30),     # F#3 — low grim tone
        # Multi-note loops so background isn't a single repeating tone
        "title_loop": _melody([          # slow, atmospheric arpeggio ~2s
            (196, 400), (247, 400), (294, 400), (370, 600),
            (294, 300), (247, 300), (None, 200),
        ]),
        "play_loop":  _melody([          # upbeat walking bassline ~1.6s
            (262, 200), (294, 200), (330, 200), (294, 200),
            (262, 200), (247, 200), (220, 200), (None, 200),
        ]),
    }


def play(sounds: dict, name: str) -> None:
    if not _muted and name in sounds:
        sounds[name].play()


def play_loop(sounds: dict, name: str) -> None:
    if _loop_ch is None or name not in sounds:
        return
    if _loop_ch.get_sound() is sounds[name] and _loop_ch.get_busy():
        return                              # already playing, don't restart
    _loop_ch.stop()
    if not _muted:
        _loop_ch.play(sounds[name], loops=-1)


def stop_loop() -> None:
    if _loop_ch:
        _loop_ch.stop()


def toggle_mute(sounds: dict) -> None:
    global _muted
    _muted = not _muted
    # Volume is baked into waveform amplitude, so restore to 1.0 (not MUSIC_VOL)
    # to avoid applying the scale factor twice and making sounds inaudible.
    vol = 0.0 if _muted else 1.0
    for s in sounds.values():
        s.set_volume(vol)
    if _loop_ch:
        _loop_ch.set_volume(vol)