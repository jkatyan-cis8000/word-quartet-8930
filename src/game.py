"""Game state management for Word Quartet puzzle game."""

from typing import List, Optional, Tuple

from src.data.word_groups import WORD_GROUPS, DIFFICULTY
from src.puzzle import Puzzle, GroupInfo, generate_daily_puzzle


class GameState:
    """Current state of the Word Quartet game."""

    def __init__(
        self,
        word_grid: List[str],
        found_groups: Optional[List[GroupInfo]] = None,
        mistakes: int = 0,
        max_mistakes: int = 4,
    ):
        """
        Initialize game state.

        Args:
            word_grid: List of 16 words forming the puzzle grid
            found_groups: List of already found GroupInfo (optional)
            mistakes: Number of incorrect guesses made
            max_mistakes: Maximum allowed mistakes before game over
        """
        self.puzzle = Puzzle(word_grid)
        self.found_groups = found_groups or []
        self.mistakes = mistakes
        self.max_mistakes = max_mistakes

    @property
    def word_grid(self) -> List[str]:
        """Get the current word grid."""
        return self.puzzle._word_grid

    @property
    def remaining_guesses(self) -> int:
        """Get remaining guesses before game over."""
        return max(0, self.max_mistakes - self.mistakes)

    @property
    def is_complete(self) -> bool:
        """Check if all groups have been found."""
        return len(self.found_groups) == 4

    @property
    def is_game_over(self) -> bool:
        """Check if game is over (either complete or too many mistakes)."""
        return self.is_complete or self.mistakes >= self.max_mistakes

    def submit_guess(self, words: List[str]) -> Tuple[bool, Optional[GroupInfo], str]:
        """
        Submit a guess for a group.

        Args:
            words: List of 4 words to submit

        Returns:
            Tuple of (success, group_info if correct, message)
        """
        if len(words) != 4:
            return False, None, "Must select exactly 4 words."

        is_valid, group_info = self.puzzle.validate_group(words)

        if is_valid and group_info:
            # Check if this group was already found
            words_set = frozenset(words)
            for found in self.found_groups:
                if frozenset(found.words) == words_set:
                    return False, None, "This group has already been found!"

            self.found_groups.append(group_info)
            return True, group_info, f"Correct! Found: {group_info.category}"

        self.mistakes += 1
        return False, None, "Incorrect group. Try again!"

    def get_hint(self) -> Optional[GroupInfo]:
        """
        Get a hint for an unfound group.

        Returns:
            GroupInfo of one remaining group, or None if all found
        """
        solution = self.puzzle.get_solution()
        found_sets = [frozenset(g.words) for g in self.found_groups]

        for group_info in solution:
            if frozenset(group_info.words) not in found_sets:
                return group_info

        return None


class Game:
    """Main game controller for Word Quartet."""

    def __init__(self, puzzle: Optional[Puzzle] = None, date: Optional = None):
        """
        Initialize game.

        Args:
            puzzle: Pre-created Puzzle instance (optional)
            date: Date for daily puzzle generation (defaults to today)
        """
        if puzzle:
            self.puzzle = puzzle
        else:
            self.puzzle = generate_daily_puzzle(date)

        self.state = GameState(
            word_grid=self.puzzle._word_grid,
            found_groups=[],
            mistakes=0,
            max_mistakes=4,
        )

    def submit_group(self, words: List[str]) -> Tuple[bool, Optional[GroupInfo], str]:
        """
        Submit a group guess.

        Args:
            words: List of 4 words to submit

        Returns:
            Tuple of (success, group_info if correct, message)
        """
        success, group_info, message = self.state.submit_guess(words)

        if success and group_info:
            self.puzzle.mark_group_found(words)

        return success, group_info, message

    def get_state(self) -> GameState:
        """Get current game state."""
        return self.state

    def get_remaining_groups(self) -> List[GroupInfo]:
        """Get list of remaining groups to find."""
        solution = self.puzzle.get_solution()
        found_sets = [frozenset(g.words) for g in self.state.found_groups]

        return [
            group_info
            for group_info in solution
            if frozenset(group_info.words) not in found_sets
        ]
