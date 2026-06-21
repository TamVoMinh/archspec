"""Tests for sda graph view/serve data building."""

import yaml
import pytest
from pathlib import Path

from sda.commands.viewer import build_viewer_data, _inject_data


@pytest.fixture
def project(tmp_path: Path) -> Path:
    (tmp_path / "architecture" / "inbox").mkdir(parents=True)
    (tmp_path / "architecture" / "model").mkdir(parents=True)
    (tmp_path / "architecture" / "adr").mkdir(parents=True)
    (tmp_path / "architecture" / "inbox" / "PROB-001.yaml").write_text(
        "id: PROB-001\ntitle: latency\nstatus: active\nservices: [api]\n", encoding="utf-8"
    )
    (tmp_path / "architecture" / "model" / "services.yaml").write_text(
        yaml.dump({"services": {"api": {"depends_on": ["db"]}, "db": {}}}), encoding="utf-8"
    )
    (tmp_path / "architecture" / "adr" / "ADR-001.md").write_text(
        "# ADR-001\n\n## Metadata\n- status: accepted\n- links: [PROB-001]\n\n## Affected Services\n- api\n",
        encoding="utf-8",
    )
    return tmp_path


class TestViewerData:
    def test_model_has_version_and_depends_on(self, project: Path) -> None:
        data = build_viewer_data(project)
        assert data["model"]["schemaVersion"] == 1
        assert data["model"]["graph"]["api"]["depends_on"] == ["db"]

    def test_documents_cover_node_types(self, project: Path) -> None:
        docs = build_viewer_data(project)["documents"]
        assert docs["ADR-001"]["contentType"] == "markdown"
        assert docs["PROB-001"]["contentType"] == "markdown"
        assert docs["api"]["contentType"] == "service-detail"
        # service-detail must not leak internal discovery fields
        assert "_group" not in docs["api"]["text"] and "_file" not in docs["api"]["text"]

    def test_inject_data_is_script_safe(self) -> None:
        html = _inject_data("<head></head>", {"x": "</script>"})
        assert "window.__ARCHSPEC_DATA__" in html
        # the data's </script> is escaped so it can't break out of the inline script
        assert "<\\/script>" in html
        assert '"</script>"' not in html
