"""Tests for sda status — partitioned and flat mode display."""

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
    (tmp_path / "architecture" / "catalog" / "model").mkdir(parents=True)
    (tmp_path / "architecture" / "adr").mkdir(parents=True)
    return tmp_path


class TestFlatStatus:

    def test_shows_flat_panel(self, flat_project: Path) -> None:
        _write_services(flat_project / "architecture" / "model" / "services.yaml", {})
        result = runner.invoke(app, ["status", "--project-dir", str(flat_project)])
        assert result.exit_code == 0
        assert "ArchSpec Status" in result.output
        assert "Systems" not in result.output


class TestPartitionedStatus:

    def test_shows_partition_table(self, partitioned_project: Path) -> None:
        _write_services(partitioned_project / "architecture" / "payments" / "model" / "services.yaml", {"svc-orders": {}})
        _write_services(partitioned_project / "architecture" / "catalog" / "model" / "services.yaml", {})
        result = runner.invoke(app, ["status", "--project-dir", str(partitioned_project)])
        assert result.exit_code == 0
        assert "payments" in result.output
        assert "catalog" in result.output

    def test_shows_systems_count(self, partitioned_project: Path) -> None:
        _write_services(partitioned_project / "architecture" / "payments" / "model" / "services.yaml", {})
        _write_services(partitioned_project / "architecture" / "catalog" / "model" / "services.yaml", {})
        result = runner.invoke(app, ["status", "--project-dir", str(partitioned_project)])
        assert "Systems: 2" in result.output

    def test_shows_unrouted_count(self, partitioned_project: Path) -> None:
        _write_services(partitioned_project / "architecture" / "payments" / "model" / "services.yaml", {})
        _write_services(partitioned_project / "architecture" / "catalog" / "model" / "services.yaml", {})
        inbox = partitioned_project / "architecture" / "inbox"
        _write_problem(inbox, "PROB-001", system="payments")
        _write_problem(inbox, "PROB-002")  # unrouted
        result = runner.invoke(app, ["status", "--project-dir", str(partitioned_project)])
        assert "1 unrouted" in result.output
