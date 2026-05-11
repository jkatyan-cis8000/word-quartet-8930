# ARCHITECTURE.md

Written by team-lead before spawning teammates. This is the shared blueprint —
teammates read it to understand what they are building and how their module fits.
Update it when the structure changes; do not let it drift from the actual code.

## Module Structure

- `src/data/__init__.py`: Package initialization and word category definitions
- `src/data/word_groups.py`: Hardcoded word groups with categories and difficulty levels
- `src/puzzle.py`: Core puzzle logic — word selection, grouping validation, solution finding
- `src/game.py`: Game state management, turn tracking, win/loss conditions
- `src/ui.py`: Terminal UI rendering, user input handling, interactive display
- `src/main.py`: Application entry point, daily puzzle initialization
- `tests/`: Unit tests for each module

## Interfaces

### puzzle.py
- `Puzzle` class with:
  - `__init__(word_grid: List[str])`: Initialize with 16 words
  - `get_solution() -> List[Tuple[List[str], str, str]]`: Returns correct groupings, category, difficulty
  - `validate_group(words: List[str]) -> Tuple[bool, Optional[str]]`: Check if group is correct, returns category if valid
  - `get_remaining_words() -> List[str]`: Words not yet grouped correctly
  - `is_complete() -> bool`: Whether all groups have been found

### game.py
- `Game` class with:
  - `__init__(puzzle: Puzzle)`: Initialize with a Puzzle instance
  - `make_guess(word_indices: List[int]) -> GameResult`: Process player selection
  - `get_remaining_guesses() -> int`: How many more mistakes allowed
  - `get_state() -> GameState`: Current board state, found groups, mistakes
  - `is_game_over() -> bool`: Win or loss condition met
  - `shuffle_grid()`: Randomize word positions (no gameplay impact)

### ui.py
- `TerminalUI` class with:
  - `display_grid(words: List[str], found_groups: List[GroupInfo])`: Render 4x4 grid
  - `display_found_groups(found_groups: List[GroupInfo])`: Show solved groups
  - `get_user_input(current_selection: List[int]) -> UserAction`: Parse input for selection/take/shuffle/quit
  - `show_feedback(result: GameResult)`: Display success/failure message

## Shared Data Structures

```python
# Difficulty levels and their display colors
DIFFICULTY = {
    "yellow": {"color": "yellow", "points": 1},
    "green": {"color": "green", "points": 2},
    "blue": {"color": "blue", "points": 3},
    "purple": {"color": "purple", "points": 4}
}

# Group info returned from puzzle validation
GroupInfo = NamedTuple("GroupInfo", [
    ("words", List[str]),
    ("category", str),
    ("difficulty", str)
])

# Game result from make_guess
GameResult = NamedTuple("GameResult", [
    ("success", bool),
    ("group_info", Optional[GroupInfo]),
    ("message", str),
    ("mistakes", int)
])

# Game state for UI
GameState = NamedTuple("GameState", [
    ("word_grid", List[str]),
    ("found_groups", List[GroupInfo]),
    ("mistakes", int),
    ("remaining_guesses", int),
    ("is_complete", bool)
])

# User actions from input parser
UserAction = NamedTuple("UserAction", [
    ("type", str),  # "select", "take", "shuffle", "quit"
    ("indices", Optional[List[int]])
])
```

## External Dependencies

- `colorama`: For color-coded terminal output (yellow, green, blue, purple)
- No external dependencies for core logic — pure Python standard library

## Daily Puzzle Generation

- Puzzle uses a predefined set of word groups (stored in `src/data/word_groups.py`)
- Daily puzzle selects words deterministically based on date (YYYY-MM-DD hash)
- Same date = same puzzle for all players
