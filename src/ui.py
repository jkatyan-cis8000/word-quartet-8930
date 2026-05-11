"""Terminal UI module for Word Quartet puzzle game."""

from typing import List, Optional
from colorama import Fore, Style, init

init(autoreset=True)

DIFFICULTY_COLORS = {
    "yellow": Fore.YELLOW,
    "green": Fore.GREEN,
    "blue": Fore.BLUE,
    "purple": Fore.MAGENTA,
}


class TerminalUI:
    """Terminal UI for interacting with the Word Quartet puzzle game."""

    def display_grid(
        self, words: List[str], found_groups: List["GroupInfo"], current_selection: Optional[List[int]] = None
    ) -> None:
        """Render a 4x4 grid of words with found groups displayed below."""
        if current_selection is None:
            current_selection = []

        print("\n" + "=" * 50)
        print("WORD QUARTET")
        print("=" * 50 + "\n")

        print("GRID:")
        print("-" * 50)

        for i in range(4):
            row = []
            for j in range(4):
                idx = i * 4 + j
                word = words[idx]
                if idx in current_selection:
                    row.append(f"{Fore.WHITE}{Style.BRIGHT}[{word:^12}]")
                else:
                    row.append(f"{Fore.WHITE}{word:^12}")
            print("  ".join(row))

        print("-" * 50)
        print("\nControls: Select 1-16, 'take' to guess, 'shuffle' to rearrange, 'quit' to exit")

    def display_found_groups(self, found_groups: List["GroupInfo"]) -> None:
        """Display found groups with their categories and difficulty colors."""
        if not found_groups:
            print("\nFound Groups: (none yet)")
            return

        print("\n" + "-" * 50)
        print("FOUND GROUPS:")
        print("-" * 50)

        for group in found_groups:
            color = DIFFICULTY_COLORS.get(group.difficulty, Fore.WHITE)
            words_str = ", ".join(group.words)
            print(f"{color}● {group.category} [{group.difficulty}]")
            print(f"  {words_str}")

        print("-" * 50)

    def get_user_input(self, current_selection: List[int]) -> "UserAction":
        """Parse user input for selection, take, shuffle, or quit."""
        selection_count = len(current_selection)

        if selection_count == 0:
            prompt = "Select word (1-16): "
        elif selection_count == 4:
            prompt = "Command (take/shuffle/quit): "
        else:
            selected_str = ", ".join(str(i + 1) for i in current_selection)
            prompt = f"Select word (1-16, current: {selected_str}): "

        user_input = input(prompt).strip().lower()

        if user_input in ("take", "t"):
            if selection_count == 4:
                return UserAction(type="take", indices=current_selection.copy())
            else:
                print(f"Must select exactly 4 words (currently {selection_count})")
                return UserAction(type="none", indices=None)

        if user_input in ("shuffle", "s"):
            return UserAction(type="shuffle", indices=None)

        if user_input in ("quit", "q", "exit"):
            return UserAction(type="quit", indices=None)

        try:
            idx = int(user_input) - 1
            if idx < 0 or idx > 15:
                print("Please enter a number between 1 and 16")
                return UserAction(type="none", indices=None)
            if idx in current_selection:
                current_selection.remove(idx)
                print(f"Removed word at position {idx + 1}")
                return UserAction(type="none", indices=None)
            if len(current_selection) >= 4:
                print("Already selected 4 words. Use 'take' to submit or remove a word.")
                return UserAction(type="none", indices=None)
            current_selection.append(idx)
            return UserAction(type="select", indices=[idx])
        except ValueError:
            print("Invalid input. Use number 1-16, 'take', 'shuffle', or 'quit'")
            return UserAction(type="none", indices=None)

    def show_feedback(self, result: "GameResult") -> None:
        """Display immediate feedback after a guess."""
        print("\n" + "=" * 50)

        if result.success:
            print(f"{Fore.GREEN}✓ CORRECT!")
            print(f"{Fore.WHITE}{result.message}")
        else:
            print(f"{Fore.RED}✗ INCORRECT")
            print(f"{Fore.WHITE}{result.message}")

        print(f"\nMistakes: {result.mistakes}/3")
        remaining = max(0, 3 - result.mistakes)
        print(f"Remaining guesses: {remaining}")

        print("=" * 50 + "\n")

    def show_game_state(self, state: "GameState") -> None:
        """Display complete game state including grid, found groups, and stats."""
        self.display_grid(state.word_grid, state.found_groups)
        self.display_found_groups(state.found_groups)

        if not state.is_complete:
            print(f"\nMistakes: {state.mistakes}/3")
            remaining = max(0, 3 - state.mistakes)
            print(f"Remaining guesses: {remaining}")
            print(f"Puzzles found: {len(state.found_groups)}/4")

    def show_error(self, message: str) -> None:
        """Display an error message."""
        print(f"\n{Fore.RED}Error: {message}\n")

    def show_shutdown(self) -> None:
        """Display shutdown message."""
        print("\nThanks for playing Word Quartet!\n")


from dataclasses import dataclass


@dataclass
class GroupInfo:
    """Represents a found group with its category and difficulty."""

    words: List[str]
    category: str
    difficulty: str


@dataclass
class GameResult:
    """Result of a player's guess."""

    success: bool
    group_info: Optional["GroupInfo"]
    message: str
    mistakes: int


@dataclass
class GameState:
    """Current state of the game."""

    word_grid: List[str]
    found_groups: List["GroupInfo"]
    mistakes: int
    remaining_guesses: int
    is_complete: bool


@dataclass
class UserAction:
    """User action from input parsing."""

    type: str
    indices: Optional[List[int]]
