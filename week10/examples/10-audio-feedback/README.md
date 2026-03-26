# Week 10 Example — Audio + Moment-to-Moment Feedback

This example supports the Week 10 slides as a compact scenes-based game with a centralized audio layer.

## Learning goals

- use a low-latency `pygame.mixer.pre_init(...)` pattern before `pygame.init()`
- initialize `pygame.mixer` safely
- keep audio logic in one helper instead of scattering it across files
- trigger sound from events such as start, fire, hit, damage, and game over
- use looping background ambience for scene/state changes
- route simple UI confirm / cancel cues through their own category
- reserve a channel for a critical warning cue
- provide mute support and a silent fallback if audio is unavailable

## Run

From this folder:

- (Recommended) create and use a virtual environment so you install `pygame` into the same Python you run:
    - `python3 -m venv .venv`
    - `source .venv/bin/activate`
    - `python -m pip install pygame`
    - `python main.py`

## Controls

- Arrow keys / WASD: move (play only)
- `Space`: start / fire / restart (depends on scene)
- `M`: mute / unmute audio
- `Esc`: quit

## Notes

- This example generates simple tones in code, so it does not need external sound files.
- If audio initialization fails, the game keeps running silently.
- The background loop uses a dedicated reserved channel.
- A second reserved channel carries UI confirm / cancel cues.
- A third reserved channel protects the low-health warning so it does not get lost in action clutter.
- `M` toggles mute, and the example keeps music decisions on scene transitions instead of in hot gameplay paths.
- `Space` on title and game-over scenes plays a UI confirm cue before the state change.
- `Esc` plays a UI cancel cue and then exits after a brief delay so the cue is audible.