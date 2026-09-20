# Desert Dash

Desert Dash is a 2D endless-runner built with Python and Pygame. The player avoids increasingly frequent obstacles, collects power-ups, and attempts to set a high score as the game progressively increases in speed and difficulty.

(all graphics drawn by me except the font)

[Watch a video of the game here!](https://youtu.be/va2PVXzSH-k)

## Gameplay

- Dodge cacti, tumbleweeds, and bats as the game becomes progressively faster.
- Collect hearts to gain lives and stars to temporarily double your score.
- Collect laser pickups to charge the laser meter, then press `L` to activate homing shots.
- Your five highest scores are saved locally.

## Requirements

- Python 3.9 or later
- Pygame Community Edition

## Running the Game

Clone the repository and enter its directory:

```bash
git clone https://github.com/am-i-rit/desert-dash.git
cd desert-dash
```

### macOS or Linux

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install Pygame and start the game:

```bash
python -m pip install -r requirements.txt
python main.py
```

### Windows

Create and activate a virtual environment in PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install Pygame and start the game:

```powershell
python -m pip install -r requirements.txt
python main.py
```

## Controls

| Key | Action |
|---|---|
| `Space` or `Up Arrow` | Jump |
| `Down Arrow` | Fall faster while airborne |
| `L` | Activate automatic firing when the laser meter is full |
| `I` | Open the instructions from the main menu |
| `B` | Return to the main menu |
| `Space` | Start a run or play again |