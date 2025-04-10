# Deathtrip: Redd en Venn

A short interactive game that raises awareness about the dangers of impaired driving.

## Overview

**Deathtrip: Redd en Venn** is a visual-novel-style decision-making game developed using Python and Pygame. Players navigate through various scenarios where they must help a friend avoid impaired driving. The game’s narrative is driven by dialogue choices, and every decision affects the outcome of the story.

## Features

- **Interactive Story:** Engage with characters and make choices that influence the narrative.
- **Dynamic Transitions:** Enjoy smooth fade transitions between scenes powered by a custom `FadeTransition` class ([`FadeTransition`](code/transition.py)).
- **Configurable Audio:** Adjust the volume for sound effects and music separately using in-game sliders. Configuration is handled by functions in [`settings.py`](code/settings.py).
- **Multiple Scenes:** The game offers several scenes (e.g., "start", "scene_2", "scene_3", "scene_4", and ending scenes) to simulate the consequences of each choice.
- **Custom UI Elements:** Animated buttons and dialogue boxes enhance the visual interaction ([`AnimatedButton`](code/game.py)).


## How to Run

1. **Install Dependencies:**  
   Ensure Python and Pygame are installed. Install Pygame with:
   ```sh
   pip install pygame

2. **Lauch the Game**
    python code/menu.py

3. **Gameplay:**
    Use the mouse to navigate through the menu and game dialogue.
    Adjust volume settings in the settings screen.
    Make choices during the interactive dialogue to see different outcomes.

## Configuration
General Volume: Stored in config.txt (e.g., volume=2.5).
Music Volume: Stored in music_config.txt (e.g., music_volume=2.5).