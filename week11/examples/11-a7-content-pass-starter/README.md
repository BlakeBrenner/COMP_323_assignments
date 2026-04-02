# A7 Content Pass Starter

Starting point for Assignment A7 — Content pass + tuning notes.

## How to run

From this folder:

- `python3 -m venv .venv`
- `source .venv/bin/activate`
- `python -m pip install -r requirements.txt`
- `python main.py`

## Controls

- Arrow keys: move left/right
- Space: fire
- Escape: quit

## Your task

This game has hardcoded difficulty values scattered through the code. Your assignment:

1. **Extract** all difficulty values into `game_config.py`
2. **Create** a content map for the first 60 seconds
3. **Tune** at least 3 values with before/after documentation
4. **Document** everything in this README

Look for `# TODO: move to config` comments in `main.py` for the values to extract.

## Content map

| Time (sec) | What happens | Difficulty lever | Current value | Assessment |
|---|---|---|---|---|
| 0–5 | Game starts; player spawns; no enemies yet | — | — | Good — gives player a moment to orient |
| 5–15 | First enemies appear, slow trickle (~1 every 1.2 s) | `SPAWN_DELAY_MS`, `ENEMY_SPEED_MIN/MAX` | 1200 ms, speed 2–5 | Fair — manageable opening, teaches core loop |
| 15–30 | Enemies accumulate; up to ~10 on screen | `MAX_ENEMIES` | 12 | Slightly easy — skilled players clear enemies faster than they spawn; could feel slow |
| 30–45 | Screen fills closer to cap; dodging becomes necessary | `ENEMY_SPEED_MAX`, `ENEMY_DAMAGE` | speed 5, 20 HP | Good — requires real attention but not punishing |
| 45–60 | Cap of 12 enemies reached regularly; one hit = 20% health | `MAX_ENEMIES`, `ENEMY_DAMAGE` | 12 enemies, 20 HP | Too hard spike possible if 3 enemies reach player simultaneously (−60 HP in one frame cluster) |

## Tuning log

| Variable | Before | After | Why | Result |
|---|---|---|---|---|
| `SPAWN_DELAY_MS` | 800 ms | 1200 ms | At 800 ms the screen flooded within 15 s, leaving almost no room to dodge. Slowing spawns gives the player space to learn the shoot mechanic before being overwhelmed. | First 30 s now feel like a proper warm-up rather than instant chaos. |
| `ENEMY_SPEED_MIN` | 1 px/frame | 2 px/frame | Speed-1 enemies were nearly stationary, padding the screen with near-harmless blockers. Raising the floor makes every enemy a mild threat and keeps the screen from feeling cluttered with free score. | All enemies now require at least some attention; clutter is reduced. |
| `ENEMY_SPEED_MAX` | 7 px/frame | 5 px/frame | Speed-7 enemies crossed the full screen height in under 2 seconds, which at 800 ms spawn rate made some waves literally impossible to react to. Capping at 5 keeps fast enemies as a threat without being frame-perfect. | Fast enemies are now clearly dangerous but dodgeable with a timely move. |
| `MAX_ENEMIES` | uncapped | 12 | Without a cap, late-game screens filled with 20+ enemies simultaneously, turning the game into unavoidable damage. A cap of 12 keeps visual density readable and difficulty tied to skill rather than arithmetic overflow. | Difficulty scales more gracefully; late game feels intense but fair. |

## Intended difficulty curve

The target curve is a gentle S-shape: easy opening (0–15 s) to let the player learn movement and firing, a gradual ramp through the mid-game (15–45 s) where enemies become faster and more numerous, and a steady hard plateau beyond 45 s where the enemy cap and speed ceiling keep difficulty from spiraling into unavoidable damage. The biggest change from the original code is slowing the spawn rate early and capping total enemies — the original design had no ceiling, so difficulty was purely exponential and collapsed into an unwinnable state within a minute. The revised curve rewards continued play and skill improvement rather than punishing the player for surviving too long.
