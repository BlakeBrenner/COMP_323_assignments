# Week 5 Example — Animation + Feedback

This example supports the Week 5 slides (animation states, dt-driven frame timers, and feedback bundles).

## Learning goals

- Implement a basic animation timer (dt-driven)
- Choose animation by state (idle/run/hurt)
- Keep motion smooth with float positions + `Rect`
- Add a small feedback bundle (flash/shake/hitstop/particles)
- Handle rotation without drift (`get_rect(center=...)`)

## Run
From this folder:

- `python3 -m pip install pygame`
- `python3 main.py`

## Controls
- Arrow keys / WASD: move
- `Space`: start / restart
- `F1`: toggle debug overlay (hitboxes)
- `R`: reset level
- `1`: toggle flash cue
- `2`: toggle screen shake cue
- `3`: toggle hitstop cue
- `4`: toggle particles cue
- `Esc`: quit

## What to change first
- Change animation speed (fps) in `anim_feedback/game.py`
- Add one more state (e.g., `hurt` animation)
- Add a new event and choose a feedback bundle for it

## What I Added
- **Text popups** — a floating "+1" appears above a coin on pickup, "OUCH!" appears above the player on hazard contact, and "i'm dead" appears on death; each popup drifts upward and fades out over 0.75 s.
- **Sound** — synthesized sine-wave beeps play on each event: a high-pitched tone on coin pickup, a low buzz on hazard hit, and a deep tone on death; generated programmatically at runtime with no external audio files.
- **Player Animation** - Expanded the canvas to 56×60 so limbs have real room

## Core Loop
The player navigates a walled arena collecting coins while avoiding spinning hazard diamonds. Once all 10 coins are collected the level resets with the player's score preserved; the game ends when HP reaches zero.

## Rationale

I wanted the player to have a visual numeric feedback when collecting coins so I created the coin pop up in order for the player to not have to take their eyes away from the character. I also wanted to givee audio feedback to the player when it collects a coin or gets hurt.  On death, a distinct deep tone paired with the "i'm dead" popup provides a final clear signal that the game is over.