# Week 4 Example — Sprites + Collisions

This example supports the Week 4 slides (sprites, groups, hitboxes, and collision responses).

## Learning goals
- Use `pygame.sprite.Sprite` and `pygame.sprite.Group`
- Keep a *hitbox* (`rect`) separate from how you draw
- Detect overlaps and handle *responses* (solid walls, triggers, damage)
- Add basic fairness/feel: feedback bundle + short invincibility frames

## Run
From this folder:

- `python3 -m pip install pygame`
- `python3 main.py`

## Controls
- Arrow keys / WASD: move
- `F1`: toggle debug (hitboxes)
- `R`: reset
- `Esc`: quit

## What was added
- **Dash Powerup**: Collect the green star-shaped powerup to gain the ability to dash
- **Dash Mechanic**: Press Left Shift to perform a high-speed dash in your current movement direction
- **Invincibility During Dash**: Taking damage while dashing grants 0.3 seconds of invincibility frames where hazards can't hurt you
- **Color Change**: Player changes from cyan to purple when the dash powerup is active
- **Powerup Loss on Damage**: Getting hit by a hazard while you have the dash powerup removes it instead of losing HP
- **Visual Feedback**: Powerups are displayed as star shapes and the HUD shows "[Dash Ready - LShift]" when available

## Game loop
Each frame, the game reads player input and updates positions with collision detection against solid walls. When the player collides with coins, they score points; when hit by hazards, they lose the dash powerup (if equipped) or take damage with knockback and temporary invincibility frames. The camera shakes on impact to provide tactile feedback.
