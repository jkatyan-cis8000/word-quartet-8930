"""Main entry point for Word Quartet puzzle game."""

import sys
from typing import Optional

from src.data.word_groups import WORD_GROUPS, DIFFICULTY
from src.puzzle import Puzzle, generate_daily_puzzle
from src.game import Game, GameState
from src.ui import TerminalUI, UserAction, GroupInfo, GameResult, GameState as UIGameState


def get_random_word_grid(num_groups: int = 4) -> list:
    """Get a random set of words for the puzzle grid."""
    all_words = []
    for words, _, _ in WORD_GROUPS:
        all_words.extend(words)

    return all_words[:16]


def main():
    """Main entry point for Word Quartet."""
    ui = TerminalUI()

    # Generate or load puzzle
    print("Welcome to Word Quartet!")
    print("Your puzzle is ready. Good luck!\n")

    # For now, use a random grid; later use generate_daily_puzzle()
    word_grid = get_random_word_grid()

    try:
        puzzle = Puzzle(word_grid)
    except ValueError as e:
        print(f"Error creating puzzle: {e}")
        sys.exit(1)

    game = Game(puzzle=puzzle)

    current_selection: list = []

    while not game.state.is_game_over:
        # Display current game state
        ui.show_game_state(game.state)

        if current_selection:
            print(f"\nSelected: {', '.join(current_selection)}")
            print("Use 'take' to submit guess, 'shuffle' to rearrange, 'quit' to exit")

        # Get user input
        try:
            user_input = input("\nAction: ").strip().lower()
        except EOFError:
            print("\nInput stream ended. Exiting...")
            break

        if user_input in ("quit", "q", "exit"):
            print("Thanks for playing!")
            break

        if user_input in ("shuffle", "s"):
            # Shuffle the grid (randomize order)
            import random
            new_grid = game.state.word_grid.copy()
            random.shuffle(new_grid)
            game = Game(puzzle=Puzzle(new_grid))
            game.state.found_groups = game.state.found_groups.copy()
            current_selection = []
            continue

        if user_input in ("take", "t"):
            if len(current_selection) != 4:
                print(f"Must select exactly 4 words (currently {len(current_selection)})")
                continue

            # Submit guess
            words = [game.state.word_grid[int(i) - 1] for i in current_selection]
            success, group_info, message = game.submit_group(words)

            if success and group_info:
                print(f"\n✓ CORRECT! Found: {group_info.category}")
                print(f"  Words: {', '.join(group_info.words)}")
                print(f"  Difficulty: {group_info.difficulty}")
            else:
                print(f"\n✗ INCORRECT: {message}")

            current_selection = []

        # Try to parse as word selection
        try:
            idx = int(user_input) - 1
            if 0 <= idx < 16:
                if idx in current_selection:
                    current_selection.remove(idx)
                else:
                    if len(current_selection) < 4:
                        current_selection.append(idx)
                    else:
                        print("Already selected 4 words. Use 'take' to submit.")
            else:
                print("Please enter a number between 1 and 16")
        except ValueError:
            print("Invalid input. Use number 1-16, 'take', 'shuffle', or 'quit'")

    # Final state display
    ui.show_game_state(game.state)

    if game.state.is_complete:
        print("\n🎉 Congratulations! You found all groups!")
    elif game.state.mistakes >= game.state.max_mistakes:
        print(f"\nGame over! You made {game.state.mistakes} mistakes.")

    print("\nThanks for playing Word Quartet!")


if __name__ == "__main__":
    main()
