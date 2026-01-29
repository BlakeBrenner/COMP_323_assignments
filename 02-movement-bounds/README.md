# Week 2 Example — Movement + Boundaries

This example supports the Week 2 slides.

## Learning goals
- Define a playfield separate from the HUD
- Update movement with dt and a velocity vector
- Implement boundary rules (clamp/wrap/bounce)
- Add a simple goal loop (reach target) + a second object (teleporter)

## Run
From this folder:

- `python3 -m pip install pygame`
- `python3 main.py`

## Controls
- Arrow keys / WASD: move
- `Tab`: cycle boundary mode
- `P`: toggle platformer mode (jump + gravity)
- `Up` / `W`: jump (platformer mode)
- `R`: reset level
- `Space`: start (from title)
- `Esc`: quit

## What to change first
- `PLAYFIELD_PADDING`, `PLAYER_MAX_SPEED`, `TIMER_SECONDS`
- Try swapping boundary mode defaults
- Try making the teleporter a hazard instead

## What I added 

### Moving Platforms — 3-6 Key Bullets
- What it does — Bounces player upward with oscillating movement
- What choice it forces — When to jump (timing-based decisions)
- What the player learns — Prediction and "leading" jumps
- Why it enables progression — Natural difficulty scaling
- Risk/reward dynamic — Platform position affects future moves

### Checkpoints — 3-6 Key Bullets
- What it does — Progress markers with goal relocation
- What choice it forces — Route selection through platforms
- What the player learns — Spatial planning and foresight
- Why it enables progression — Creates natural level pacing
- Meaningful decision-making — Every jump impacts checkpoint navigation

### Change notes
- Platform flickering bug, platform 4 was moving upward (velocity.y = -130)
But min_pos and max_pos were swapped — the boundaries were reversed
This caused the platform to flicker and get stuck at the boundary checks

- Platform heigh change, platform spawn was too high for the player to jump onto
