# 🍄 Super Mario Bros. 3 Pygame Clone

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)
![Status: WIP](https://img.shields.io/badge/Status-Work_In_Progress-orange.svg)
![Help Wanted](https://img.shields.io/badge/Help_Wanted-Yes!-ff69b4.svg)

**A complete, data-driven Super Mario Bros. 3 fan game made with Pygame, featuring its own built-in map editor.**

<img alt="Super Mario Bros 3 Pygame Screenshot" src="https://github.com/user-attachments/assets/0ff67d42-6ddf-4e09-af40-68f06c6bd275" />

> 🚧 **WORK IN PROGRESS & WE NEED YOUR HELP!** 🚧
> 
> *This game is currently in active development. We are looking for extra hands to help build levels, add new entities, code features, and polish the engine.
> Whether you know Python, enjoy level design, or just want to test things out, **your help is incredibly welcome!***

[![Gameplay Preview](https://img.youtube.com/vi/D--FpcQ12yk/maxresdefault.jpg)](https://youtu.be/D--FpcQ12yk?t=17)
*(Click to watch the gameplay preview)*

---

## 🚧 Roadmap & Where We Need Help

Since our engine is mostly data-driven, **you don't even need to be a Python expert to contribute!** We are actively looking for:

- **🐍 Python Developers:** To implement missing entity behaviors (bosses, complex enemies), refine physics, and optimize the engine.
- **🗺️ Level Designers:** To use our built-in map editor and recreate classic levels or design brand-new custom worlds!
- **📝 Data Tweakers:** To adjust YAML files (balancing jump height, enemy speed, hitboxes).
- **🐛 Playtesters:** To play the game, try to break it, and report bugs.

If you want to jump in, check out the [Contributing](#-contributing--we-need-you) section below!

---

## ✨ Current Features

- **Classic Gameplay:** Authentic physics, basic entities (Goombas, Koopas), and power-ups.
- **Built-in Map Editor:** Create, edit, and playtest your own custom levels seamlessly.
- **100% Data-Driven:** Modify game rules, entities, animations, and levels via YAML and JSON without writing a single line of Python.
- **Customizable:** Fully remappable controls and scalable window resolutions.

---

## 🚀 Quick Start

### Requirements
- Python 3.10+
- Pygame 2
- PyYAML

### Installation & Run

Clone the repository and install the dependencies:
```bash
python -m pip install -r requirements.txt
```
Launch the game (it automatically finds its files regardless of the working directory):
```bash
python SuperMarioBros3.pyw
```

---

## 🎮 Controls

| Action  | Keys (default)          | Use                                        |
|---------|-------------------------|--------------------------------------------|
| Move    | `Z Q S D` or arrows     | Navigate menus, move on the world map (hold to keep going), walk in a level. |
| Confirm | `A`, `Enter` or `Space` | Choose menus, skip intros, enter levels. Jump in-game (hold for height). |
| Run     | `Shift` or `E`          | Sprint in a level (running jumps give you more height and distance).  |
| Back    | `Esc`                   | Pause a level (press twice to leave). Go back in menus. |

Keys can be changed in the `controls` section of `config.yaml`, with
[pygame key names](https://www.pygame.org/docs/ref/key.html).

---

## 🛠️ Modding & Level Creation

### The Title Screen Options

* **START GAME**: Play the main world map.
* **CUSTOM LEVELS**: Play any map located in `res/maps` created with the map editor.
* **MAP EDITOR**: Launch the built-in map editor. Press `F5` to instantly save and playtest your map without losing lives!
* **QUIT**: Exit the game.

### How to Add a New Level

1. Draw the level with the map editor (from the title screen: `MAP EDITOR`).
2. Save it as `res/maps/level_1.json` and paint its solid cells (Collisions mode). Test it with `F5`.
3. The world map will automatically load it when the player confirms on the `level1` tile.
*(See the [Map Editor Documentation](https://www.google.com/search?q=map_editor/README.md) for more details).*

### Entities & Data-Driven Engine

The engine is designed so that **values live in YAML files**. You can tweak or create new content without touching the Python codebase.

* **`res/rules.yaml`**: Gameplay mechanics (Mario's physics, scores, time limits, default skies/music).
* **`res/entities.yaml`**: Enemy/Item behaviors, animations, speed, and reactions (e.g., what happens on stomp or touch).
* **`res/sprites.yaml` & `res/sheets/*.yaml**`: Animations, HUD layouts, and tile metadata.
* **`ressources.yaml`**: Asset registry (images, maps, sounds, music).
* **`config.yaml`**: User preferences (window size, controls, volume). *Auto-generated when using the in-game Settings.*
* **`save.yaml`**: Player progress (lives, score, world position). Playtesting in the editor uses a disposable save state to prevent corrupting your main progress.

To tune a **single placed entity** in your level, `Alt + Click` it in the editor's *Entities* mode.

---

## 🏗️ Code Architecture

Curious about how it works under the hood? Read our detailed [Architecture Guide](https://www.google.com/search?q=docs/ARCHITECTURE.md) with diagrams.

```text
SuperMarioBros3.pyw        # Entry point
src/
  game.py                  # Composition root: window, files, scenes, main loop
  scene_manager.py         # Handles current scene & transitions
  platformer.py            # Mario's movement and collisions (logic only, no drawing)
  editor_bridge.py         # Runs the map editor inside the game window
  inputs/                  # YAML parsers and config loaders
  scenes/                  # Title screen, world map, platform levels, etc.
  entities/                # Data-driven Entity base class, spawner, logic
tests/                     # Unit tests
```

---

## 🤝 Contributing (We need you!)

This project is ambitious, and **there is only so much we can do alone!**
Contributions are welcome from everyone, from bug reports to new entities and levels.

1. Read our [Contribution Guide](https://www.google.com/search?q=CONTRIBUTING.md) to get started.
2. Check the [Code of Conduct](https://www.google.com/search?q=CODE_OF_CONDUCT.md).
3. Look at the [Changelog](CHANGELOG.md) for recent updates.
4. Pick an issue, or open a new one to suggest an idea!

*(Report security issues as explained in [SECURITY.md](SECURITY.md)).*

---

## ⚖️ License and Disclaimer

The source code of this project is released under the **[MIT License](https://www.google.com/search?q=LICENSE)**.

**Disclaimer:** This is a non-commercial, open-source fan project. It is not affiliated with, nor endorsed by, Nintendo. *Super Mario Bros. 3*, its characters, graphics, and sounds are trademarks and copyrights of Nintendo. These assets are not covered by the MIT license.
