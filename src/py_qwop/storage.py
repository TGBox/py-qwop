"""Persistent storage for highscores, game settings, and ghost runner data."""

import json
import os
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt


def get_data_dir() -> Path:
    """Return platform-appropriate application data directory."""
    if os.name == "nt":
        base = os.getenv("APPDATA") or str(Path.home())
        data_dir = Path(base) / "py_qwop"
    else:
        data_dir = Path.home() / ".config" / "py_qwop"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


class StorageManager:
    """Manages reading and writing highscores, configuration, and ghost runs."""

    def __init__(self):
        self.data_dir = get_data_dir()
        self.save_file = self.data_dir / "save_data.json"
        self.ghost_file = self.data_dir / "best_ghost.json"

    def load_data(self) -> dict[str, Any]:
        """Load settings and scores from disk or return sensible defaults."""
        defaults: dict[str, Any] = {
            "highscores": {
                "max_distance": 0.0,
                "best_time_100m": None,
                "total_runs": 0,
            },
            "settings": {
                "ghost_runner_enabled": True,
                "fullscreen_on_start": False,
            },
            "key_bindings": {
                "thigh_q": int(Qt.Key.Key_Q),
                "thigh_w": int(Qt.Key.Key_W),
                "calf_o": int(Qt.Key.Key_O),
                "calf_p": int(Qt.Key.Key_P),
                "restart": int(Qt.Key.Key_R),
                "fullscreen": int(Qt.Key.Key_F11),
                "pause": int(Qt.Key.Key_Escape),
            },
        }

        if not self.save_file.exists():
            return defaults

        try:
            with open(self.save_file, "r", encoding="utf-8") as f:
                saved = json.load(f)
                # Merge with defaults in case of missing keys
                for key, default_val in defaults.items():
                    if key in saved:
                        if isinstance(default_val, dict) and isinstance(saved[key], dict):
                            default_val.update(saved[key])
                        else:
                            defaults[key] = saved[key]
                return defaults
        except (OSError, json.JSONDecodeError, TypeError, KeyError):
            return defaults

    def save_data(self, data: dict[str, Any]) -> None:
        """Write current data safely to disk."""
        try:
            temp_file = self.save_file.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            temp_file.replace(self.save_file)
        except OSError as e:
            print(f"Error saving data: {e}")

    def update_record(self, distance: float, time_sec: float) -> bool:
        """Update highscore if new record is achieved. Returns True if record broken."""
        data = self.load_data()
        highscores = data["highscores"]
        highscores["total_runs"] = highscores.get("total_runs", 0) + 1
        is_new_record = False

        if distance > highscores.get("max_distance", 0.0):
            highscores["max_distance"] = round(distance, 2)
            is_new_record = True

        if distance >= 100.0:
            current_best_time = highscores.get("best_time_100m")
            if current_best_time is None or time_sec < current_best_time:
                highscores["best_time_100m"] = round(time_sec, 2)
                is_new_record = True

        self.save_data(data)
        return is_new_record

    def save_ghost(self, ghost_frames: list[dict[str, Any]]) -> None:
        """Save runner keyframe animation data for ghost runner."""
        try:
            with open(self.ghost_file, "w", encoding="utf-8") as f:
                json.dump(ghost_frames, f)
        except OSError as e:
            print(f"Error saving ghost run: {e}")

    def load_ghost(self) -> list[dict[str, Any]] | None:
        """Load recorded ghost runner frames if present."""
        if not self.ghost_file.exists():
            return None
        try:
            with open(self.ghost_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError, TypeError, KeyError):
            return None


# Global singleton instance
STORAGE = StorageManager()
