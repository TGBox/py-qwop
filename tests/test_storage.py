"""Unit tests for persistent storage, highscore records, and ghost trajectory data."""

from py_qwop.storage import StorageManager


def test_storage_defaults(tmp_path):
    """Test fallback to defaults when no save file exists."""
    storage = StorageManager()
    storage.data_dir = tmp_path
    storage.save_file = tmp_path / "test_save.json"
    storage.ghost_file = tmp_path / "test_ghost.json"

    data = storage.load_data()
    assert "highscores" in data
    assert "settings" in data
    assert "key_bindings" in data
    assert data["highscores"]["max_distance"] == 0.0


def test_storage_update_records_and_ghost(tmp_path):
    """Test record breaking logic and ghost serialization."""
    storage = StorageManager()
    storage.data_dir = tmp_path
    storage.save_file = tmp_path / "test_save.json"
    storage.ghost_file = tmp_path / "test_ghost.json"

    # Set new distance record
    is_rec = storage.update_record(distance=24.5, time_sec=12.0)
    assert is_rec
    data = storage.load_data()
    assert data["highscores"]["max_distance"] == 24.5

    # Run that does not break distance record
    is_rec_2 = storage.update_record(distance=15.0, time_sec=8.0)
    assert not is_rec_2

    # Run reaching 100m finish line
    is_win_rec = storage.update_record(distance=102.0, time_sec=55.0)
    assert is_win_rec
    data = storage.load_data()
    assert data["highscores"]["best_time_100m"] == 55.0

    # Save and load ghost runner
    fake_ghost = [{"t": 0.0, "torso": [0.0, 1.2, 0.0]}, {"t": 0.1, "torso": [0.1, 1.2, 0.0]}]
    storage.save_ghost(fake_ghost)
    loaded_ghost = storage.load_ghost()
    assert loaded_ghost is not None
    assert len(loaded_ghost) == 2
    assert loaded_ghost[1]["t"] == 0.1
