# 🎮 Python Mini-Game Arcade

Welcome to the **Ultimate Python Mini-Game Arcade**! This is a fully playable, juice-filled collection of classic retro games built entirely in Python using the `pygame` library. The arcade features massive visual upgrades, modern particle systems, deep parallax backgrounds, and an incredibly satisfying user experience.

---

## 🕹️ The Games

A central interactive Hub menu allows you to launch any of the following visually stunning mini-games:

- **🐍 Neon Snake**: A classic snake game featuring a scrolling geometric background, pulsing snake animations, and glowing shockwave rings when collecting food.
- **🏓 Pong**: Fast-paced paddle action with a dynamic pulsing center net, paddle sparks on impact, and a smooth glowing ribbon trail for the ball.
- **✖️⭕ Tic-Tac-Toe**: A clean, premium UI with neon hover glows and a beautiful radial background. 
- **🧱 Brick Breaker**: Shatter bricks into hundreds of colorful debris particles, set against a downward-scrolling parallax tech grid with glowing spaceship paddle thrusters.
- **🚀 Space Shooter**: Defend against aliens in a multi-layered parallax starfield with continuous engine thruster plumes, cyan muzzle flashes, and massive expanding explosion shockwaves.
- **🧩 Neon Tetris**: Features a "ghost" projection showing exactly where your pieces will land, hard-drop particle trails, and intense screen flashes on line clears!
- **🦅 Flappy Bird**: Navigate pipes in a multi-layered scrolling cityscape featuring a dynamic day/night cycle and glowing floating coins.

---

## ✨ Features

- **Modern Visual Effects:** Every game is packed with screen shake, particle emitters, shockwaves, ribbon trails, and parallax scrolling backgrounds.
- **Multiple Themes:** Cycle through 4 distinct color palettes (Neon, Retro, Midnight, Cyberpunk) directly from the main hub.
- **Persistent High Scores:** Your high scores and theme preferences are automatically saved locally in a `data.json` file.
- **Clean Architecture:** The entire arcade, all UI elements, and all 7 games are seamlessly integrated into a single cohesive Python application.

---

## 🛠️ Installation & Setup

It's extremely easy to get the arcade running on your local machine.

### Prerequisites
- Python 3.x installed on your system.

### Steps
1. **Clone this repository** to your local machine:
   ```bash
   git clone https://github.com/Harshitagarwal113/Arcade_Games.git
   cd Arcade_Games
   ```

2. **Install the required dependencies** (only `pygame` is needed):
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the arcade**:
   ```bash
   python arcade.py
   ```

---

## 🎮 How to Play

- **Navigating the Hub:** Use your mouse to hover over the glowing game cards and click to launch a game. Use the "Toggle Theme" button to change the global color scheme.
- **In-Game Controls:**
  - **Pong:** Player 1 uses `W`/`S`, Player 2 uses `UP`/`DOWN` arrows.
  - **Snake:** Arrow keys to move.
  - **Tic-Tac-Toe:** Mouse clicks to place your piece.
  - **Brick Breaker / Space Shooter:** `LEFT`/`RIGHT` arrows to move. `SPACE` to shoot (in Space Shooter).
  - **Tetris:** `LEFT`/`RIGHT` to move, `UP` to rotate, `DOWN` for soft drop, `SPACE` for hard drop.
  - **Flappy Bird:** `SPACE` or `UP` arrow to flap.
- **Exiting a Game:** You can exit any game at any time and return to the main hub by pressing the `ESC` key.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! If you want to add a new game or improve an existing effect, feel free to fork the repository and submit a pull request.

---

**Built with ❤️ using Python and Pygame.**
   