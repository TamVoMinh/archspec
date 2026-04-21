"""Tests for sda check — partitioned and flat mode validation."""

import yaml
import pytest
from pathlib import Path
from typer.testing import CliRunner

from sda.main import app

runner = CliRunner()


def _write_problem(inbox: Path, prob_id: str, *, system: str | None = None, status: str = "active") -> None:
    content = {"id": prob_id, "title": "test", "status": status, "source": "adhoc", "type": "other", "created_at": "2026-04-21", "services": [], "symptoms": []}
    if system:
        content["system"] = system
    (inbox / f"{prob_id}.yaml").write_text(yaml.dump(content), encoding="utf-8")


def _write_services(path: Path, services: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump({"services": services}), encoding="utf-8")


@pytest.fixture
def flat_project(tmp_path: Path) -> Path:
    (tmp_path / "architecture" / "inbox").mkdir(parents=True)
    (tmp_path / "architecture" / "model").mkdir(parents=True)
    (tmp_path / "architecture" / "adr").mkdir(parents=True)
    return tmp_path


@pytest.fixture
def partitioned_project(tmp_path: Path) -> Path:
    (tmp_path / "architecture" / "inbox").mkdir(parents=True)
    (tmp_path / "architecture" / "payments" / "model").mkdir(parents=True)
    (tmp_path / "architecture" / "payments" / "adr").mkdir(parents=True)
    (tmp_path / "architecture" / "catalog" / "model").mkdir(parents=True)
    (tmp_path / "architecture" / "adr").mkdir(parents=True)
    return tmp_path


class TestFlatCheck:

    def test_passes_on_empty_flat(self, flat_project: Path) -> None:
        _write_services(flat_project / "architecture" / "model" / "services.yaml", {})
        result = runner.invoke(app, ["check", "--project-dir", str(flat_project)])
        # No OWNERS.yaml → error, but check runs
        assert result.exit_code == 0

    def test_backward_compat_no_system_validation(self, flat_project: Path) -> None:
        """In flat mode, problems without system: field should NOT trigger warnings."""
        _write_services(flat_project / "architecture" / "model" / "services.yaml", {})
        _write_problem(flat_project / "architecture" / "inbox", "PROB-001")
        result = runner.invoke(app, ["check", "--project-dir", str(flat_project)])
        assert "system:" not in result.output


class TestPartitionedCheck:

    def test_warns_missing_system(self, partitioned_project: Path) -> None:
        _write_services(partitioned_project / "architecture" / "payments" / "model" / "services.yaml", {})
        _write_services(partitioned_project / "architecture" / "catalog" / "model" / "services.yaml", {})
        _write_problem(partitioned_project / "architecture" / "inbox", "PROB-001")
        result = runner.invoke(app, ["check", "--project-dir", str(partitioned_project)])
        assert "has no system: field" in result.output

    def test_warns_system_mismatch(self, partitioned_project: Path) -> None:
        _write_services(partitioned_project / "architecture" / "payments" / "model" / "services.yaml", {})
        _write_services(partitioned_project / "architecture" / "catalog" / "model" / "services.yaml", {})
        _write_problem(partitioned_project / "architecture" / "inbox", "PROB-001", system="nonexistent")
        result = runner.invoke(app, ["check", "--project-dir", str(partitioned_project)])
        assert "nonexistent" in result.output and "match any partition" in result.output

    def test_no_warning_for_valid_system(self, partitioned_project: Path) -> None:
        _write_services(partitioned_project / "architecture" / "payments" / "model" / "services.yaml", {})
        _write_services(partitioned_project / "architecture" / "catalog" / "model" / "services.yaml", {})
        _write_problem(partitioned_project / "architecture" / "inbox", "PROB-001", system="payments")
        result = runner.invoke(app, ["check", "--project-dir", str(partitioned_project)])
        assert "system:" not in result.output

    def test_per_partition_service_validation(self, partitioned_project: Path) -> None:
        _write_services(partitioned_project / "architecture" / "payments" / "model" / "services.yaml", {"svc-orders": {"last_reviewed": "2020-01-01"}})
        _write_services(partitioned_project / "architecture" / "catalog" / "model" / "services.yaml", {})
        result = runner.invoke(app, ["check", "--project-dir", str(partitioned_project)])
        assert "payments" in result.output
        assert "STALE" in result.output

    def test_root_model_ignored_when_partitions_exist(self, partitioned_project: Path) -> None:
        """Root architecture/model/services.yaml should not be checked in partitioned mode."""
        # Create a stale service in root model dir (leftover from flat layout)
        root_model = partitioned_project / "architecture" / "model"
        root_model.mkdir(parents=True, exist_ok=True)
        _write_services(root_model / "services.yaml", {"stale-svc": {"last_reviewed": "2020-01-01"}})

        # Partition services are fine
        _write_services(partitioned_project / "architecture" / "payments" / "model" / "services.yaml", {})
        _write_services(partitioned_project / "architecture" / "catalog" / "model" / "services.yaml", {})

        result = runner.invoke(app, ["check", "--project-dir", str(partitioned_project)])
        assert "stale-svc" not in result.output
