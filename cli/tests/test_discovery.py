"""Tests for sda.discovery — inbox problem discovery, service model loading, partition discovery."""

import pytest
from pathlib import Path

from sda.discovery import (
    discover_partitions,
    discover_problem_files,
    discover_max_prob_id,
    discover_service_files,
    load_all_services,
)


# ── Fixtures ──────────────────────────────────────────────────


@pytest.fixture
def inbox(tmp_path: Path) -> Path:
    d = tmp_path / "architecture" / "inbox"
    d.mkdir(parents=True)
    return d


@pytest.fixture
def model_dir(tmp_path: Path) -> Path:
    d = tmp_path / "architecture" / "model"
    d.mkdir(parents=True)
    return d


def _write_prob(inbox: Path, prob_id: str, *, folder: bool = False) -> Path:
    """Helper to write a minimal problem YAML."""
    content = f"id: {prob_id}\ntitle: test\nstatus: active\n"
    if folder:
        d = inbox / prob_id
        d.mkdir(exist_ok=True)
        f = d / f"{prob_id}.yaml"
    else:
        f = inbox / f"{prob_id}.yaml"
    f.write_text(content, encoding="utf-8")
    return f


def _write_services(path: Path, services: dict[str, dict | None]) -> None:
    """Helper to write a services.yaml at the given path."""
    import yaml

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump({"services": services}), encoding="utf-8")


# ── discover_problem_files ────────────────────────────────────


class TestDiscoverProblemFiles:

    def test_empty_inbox(self, inbox: Path) -> None:
        assert discover_problem_files(inbox) == []

    def test_nonexistent_inbox(self, tmp_path: Path) -> None:
        assert discover_problem_files(tmp_path / "no-such") == []

    def test_flat_layout(self, inbox: Path) -> None:
        _write_prob(inbox, "PROB-001")
        _write_prob(inbox, "PROB-002")
        result = discover_problem_files(inbox)
        assert len(result) == 2
        assert result[0].name == "PROB-001.yaml"
        assert result[1].name == "PROB-002.yaml"

    def test_folder_layout(self, inbox: Path) -> None:
        _write_prob(inbox, "PROB-001", folder=True)
        _write_prob(inbox, "PROB-002", folder=True)
        result = discover_problem_files(inbox)
        assert len(result) == 2
        assert result[0].name == "PROB-001.yaml"
        assert result[1].name == "PROB-002.yaml"

    def test_mixed_layout(self, inbox: Path) -> None:
        _write_prob(inbox, "PROB-001")
        _write_prob(inbox, "PROB-002", folder=True)
        result = discover_problem_files(inbox)
        assert len(result) == 2

    def test_duplicate_raises(self, inbox: Path) -> None:
        _write_prob(inbox, "PROB-001")
        _write_prob(inbox, "PROB-001", folder=True)
        with pytest.raises(ValueError, match="PROB-001"):
            discover_problem_files(inbox)

    def test_template_ignored(self, inbox: Path) -> None:
        (inbox / "PROB-TEMPLATE.yaml").write_text("template: true\n")
        _write_prob(inbox, "PROB-001")
        result = discover_problem_files(inbox)
        assert len(result) == 1


# ── discover_max_prob_id ──────────────────────────────────────


class TestDiscoverMaxProbId:

    def test_empty_inbox(self, inbox: Path) -> None:
        assert discover_max_prob_id(inbox) == 0

    def test_nonexistent_inbox(self, tmp_path: Path) -> None:
        assert discover_max_prob_id(tmp_path / "no-such") == 0

    def test_flat_only(self, inbox: Path) -> None:
        _write_prob(inbox, "PROB-001")
        _write_prob(inbox, "PROB-003")
        assert discover_max_prob_id(inbox) == 3

    def test_folder_only(self, inbox: Path) -> None:
        _write_prob(inbox, "PROB-005", folder=True)
        assert discover_max_prob_id(inbox) == 5

    def test_mixed_picks_highest(self, inbox: Path) -> None:
        _write_prob(inbox, "PROB-002")
        _write_prob(inbox, "PROB-007", folder=True)
        assert discover_max_prob_id(inbox) == 7


# ── discover_service_files ────────────────────────────────────


class TestDiscoverServiceFiles:

    def test_nonexistent_dir(self, tmp_path: Path) -> None:
        assert discover_service_files(tmp_path / "nope") == []

    def test_root_only(self, model_dir: Path) -> None:
        _write_services(model_dir / "services.yaml", {"svc-a": {}})
        result = discover_service_files(model_dir)
        assert len(result) == 1
        assert result[0][0] is None  # group=None for root

    def test_subdirectory(self, model_dir: Path) -> None:
        _write_services(model_dir / "group-a" / "services.yaml", {"svc-x": {}})
        result = discover_service_files(model_dir)
        assert len(result) == 1
        assert result[0][0] == "group-a"

    def test_root_and_subdirectory(self, model_dir: Path) -> None:
        _write_services(model_dir / "services.yaml", {"svc-a": {}})
        _write_services(model_dir / "group-b" / "services.yaml", {"svc-b": {}})
        result = discover_service_files(model_dir)
        assert len(result) == 2
        groups = [r[0] for r in result]
        assert None in groups
        assert "group-b" in groups


# ── load_all_services ─────────────────────────────────────────


class TestLoadAllServices:

    def test_empty(self, model_dir: Path) -> None:
        all_svcs, groups, errors = load_all_services(model_dir)
        assert all_svcs == {}
        assert groups == {}
        assert errors == []

    def test_root_services(self, model_dir: Path) -> None:
        _write_services(model_dir / "services.yaml", {
            "svc-a": {"last_reviewed": "2025-01-01"},
            "svc-b": None,
        })
        all_svcs, groups, errors = load_all_services(model_dir)
        assert len(all_svcs) == 2
        assert all_svcs["svc-a"]["_group"] is None
        assert groups == {}
        assert errors == []

    def test_grouped_services(self, model_dir: Path) -> None:
        _write_services(model_dir / "infra" / "services.yaml", {
            "svc-x": {"last_reviewed": "2025-06-01"},
        })
        all_svcs, groups, errors = load_all_services(model_dir)
        assert all_svcs["svc-x"]["_group"] == "infra"
        assert "infra" in groups
        assert "svc-x" in groups["infra"]

    def test_duplicate_service_across_files(self, model_dir: Path) -> None:
        _write_services(model_dir / "services.yaml", {"svc-dup": {}})
        _write_services(model_dir / "group-a" / "services.yaml", {"svc-dup": {}})
        all_svcs, groups, errors = load_all_services(model_dir)
        assert len(errors) == 1
        assert "svc-dup" in errors[0]
        # First-seen wins
        assert all_svcs["svc-dup"]["_group"] is None

    def test_merge_root_and_group(self, model_dir: Path) -> None:
        _write_services(model_dir / "services.yaml", {"svc-root": {}})
        _write_services(model_dir / "apps" / "services.yaml", {"svc-app": {}})
        all_svcs, groups, errors = load_all_services(model_dir)
        assert len(all_svcs) == 2
        assert all_svcs["svc-root"]["_group"] is None
        assert all_svcs["svc-app"]["_group"] == "apps"
        assert errors == []


# ── discover_partitions ───────────────────────────────────────


@pytest.fixture
def arch_dir(tmp_path: Path) -> Path:
    d = tmp_path / "architecture"
    d.mkdir()
    return d


class TestDiscoverPartitions:

    def test_nonexistent_dir(self, tmp_path: Path) -> None:
        assert discover_partitions(tmp_path / "no-arch") == []

    def test_empty_dir(self, arch_dir: Path) -> None:
        assert discover_partitions(arch_dir) == []

    def test_dir_with_model_is_partition(self, arch_dir: Path) -> None:
        (arch_dir / "payments" / "model").mkdir(parents=True)
        result = discover_partitions(arch_dir)
        assert len(result) == 1
        assert result[0][0] == "payments"

    def test_dir_with_adr_is_partition(self, arch_dir: Path) -> None:
        (arch_dir / "catalog" / "adr").mkdir(parents=True)
        result = discover_partitions(arch_dir)
        assert len(result) == 1
        assert result[0][0] == "catalog"

    def test_dir_without_model_or_adr_not_partition(self, arch_dir: Path) -> None:
        (arch_dir / "docs").mkdir()
        (arch_dir / "docs" / "readme.md").write_text("hi")
        assert discover_partitions(arch_dir) == []

    def test_reserved_names_excluded(self, arch_dir: Path) -> None:
        for name in ("inbox", "model", "adr"):
            (arch_dir / name / "model").mkdir(parents=True)
        assert discover_partitions(arch_dir) == []

    def test_sorted_alphabetically(self, arch_dir: Path) -> None:
        (arch_dir / "zebra" / "model").mkdir(parents=True)
        (arch_dir / "alpha" / "adr").mkdir(parents=True)
        (arch_dir / "middle" / "model").mkdir(parents=True)
        result = discover_partitions(arch_dir)
        assert [r[0] for r in result] == ["alpha", "middle", "zebra"]

    def test_mixed_partitions_and_non_partitions(self, arch_dir: Path) -> None:
        (arch_dir / "payments" / "model").mkdir(parents=True)
        (arch_dir / "catalog" / "adr").mkdir(parents=True)
        (arch_dir / "docs").mkdir()  # not a partition
        (arch_dir / "inbox").mkdir()  # reserved
        result = discover_partitions(arch_dir)
        assert [r[0] for r in result] == ["catalog", "payments"]

    def test_flat_layout_no_partitions(self, arch_dir: Path) -> None:
        """Standard flat layout: model/ and adr/ at root — no partitions."""
        (arch_dir / "model").mkdir()
        (arch_dir / "adr").mkdir()
        (arch_dir / "inbox").mkdir()
        assert discover_partitions(arch_dir) == []
