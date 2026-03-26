# Week 10 Assignment Starter — A6 Audio Pass

This starter is meant to be a clean base for A6, not a finished submission.

It already includes:

- a small scenes-based `pygame` app
- a centralized audio helper with safe mixer setup
- generated placeholder tones for `start`, `scan`, and background loops
- a mute toggle and separate music/SFX volume constants
- an explicit cooldown on the scan action so they have one anti-spam example to build from

## Run

From this folder:

- `python3 -m venv .venv`
- `source .venv/bin/activate`
- `python -m pip install -r requirements.txt`
- `python main.py`

## Controls

- `WASD` or arrow keys: move
- `Space`: scan pulse
- `M`: mute / unmute
- `Esc`: quit

## Starter design

- `title` scene: looping title ambience and start transition
- `play` scene: collect blue nodes, avoid red hazards, use scan pulse on cooldown
- `end` scene: restart flow and space for students to add success/fail cues

## Audio map
 
All sounds are generated procedurally at startup using sine waves — no audio files required.
 
| Cue | Trigger | Character |
|-----|---------|-----------|
| `start` | Space on title / end screen | Short 523 Hz (C5) blip — neutral confirmation |
| `scan` | Space during play, cooldown-gated | 740 Hz ping — sonar pulse feel |
| `pickup` | Player overlaps a node | High 1047 Hz (C6) beep — bright, rewarding |
| `damage` | Player hit by hazard (once per invincibility window) | Low 131 Hz (C3) thud — heavy, clearly negative |
| `win` | Score reaches target | Sustained 880 Hz (A5) tone — victorious |
| `fail` | HP reaches zero | Low 185 Hz (F#3) tone — grim, definitive |
| `title_loop` | Title screen (reserved channel) | Slow atmospheric arpeggio: G3→B3→D4→F#4→D4→B3, ~2s cycle |
| `play_loop` | Play scene (reserved channel) | Walking bassline: C4→D4→E4→D4→C4→B3→A3, ~1.6s cycle |

## Playtesting Notes
The original background loops were single repeating notes which became grating almost immediately. 
Replacing them with short multi-note melodies using the `_melody()` helper made the background feel
like it was moving rather than just droning. The `title_loop` intentionally ends with a short silence 
before repeating, which gives it room to breathe. The `damage` cue was the hardest to balance — too quiet 
and it disappeared under the play loop, too loud and it felt punishing. Landing at `SFX_VOL` (0.40) with 
the loop at `MUSIC_VOL` (0.15) gave it enough headroom to cut through without being jarring.

## Mix-control and scene behavior
 
Channel 0 is reserved exclusively for the background loop so SFX can never steal it. `play_loop()` checks
`get_busy()` before restarting to prevent stuttering on scene re-entry. The end screen calls `stop_loop()` 
first so the win/fail cue always plays over silence.