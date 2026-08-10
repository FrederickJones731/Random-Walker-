# Random-Walker +

## Overview

Welcome to the Random Walker+ project! This simulation explores the mathematical concept of a random walk through a completely self-playing visual experience. Once launched, the program takes over, generating a unique, unpredictable path across the screen without requiring any user input. It is a minimalist sandbox designed to visualize how random, micro-level directional decisions can culminate in complex, organic patterns over time.

---

## Libraries Used

This project relies on a few core libraries to handle the logic, math, and rendering smoothly.

| Library | Purpose |
| --- | --- |
| **Pygame** | Handles the graphical user interface, rendering the walker's path, and managing the application window and frame rate. |
| **NumPy** | Manages the coordinate tracking, array manipulations, and grid calculations efficiently. |
| **Random** | The built-in Python module used to generate the core randomized directional choices for the walker's movement. |

---

## Core Architecture

The project is structured around a few key classes to keep the logic modular and easy to extend. Here is a breakdown of what each class does:

* **`Simulation`**: This is the main engine of the project. It initializes the display window, manages the main application loop, handles background rendering, and safely closes the program when the user exits.
* **`Walker`**: This class represents the entity moving across the screen. It tracks its own current X and Y coordinates, calculates its next move based on a randomized step function, and manages its visual attributes like color and size.
* **`Environment`**: This acts as the canvas or grid where the walker exists. It keeps a record of all previously visited coordinates to draw the continuous trail and ensures the walker either wraps around or bounces off the screen edges when it wanders too far.

## Game Modes

Beyond the standard infinite random walk, this simulation features several self-playing game modes where the autonomous walkers compete against each other or their environment. Once the simulation begins, the entities rely entirely on their random movement logic to achieve the following objectives:

* **Coin Collection**: Walkers randomly traverse the map to collect coins. The simulation tracks their scores, and the first walker to reach a prespecified coin threshold is declared the winner.


* **Race**: A test of pure, chaotic luck. A flag pole is spawned on the grid, and the walkers race to reach it. The first entity to touch the flag wins the round.


* **Cops and Robbers**: This mode introduces asymmetrical roles, complete with distinct police and robber sprites. The "cops" are given a specific number of turns to corner and catch the "robbers." If the turn limit expires before the cops successfully catch their targets, the robbers win the simulation.


* **Survival**: A high-stakes endurance mode. Environmental obstacles (like spreading fire) spawn and expand across the grid with every tick. The walkers must randomly navigate the shrinking safe zones, and the last walker standing claims victory. Dedicated animations will display the winners and losers at the end of the match.


---

## Configuration and Malleable Attributes

To keep the project highly customizable, you do not need to dive into the core Python scripts to tweak the experience. All core attributes, constraints, and game rules are entirely malleable and can be adjusted externally.

This is all applicable in the specific file named `rules_config.json`. This JSON file acts as the control center for the simulation. By editing this file, you can easily tweak parameters such as:

* The required coin threshold to win the Coin Collection mode.
* The strict turn limits assigned to the cops in the Cops and Robbers mode.
* The spread rate and density of the obstacles generated in the Survival mode.
* General settings like grid dimensions, walker movement logic, and UI parameters.

---

## File Structure Highlights

For those looking to explore the underlying codebase within final_project.zip, here are a few specific files to note:

* **`rules_config.json`**: The primary configuration file used to easily alter the simulation's rules and malleable attributes.


* **`main.py` & `game.py**`: The core engines that drive the application loop, manage the state transitions between the different game modes, and initialize the simulations.


* **`field.py`**: This file manages the underlying grid, handling the coordinate mapping, obstacle spreading logic for Survival mode, and spatial relationships between the walkers.


* **`game_screen.py` & `graph_screen.py**`: These handle the visual rendering of the simulation and any analytical data tracking the walkers' paths.


* **Media Assets**: The project dynamically pulls specific visual and audio cues depending on the active game mode, including `coin_sfx.wav` for the collection mode, `bump_sfx.aiff` for collisions, and various animated GIFs for the cops, robbers, and hazards.

---

## Getting Started

To watch the random walker play itself, follow these straightforward steps:

1. Clone or download this repository to your local machine.
2. Install the required dependencies via your terminal (e.g., `pip install pygame numpy`).
3. Run the main application file from your terminal.
4. Pick your desired game mode.
5. Sit back, relax, and watch the simulation unfold on its own.
