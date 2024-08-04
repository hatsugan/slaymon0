
# Slaymon v0.1

Slaymon is a simple web-based game where players select a "Slay" (creature) to battle against a randomly chosen opponent. The game is built using Flask for the backend and a basic HTML/CSS front-end to display the game interface.

## Project Structure

### Files
- **app.py**: The main Flask application that handles routing and game logic integration.
- **game_engine.py**: Contains the game logic, including classes for `Slay` and `Battle`, and the list of available Slays and their moves.
- **templates/index.html**: The main page for selecting a Slay.
- **templates/battle.html**: The battle interface page.
- **static/styles.css**: Stylesheet for the game's frontend.
- **static/scripts.js**: Script to handle frontend behavior.

### app.py

This is the main file that initializes the Flask application and defines the routes for the game.

#### Routes
- **/**: Displays the list of available Slays for the player to choose from.
- **/select/<int:slay_index>**: Initializes a battle with the selected Slay and a random opponent.
- **/battle**: Displays the battle interface.
- **/move/<int:move_index>**: Handles the player's move during the battle.
- **/rematch**: Starts a new battle with the same player Slay against a new random opponent.

### game_engine.py

This file contains the core game logic.

#### Classes

- **Slay**: Represents a creature with attributes such as name, health, strength, hardness, toughness, speed, and moves.
  - **Methods**:
    - `generate_image_filename`: Generates the filename for the Slay's image.
    - `take_damage`: Adjusts the Slay's health based on damage or healing.
    - `is_fainted`: Checks if the Slay has fainted (health is 0).
    - `reset_health`: Resets the Slay's health to maximum.

- **Battle**: Manages a battle between two Slays.
  - **Methods**:
    - `calculate_damage`: Calculates damage based on move modality and attributes of attacker and defender.
    - `calculate_healing`: Calculates healing based on move and toughness of the user.
    - `slay_move`: Executes a move and updates the health and battle log.
    - `player_turn`: Sets the move for the player's turn.
    - `opponent_CPU`: Randomly selects a move for the opponent.
    - `execute_round`: Executes a round of battle, considering speed and turn order.
    - `end_round`: Ends the round and checks if the battle is over.
    - `is_battle_over`: Checks if either Slay has fainted, ending the battle.

#### Functions
- **get_random_slay**: Returns a new instance of a random Slay from the list.

#### Variables
- **slay_list**: A list of available Slays with predefined attributes and moves.

### Frontend Templates

#### index.html

Displays a list of available Slays for the player to choose from. Each Slay is displayed with its image, stats, and moves.

#### battle.html

Displays the current battle state, including the player's Slay, opponent's Slay, their health bars, stats, available moves for the player, and the battle log.

### Static Files

#### styles.css

Contains the styles for the game, ensuring a consistent look and feel across the different pages.

#### scripts.js

Includes a script to auto-scroll the battle log to the latest entry.

## Running the Project

To run the project, make sure you have Flask installed, then run `app.py`:

```bash
python app.py
```

Navigate to `http://127.0.0.1:5000/` in your web browser to start the game.

## Future Improvements

- Add more Slays with unique abilities.
- Implement more complex battle mechanics.
- Create a more dynamic and interactive front-end.
- Add user authentication and game progress tracking.

## Logging

Logging is configured to output debug information to the console, helping trace the flow of the game and identify any issues during development.
