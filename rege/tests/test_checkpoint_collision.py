"""
Regression tests for recursive-engine--generative-entity#38:
same-second checkpoint ID collisions overwriting snapshots.

CheckpointManager.create_checkpoint() derived snapshot_id to whole-second
precision, so two checkpoints created within the same second shared one ID:
the second write replaced the first snapshot file while the registry kept
two entries, and loading the first name returned the second state.
"""

import re
from datetime import datetime

import pytest

import rege.persistence.checkpoint as checkpoint_mod
from rege.persistence.archive import ArchiveManager
from rege.persistence.checkpoint import CheckpointManager
from rege.core.exceptions import PersistenceError


FIXED_NOW = datetime(2026, 10, 23, 23, 15, 0)


class _FrozenDateTime(datetime):
    """datetime stub with a clock that never advances."""

    @classmethod
    def now(cls, tz=None):
        return FIXED_NOW


@pytest.fixture
def frozen_clock(monkeypatch):
    monkeypatch.setattr(checkpoint_mod, "datetime", _FrozenDateTime)


def _manager(tmp_path):
    archive = ArchiveManager(str(tmp_path / "archive"))
    return CheckpointManager(archive)


def _state(tag):
    return {"metrics": {"tag": tag}, "organs": {}, "pending": [], "errors": []}


def test_same_second_checkpoints_get_distinct_ids_and_files(frozen_clock, tmp_path):
    """Two checkpoints at the identical wall-clock instant: distinct stable IDs, distinct files."""
    manager = _manager(tmp_path)

    first = manager.create_checkpoint("first", _state("FIRST"))
    second = manager.create_checkpoint("second", _state("SECOND"))

    assert first.snapshot_id != second.snapshot_id
    assert re.fullmatch(r"SNAP_20261023_231500_\d{3}", first.snapshot_id)
    assert re.fullmatch(r"SNAP_20261023_231500_\d{3}", second.snapshot_id)
    assert (manager._snapshots_dir / f"{first.snapshot_id}.json").exists()
    assert (manager._snapshots_dir / f"{second.snapshot_id}.json").exists()


def test_same_second_registry_entries_resolve_to_own_state(frozen_clock, tmp_path):
    """Each registry entry resolves to its own saved state; no stale-name aliasing."""
    manager = _manager(tmp_path)

    first = manager.create_checkpoint("first", _state("FIRST"))
    second = manager.create_checkpoint("second", _state("SECOND"))

    registry = manager.list_checkpoints()
    assert len(registry) == 2

    loaded_first = manager.get_checkpoint_by_name("first")
    loaded_second = manager.get_checkpoint_by_name("second")
    assert loaded_first.snapshot_id == first.snapshot_id
    assert loaded_second.snapshot_id == second.snapshot_id
    assert loaded_first.system_state["tag"] == "FIRST"
    assert loaded_second.system_state["tag"] == "SECOND"


def test_sequence_continues_across_manager_instances(frozen_clock, tmp_path):
    """A new manager on the same archive dir must not reuse an allocated ID."""
    manager = _manager(tmp_path)
    first = manager.create_checkpoint("first", _state("FIRST"))

    restarted = _manager(tmp_path)
    second = restarted.create_checkpoint("second", _state("SECOND"))

    assert second.snapshot_id != first.snapshot_id
    assert len(restarted.list_checkpoints()) == 2
    assert restarted.get_checkpoint_by_name("first").system_state["tag"] == "FIRST"


def test_failed_snapshot_write_creates_no_registry_entry(tmp_path, monkeypatch):
    """Fail closed: a failed snapshot write must not leave a registry entry."""
    manager = _manager(tmp_path)

    def _boom(snapshot):
        raise PersistenceError("simulated disk failure")

    monkeypatch.setattr(manager, "_save_snapshot", _boom)

    with pytest.raises(PersistenceError):
        manager.create_checkpoint("doomed", _state("DOOMED"))

    assert manager.list_checkpoints() == []


def test_preexisting_legacy_id_does_not_collide(frozen_clock, tmp_path):
    """An old-format (unsuffixed) snapshot on disk does not break allocation."""
    manager = _manager(tmp_path)
    legacy_path = manager._snapshots_dir / "SNAP_20261023_231500.json"
    legacy_path.write_text("{}", encoding="utf-8")

    created = manager.create_checkpoint("new", _state("NEW"))

    assert created.snapshot_id != "SNAP_20261023_231500"
    assert (manager._snapshots_dir / f"{created.snapshot_id}.json").exists()
