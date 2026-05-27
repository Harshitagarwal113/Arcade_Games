# 🎮 Python Mini-Game Arcade

<div align="center">

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-%3E%3D2.0.0-00B140?style=for-the-badge&logo=python&logoColor=white)
![Games](https://img.shields.io/badge/Games-9%20Classic%20Titles-FF2D87?style=for-the-badge)
![Themes](https://img.shields.io/badge/Themes-4%20Color%20Palettes-A020F0?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**A fully playable, visually stunning collection of 9 classic retro games — all in one Python arcade.**

</div>

---

## 📖 About

The **Python Mini-Game Arcade** is a single cohesive application that houses nine iconic games under one roof. Launched from a beautiful interactive hub menu, each game features modern visual effects including particle systems, parallax scrolling backgrounds, screen shake, neon glows, and dynamic animations — far beyond what you'd expect from a Python/Pygame project.

Built with a clean, modular architecture, the arcade supports **4 switchable color themes** and **persistent high scores** saved locally.

---

## 🕹️ The Games

| # | Game | Description |
|---|------|-------------|
| 🐍 | **Neon Snake** | Classic snake with a scrolling geometric background, pulsing snake animations & glowing shockwave rings on food collection |
| 🏓 | **Pong** | Fast-paced paddle action with a dynamic pulsing center net, paddle sparks on impact, and a smooth glowing ribbon trail for the ball |
| ✖️⭕ | **Tic-Tac-Toe** | Clean premium UI with neon hover glows and a radial animated background |
| 🧱 | **Brick Breaker** | Shatter bricks into colorful debris particles against a parallax scrolling tech grid with a glowing spaceship paddle |
| 🚀 | **Space Shooter** | Defend against aliens in a multi-layered parallax starfield with thruster plumes, muzzle flashes & shockwave explosions |
| 🧩 | **Neon Tetris** | Full Tetris with ghost-piece projection, hard-drop particle trails, and screen flash on line clears |
| 🦅 | **Flappy Bird** | Navigate pipes in a scrolling cityscape with a dynamic day/night cycle and floating glowing coins |
| 🐸 | **Frogger** | Guide your frog across busy roads and rivers in this retro-faithful remake |
| 🔢 | **2048** | The addictive sliding-tile puzzle, rendered with the arcade's premium neon aesthetic |

---

## ✨ Key Features

- 🌟 **Modern Visual Effects** — Screen shake, particle emitters, shockwave bursts, ribbon trails & parallax scrolling on every game
- 🎨 **4 Color Themes** — Switch between **Neon**, **Retro**, **Midnight**, and **Cyberpunk** palettes from the main hub at any time
- 💾 **Persistent Data** — High scores and your selected theme are automatically saved to `data.json` between sessions
- 🏗️ **Clean Architecture** — Modular codebase split across `core/`, `ui/`, `games/`, `graphics/`, and `assets/` packages
- 🎵 **Sound System** — Integrated audio via the `core/sounds` module
- ⚡ **60 FPS** — Smooth 800×600 gameplay locked at 60 frames per second

---

## 🗂️ Project Structure

```
Arcade_Games/
│
├── main.py                  # Entry point — launches the arcade
├── requirements.txt         # Dependencies (pygame >= 2.0.0)
├── data.json                # Auto-generated: high scores & theme preference
│
├── core/                    # Shared engine modules
│   ├── config.py            # Window size, FPS & all 4 theme color palettes
│   ├── display.py           # Pygame screen/display setup
│   ├── sounds.py            # Sound effects management
│   ├── data.py              # Save/load logic for scores & settings
│   └── utils.py             # Shared utility helpers
│
├── ui/
│   └── menu.py              # Main hub menu (game selection, theme toggle)
│
├── games/                   # Individual game modules
│   ├── snake.py
│   ├── pong.py
│   ├── tictactoe.py
│   ├── brick_breaker.py
│   ├── space_shooter.py
│   ├── tetris.py
│   ├── flappy.py
│   ├── frogger.py
│   └── twenty_forty_eight.py
│
├── graphics/                # Visual effect helpers & renderers
└── assets/
    └── sounds/              # Audio assets
```

---

## 🛠️ Installation & Setup

### Prerequisites
- **Python 3.x** — [Download here](https://www.python.org/downloads/)
- **pip** (included with Python)

### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Harshitagarwal113/Arcade_Games.git
   cd Arcade_Games
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the arcade:**
   ```bash
   python main.py
   ```

That's it — the hub menu will launch immediately. 🎉

---

## 🎮 Controls

### Hub Menu
| Action | Control |
|--------|---------|
| Select a game | Mouse click on a game card |
| Switch theme | Click the **Toggle Theme** button |

### In-Game Controls

| Game | Controls |
|------|----------|
| **Pong** | P1: `W` / `S` &nbsp;·&nbsp; P2: `↑` / `↓` |
| **Snake** | Arrow keys |
| **Tic-Tac-Toe** | Mouse click |
| **Brick Breaker** | `←` / `→` to move paddle |
| **Space Shooter** | `←` / `→` to move · `SPACE` to shoot |
| **Tetris** | `←` / `→` move · `↑` rotate · `↓` soft drop · `SPACE` hard drop |
| **Flappy Bird** | `SPACE` or `↑` to flap |
| **Frogger** | Arrow keys |
| **2048** | Arrow keys to slide tiles |
| **Exit any game** | `ESC` — returns to the main hub |

---

## 🎨 Themes

The arcade ships with four hand-crafted color palettes, switchable live from the hub:

| Theme | Vibe |
|-------|------|
| **Neon** | Electric green & hot pink on a deep purple-black background |
| **Retro** | Warm amber & mint green on a classic dark grey |
| **Midnight** | Soft lavender & sky blue on near-black |
| **Cyberpunk** | Blazing yellow & cyan on a deep violet |

---

## 🤝 Contributing

Contributions are welcome! If you want to add a new game, improve a visual effect, or fix a bug:

1. **Fork** the repository
2. Create a feature branch: `git checkout -b feature/new-game`
3. Commit your changes: `git commit -m "Add: [description]"`
4. Push and open a **Pull Request**

Please ensure any new game module follows the existing pattern in the `games/` directory and integrates with `core/config.py` themes.

---

## 📋 Requirements

```
pygame>=2.0.0
```

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">

**Built with ❤️ using Python & Pygame**

⭐ If you enjoyed the arcade, consider giving the repo a star!

</div>
