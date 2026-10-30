"""
High score persistence manager for GestureDino AI.
Safely stores and retrieves the all-time local record using a JSON file.
"""

from pathlib import Path
import json
import os

DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_HIGH_SCORE_FILE = DEFAULT_DATA_DIR / "high_score.json"


def load_high_score(file_path: Path = DEFAULT_HIGH_SCORE_FILE) -> int:
    """
    Load the persistent high score.
    Returns 0 if the file is missing, invalid, or unreadable.
    """
    try:
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return int(data.get("high_score", 0))
    except (json.JSONDecodeError, OSError, ValueError):
        return 0
    return 0


def save_high_score(score: int, file_path: Path = DEFAULT_HIGH_SCORE_FILE) -> bool:
    """
    Save the new high score persistently.
    Returns True if successfully written, False otherwise.
    """
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        # Atomic-style temporary write then replace to protect against file corruption
        temp_file = file_path.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump({"high_score": int(score)}, f, indent=2)
        os.replace(temp_file, file_path)
        return True
    except OSError:
        return False
