# Week 11 — Content Pass Demo

Demonstrates config extraction, progressive difficulty, and content pass workflow.

## How to run

From this folder:

- `python3 -m venv .venv`
- `source .venv/bin/activate`
- `python -m pip install -r requirements.txt`
- `python main.py`

## Controls

- Arrow keys: move left/right
- Space: fire
- M: mute/unmute
- Escape: quit

## What this demonstrates

1. **Config extraction**: all difficulty values live in `game_config.py`
2. **Progressive spawn rate**: enemies spawn faster as time passes
3. **Progressive speed scaling**: enemies get slightly faster over time
4. **Enemy cap**: max simultaneous enemies prevents screen flooding
5. **HUD feedback**: shows current spawn delay and speed bonus so you can see the ramp

## Content pass exercise

Try changing these values in `game_config.py` and observe the difference:

- `SPAWN_DELAY_START_MS`: higher = more breathing room at the start
- `SPAWN_RAMP_PER_SEC`: higher = difficulty ramps faster
- `ENEMY_SPEED_MAX_BONUS`: higher = enemies get much faster late game
- `MAX_ENEMIES`: lower = less screen flooding
- `PLAYER_HEALTH`: higher = more forgiving; lower = more punishing

Change one value at a time. Play for 60 seconds after each change. Record what feels different.
