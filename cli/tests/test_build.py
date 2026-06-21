"""Tests for sda build — one-command regeneration of all derived artifacts."""

import yaml
import pytest
from pathlib import Path
from typer.testing import CliRunner

from sda.main import app

runner = CliRunner()


def _write_services(path: Path, services: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump({"services": services}), encoding="utf-8")


@pytest.fixture
def flat_project(tmp_path: Path) -> Path:
    (tmp_path / "architecture" / "inbox").mkdir(parents=True)
    (tmp_path / "architecture" / "model").mkdir(parents=True)
    (tmp_path / "architecture" / "adr").mkdir(parents=True)
    (tmp_path / "architecture" / "inbox" / "PROB-001.yaml").write_text(
        "id: PROB-001\ntitle: test\nstatus: active\nservices: [api]\n", encoding="utf-8"
    )
    _write_services(tmp_path / "architecture" / "model" / "services.yaml", {"api": {"depends_on": ["db"]}, "db": {}})
    return tmp_path


class TestBuild:

    def test_produces_index_and_graph(self, flat_project: Path) -> None:
        result = runner.invoke(app, ["build", "--project-dir", str(flat_project)])
        assert result.exit_code == 0
        assert (flat_project / "architecture" / "index.yaml").exists()
        assert (flat_project / "architecture" / "graph.html").exists()

    def test_index_reflects_depends_on(self, flat_project: Path) -> None:
        result = runner.invoke(app, ["build", "--project-dir", str(flat_project)])
        assert result.exit_code == 0
        data = yaml.safe_load((flat_project / "architecture" / "index.yaml").read_text())
        assert data["graph"]["api"]["depends_on"] == ["db"]
