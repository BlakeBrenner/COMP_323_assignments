# Week 3 Example — Input + Control Feel

This example supports the Week 3 slides.

## Learning goals
- Use events for discrete actions (dash/jump/toggles)
- Use key-state for continuous movement intent
- Normalize 8-direction movement to avoid diagonal speed bugs
- Tune feel with small parameter presets

## Run
From this folder:

- `python3 -m pip install pygame`
- `python3 main.py`

## Controls
- Arrow keys / WASD: move (top-down)
- `P`: toggle platformer mode (jump + gravity)
- `Up` / `W` / `Space`: jump (platformer mode)
- `Left Shift`: dash (cooldown)
- `1` / `2` / `3`: feel preset (tight/floaty/heavy)
- `C`: cycle control scheme (WASD / arrows / IJKL)
- `F1`: toggle debug overlay
- `Tab`: cycle boundary mode (clamp/wrap/bounce)
- `R`: reset
- `Space`: start (from title)
- `Esc`: quit

## What to change first
- Try editing preset values in `input_control_feel/game.py`:
  - accel / friction / max speed
  - gravity / jump speed
- Try changing dash cooldown or dash impulse

## Changes
- Added variables like MOVE_LEFT and MOVE_RIGHT for more readability
- Added double jump 
  - Double jump resets when character touches ground 
  - Jump can be held or pressed
  - Jumps left are shown in corner of the screen under dash cooldown

- New gameplay presets
  - Slick: faster character acceleration speed, higher max speed, player slides along ground
    - Keypress 4
  - Moon: low gravity, huge jumps
    - Keypress 5

- Dash power increase 760 to 5000
  - I could only feel a large difference in slick preset