"""Tests for sda graph — self-contained interactive HTML output."""

import json
import re
import yaml
import pytest
from pathlib import Path
from typer.testing import CliRunner

from sda.main import app

runner = CliRunner()


def _write_problem(inbox: Path, prob_id: str, *, services: list[str] | None = None) -> None:
    content = f"id: {prob_id}\ntitle: test\nstatus: active\n"
    if services:
        content += f"services: [{', '.join(services)}]\n"
    (inbox / f"{prob_id}.yaml").write_text(content, encoding="utf-8")


def _write_services(path: Path, services: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump({"services": services}), encoding="utf-8")


@pytest.fixture
def flat_project(tmp_path: Path) -> Path:
    (tmp_path / "architecture" / "inbox").mkdir(parents=True)
    (tmp_path / "architecture" / "model").mkdir(parents=True)
    (tmp_path / "architecture" / "adr").mkdir(parents=True)
    _write_problem(tmp_path / "architecture" / "inbox", "PROB-001", services=["api"])
    _write_services(
        tmp_path / "architecture" / "model" / "services.yaml",
        {"api": {"depends_on": ["db"]}, "db": {}},
    )
    return tmp_path


@pytest.fixture
def partitioned_project(tmp_path: Path) -> Path:
    (tmp_path / "architecture" / "inbox").mkdir(parents=True)
    (tmp_path / "architecture" / "payments" / "model").mkdir(parents=True)
    (tmp_path / "architecture" / "catalog" / "model").mkdir(parents=True)
    _write_services(tmp_path / "architecture" / "payments" / "model" / "services.yaml", {"svc-orders": {}})
    _write_services(tmp_path / "architecture" / "catalog" / "model" / "services.yaml", {"catalog-api": {}})
    return tmp_path


def _extract_elements(html: str) -> list[dict]:
    # ELEMENTS is emitted as a single JSON line: `var ELEMENTS = [...];`
    m = re.search(r"var ELEMENTS = (\[.*\]);", html)
    assert m, "ELEMENTS array not found in generated HTML"
    return json.loads(m.group(1))


class TestGraphHtml:

    def test_writes_default_output(self, flat_project: Path) -> None:
        result = runner.invoke(app, ["graph", "static", "--project-dir", str(flat_project)])
        assert result.exit_code == 0
        assert (flat_project / "architecture" / "graph.html").exists()

    def test_is_self_contained_offline(self, flat_project: Path) -> None:
        runner.invoke(app, ["graph", "static", "--project-dir", str(flat_project)])
        html = (flat_project / "architecture" / "graph.html").read_text()
        # Graph engine is inlined, not loaded from a CDN/URL
        assert "cytoscape" in html
        assert not re.search(r'<script[^>]*\bsrc\s*=', html), "no external <script src> allowed"
        assert not re.search(r'<link[^>]*\bhref\s*=\s*["\']https?:', html), "no external stylesheet"

    def test_depends_on_rendered_as_edge(self, flat_project: Path) -> None:
        runner.invoke(app, ["graph", "static", "--project-dir", str(flat_project)])
        html = (flat_project / "architecture" / "graph.html").read_text()
        elements = _extract_elements(html)
        edges = [e["data"] for e in elements if "source" in e["data"]]
        assert any(e["source"] == "api" and e["target"] == "db" and e["kind"] == "depends_on" for e in edges)
        # problem -> service "affects" edge
        assert any(e["source"] == "PROB-001" and e["target"] == "api" and e["kind"] == "affects" for e in edges)

    def test_hotspots_section_present(self, flat_project: Path) -> None:
        runner.invoke(app, ["graph", "static", "--project-dir", str(flat_project)])
        html = (flat_project / "architecture" / "graph.html").read_text()
        assert "Service hotspots" in html

    def test_custom_output_path(self, flat_project: Path, tmp_path: Path) -> None:
        out = tmp_path / "custom" / "g.html"
        result = runner.invoke(app, ["graph", "static", "--project-dir", str(flat_project), "--output", str(out)])
        assert result.exit_code == 0
        assert out.exists()

    def test_partitioned_includes_all_services(self, partitioned_project: Path) -> None:
        result = runner.invoke(app, ["graph", "static", "--project-dir", str(partitioned_project)])
        assert result.exit_code == 0
        html = (partitioned_project / "architecture" / "graph.html").read_text()
        elements = _extract_elements(html)
        node_ids = {e["data"]["id"] for e in elements if "source" not in e["data"]}
        assert {"svc-orders", "catalog-api"} <= node_ids
