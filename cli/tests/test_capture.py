"""Tests for sda capture command — including --attach and folder layout."""

import pytest
from pathlib import Path
from typer.testing import CliRunner

from sda.main import app


runner = CliRunner()


@pytest.fixture
def project(tmp_path: Path) -> Path:
    """Create a minimal project directory."""
    (tmp_path / "architecture" / "inbox").mkdir(parents=True)
    return tmp_path


class TestCaptureBasic:

    def test_creates_flat_file(self, project: Path) -> None:
        result = runner.invoke(app, ["capture", "Test problem title", "--project-dir", str(project)])
        assert result.exit_code == 0
        assert "PROB-001" in result.output
        assert (project / "architecture" / "inbox" / "PROB-001.yaml").exists()

    def test_rejects_short_title(self, project: Path) -> None:
        result = runner.invoke(app, ["capture", "Hi", "--project-dir", str(project)])
        assert result.exit_code == 1

    def test_rejects_invalid_source(self, project: Path) -> None:
        result = runner.invoke(app, ["capture", "Valid title here", "--source", "invalid", "--project-dir", str(project)])
        assert result.exit_code == 1

    def test_rejects_invalid_type(self, project: Path) -> None:
        result = runner.invoke(app, ["capture", "Valid title here", "--type", "invalid", "--project-dir", str(project)])
        assert result.exit_code == 1

    def test_increments_id(self, project: Path) -> None:
        runner.invoke(app, ["capture", "First problem", "--project-dir", str(project)])
        result = runner.invoke(app, ["capture", "Second problem", "--project-dir", str(project)])
        assert result.exit_code == 0
        assert "PROB-002" in result.output


class TestCaptureAttach:

    def test_creates_folder_with_attachment(self, project: Path, tmp_path: Path) -> None:
        att = tmp_path / "evidence.txt"
        att.write_text("evidence content")

        result = runner.invoke(app, [
            "capture", "Problem with evidence",
            "--attach", str(att),
            "--project-dir", str(project),
        ])
        assert result.exit_code == 0
        assert "PROB-001" in result.output

        folder = project / "architecture" / "inbox" / "PROB-001"
        assert folder.is_dir()
        assert (folder / "PROB-001.yaml").exists()
        assert (folder / "attachments" / "evidence.txt").exists()

    def test_multiple_attachments(self, project: Path, tmp_path: Path) -> None:
        att1 = tmp_path / "file1.pdf"
        att2 = tmp_path / "file2.msg"
        att1.write_text("pdf")
        att2.write_text("msg")

        result = runner.invoke(app, [
            "capture", "Problem with multiple files",
            "--attach", str(att1),
            "--attach", str(att2),
            "--project-dir", str(project),
        ])
        assert result.exit_code == 0
        att_dir = project / "architecture" / "inbox" / "PROB-001" / "attachments"
        assert (att_dir / "file1.pdf").exists()
        assert (att_dir / "file2.msg").exists()

    def test_rejects_missing_attachment(self, project: Path) -> None:
        result = runner.invoke(app, [
            "capture", "Problem with bad file",
            "--attach", "/nonexistent/file.txt",
            "--project-dir", str(project),
        ])
        assert result.exit_code == 1

    def test_id_accounts_for_folder_layout(self, project: Path, tmp_path: Path) -> None:
        """When PROB-001 exists as a folder, next should be PROB-002."""
        att = tmp_path / "doc.txt"
        att.write_text("doc")

        # Create first with attachment (folder layout)
        runner.invoke(app, [
            "capture", "First with attach",
            "--attach", str(att),
            "--project-dir", str(project),
        ])

        # Second without attachment (flat layout)
        result = runner.invoke(app, [
            "capture", "Second flat problem",
            "--project-dir", str(project),
        ])
        assert result.exit_code == 0
        assert "PROB-002" in result.output


class TestCaptureSystem:

    def test_with_system_flag(self, project: Path) -> None:
        result = runner.invoke(app, [
            "capture", "Problem in payments",
            "--system", "payments",
            "--project-dir", str(project),
        ])
        assert result.exit_code == 0
        content = (project / "architecture" / "inbox" / "PROB-001.yaml").read_text()
        assert "system: payments" in content

    def test_without_system_flag(self, project: Path) -> None:
        result = runner.invoke(app, [
            "capture", "Problem without system",
            "--project-dir", str(project),
        ])
        assert result.exit_code == 0
        content = (project / "architecture" / "inbox" / "PROB-001.yaml").read_text()
        assert "system:" not in content
