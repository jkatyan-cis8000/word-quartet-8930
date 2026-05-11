"""Core puzzle logic for Word Quartet."""

import hashlib
from datetime import datetime
from typing import List, Tuple, Optional, NamedTuple

from src.data.word_groups import WORD_GROUPS, DIFFICULTY


GroupInfo = NamedTuple("GroupInfo", [
    ("words", List[str]),
    ("category", str),
    ("difficulty", str)
])

PuzzleSolution = Tuple[List[str], str, str]


class Puzzle:
    """Core puzzle logic for Word Quartet."""

    def __init__(self, word_grid: List[str]):
        """
        Initialize puzzle with 16 words.
        
        Args:
            word_grid: List of 16 words to form the puzzle grid
        """
        if len(word_grid) != 16:
            raise ValueError("Word grid must contain exactly 16 words")
        self._word_grid = word_grid
        self._solution = self._find_solution()
        self._found_groups: List[List[str]] = []
        self._found_categories: set = set()

    def _find_solution(self) -> List[PuzzleSolution]:
        """
        Find the correct groupings from the word grid.
        
        Returns:
            List of tuples containing (word_group, category, difficulty)
        """
        grid_set = set(self._word_grid)
        solution = []
        
        for words, category, difficulty in WORD_GROUPS:
            if set(words).issubset(grid_set):
                solution.append((words, category, difficulty))
        
        if len(solution) != 4:
            raise ValueError("Could not find exactly 4 valid groups in the word grid")
        
        return solution

    def get_solution(self) -> List[GroupInfo]:
        """
        Get the complete solution for the puzzle.
        
        Returns:
            List of GroupInfo tuples (words, category, difficulty)
        """
        return [GroupInfo(words, category, difficulty) 
                for words, category, difficulty in self._solution]

    def validate_group(self, words: List[str]) -> Tuple[bool, Optional[GroupInfo]]:
        """
        Check if a group of 4 words forms a valid solution.
        
        Args:
            words: List of 4 words to validate
            
        Returns:
            Tuple of (is_valid, GroupInfo if valid, None otherwise)
        """
        if len(words) != 4:
            return False, None
        
        words_set = set(words)
        
        for solution_words, category, difficulty in self._solution:
            if set(solution_words) == words_set:
                return True, GroupInfo(list(words_set), category, difficulty)
        
        return False, None

    def get_remaining_words(self) -> List[str]:
        """
        Get words that haven't been grouped correctly yet.
        
        Returns:
            List of words not yet found in correct groups
        """
        found_words = set()
        for group in self._found_groups:
            found_words.update(group)
        
        return [word for word in self._word_grid if word not in found_words]

    def is_complete(self) -> bool:
        """
        Check if all groups have been found.
        
        Returns:
            True if puzzle is solved, False otherwise
        """
        return len(self._found_groups) == 4

    def mark_group_found(self, words: List[str]) -> bool:
        """
        Mark a group as found (internal use by Game class).
        
        Args:
            words: The 4 words that were correctly grouped
            
        Returns:
            True if group was valid and marked, False otherwise
        """
        is_valid, group_info = self.validate_group(words)
        if is_valid and group_info:
            words_set = frozenset(words)
            if words_set not in [frozenset(g) for g in self._found_groups]:
                self._found_groups.append(list(words_set))
                return True
        return False


def generate_daily_puzzle(date: Optional[datetime] = None) -> Puzzle:
    """
    Generate a daily puzzle based on the current date.
    
    Uses a deterministic seed from the date to select words,
    ensuring all players get the same puzzle for a given day.
    
    Args:
        date: The date to generate puzzle for (defaults to today)
        
    Returns:
        Puzzle instance with 16 words and their solution
    """
    if date is None:
        date = datetime.now()
    
    date_str = date.strftime("%Y-%m-%d")
    date_hash = hashlib.md5(date_str.encode()).hexdigest()
    
    hash_value = int(date_hash[:8], 16)
    
    offset = hash_value % (len(WORD_GROUPS) - 4)
    
    selected_groups = []
    for i in range(4):
        group_idx = (offset + i * 7) % len(WORD_GROUPS)
        selected_groups.append(WORD_GROUPS[group_idx])
    
    all_words = []
    for words, _, _ in selected_groups:
        all_words.extend(words)
    
    return Puzzle(all_words)
