"""Tests for classification labels: config, index, and sda check validation."""

import yaml
import pytest
from pathlib import Path
from typer.testing import CliRunner

from sda.main import app
from sda.classification import load_dimensions

runner = CliRunner()


def _write_services(path: Path, services: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump({"services": services}), encoding="utf-8")


def _write_owners(project: Path) -> None:
    owners = {
        "roles": {"architecture_lead": {"name": "Lead", "email": "l@x.com", "triage_sla_hours": 48}, "contributors": []},
        "triage_policy": {"inbox_sla_hours": 48, "adr_review_required_approvers": 2, "adr_acceptance_requires": "architecture_lead"},
        "domain_ownership": {},
    }
    (project / "OWNERS.yaml").write_text(yaml.dump(owners), encoding="utf-8")


@pytest.fixture
def project(tmp_path: Path) -> Path:
    (tmp_path / "architecture" / "inbox").mkdir(parents=True)
    (tmp_path / "architecture" / "model").mkdir(parents=True)
    (tmp_path / "architecture" / "adr").mkdir(parents=True)
    _write_owners(tmp_path)
    return tmp_path


class TestDimensions:
    def test_defaults(self, project: Path) -> None:
        dims = load_dimensions(project)
        assert dims["area"]["values"] is None  # open
        assert dims["criticality"]["values"] is None  # open (not DDD-flavored by default)
        assert "active" in dims["lifecycle"]["values"]  # neutral default vocab

    def test_config_closes_a_vocabulary(self, project: Path) -> None:
        (project / "architecture" / "classification.yaml").write_text(
            yaml.dump({"dimensions": {"criticality": {"values": ["core", "supporting", "generic"]}}}), encoding="utf-8"
        )
        dims = load_dimensions(project)
        assert dims["criticality"]["values"] == ["core", "supporting", "generic"]


class TestIndexLabels:
    def test_labels_appear_on_nodes(self, project: Path) -> None:
        _write_services(project / "architecture" / "model" / "services.yaml", {"api": {"labels": {"area": "payments"}}})
        result = runner.invoke(app, ["index", "--project-dir", str(project)])
        assert result.exit_code == 0
        data = yaml.safe_load((project / "architecture" / "index.yaml").read_text())
        assert data["graph"]["api"]["labels"] == {"area": "payments"}


class TestCheckLabels:
    def test_open_dimension_accepts_any_value(self, project: Path) -> None:
        _write_services(project / "architecture" / "model" / "services.yaml", {"api": {"labels": {"area": "anything"}}})
        result = runner.invoke(app, ["check", "--strict", "--project-dir", str(project)])
        assert result.exit_code == 0

    def test_closed_vocab_violation_is_error(self, project: Path) -> None:
        (project / "architecture" / "classification.yaml").write_text(
            yaml.dump({"dimensions": {"criticality": {"values": ["core", "supporting", "generic"]}}}), encoding="utf-8"
        )
        _write_services(project / "architecture" / "model" / "services.yaml", {"api": {"labels": {"criticality": "wrong"}}})
        result = runner.invoke(app, ["check", "--strict", "--project-dir", str(project)])
        assert result.exit_code == 1
        assert "not in allowed values" in " ".join(result.output.split())

    def test_unknown_dimension_warns(self, project: Path) -> None:
        _write_services(project / "architecture" / "model" / "services.yaml", {"api": {"labels": {"nope": "x"}}})
        result = runner.invoke(app, ["check", "--strict", "--project-dir", str(project)])
        assert result.exit_code == 0  # warning, not error
        assert "unknown classification dimension" in " ".join(result.output.split())

    def test_no_labels_is_clean(self, project: Path) -> None:
        _write_services(project / "architecture" / "model" / "services.yaml", {"api": {}})
        result = runner.invoke(app, ["check", "--strict", "--project-dir", str(project)])
        assert result.exit_code == 0

    def test_adr_labels_validated(self, project: Path) -> None:
        (project / "architecture" / "classification.yaml").write_text(
            yaml.dump({"dimensions": {"criticality": {"values": ["core", "supporting", "generic"]}}}), encoding="utf-8"
        )
        _write_services(project / "architecture" / "model" / "services.yaml", {"api": {}})
        (project / "architecture" / "adr" / "ADR-001.md").write_text(
            "# ADR-001: X\n\n## Metadata\n- status: accepted\n- labels: criticality=bogus\n\n## Affected Services\n- api\n",
            encoding="utf-8",
        )
        result = runner.invoke(app, ["check", "--strict", "--project-dir", str(project)])
        assert result.exit_code == 1
        assert "ADR" in result.output and "not in allowed values" in " ".join(result.output.split())


class TestPartitionLabels:
    @pytest.fixture
    def partitioned(self, tmp_path: Path) -> Path:
        (tmp_path / "architecture" / "inbox").mkdir(parents=True)
        (tmp_path / "architecture" / "payments" / "model").mkdir(parents=True)
        _write_services(tmp_path / "architecture" / "payments" / "model" / "services.yaml", {"billing": {}})
        _write_owners(tmp_path)
        return tmp_path

    def test_partition_label_in_manifest(self, partitioned: Path) -> None:
        (partitioned / "architecture" / "payments" / "partition.yaml").write_text(
            yaml.dump({"labels": {"criticality": "core"}}), encoding="utf-8"
        )
        result = runner.invoke(app, ["index", "--project-dir", str(partitioned)])
        assert result.exit_code == 0
        data = yaml.safe_load((partitioned / "architecture" / "index.yaml").read_text())
        assert data["partitions"]["payments"]["labels"] == {"criticality": "core"}

    def test_partition_label_validated(self, partitioned: Path) -> None:
        (partitioned / "architecture" / "classification.yaml").write_text(
            yaml.dump({"dimensions": {"criticality": {"values": ["core", "supporting", "generic"]}}}), encoding="utf-8"
        )
        (partitioned / "architecture" / "payments" / "partition.yaml").write_text(
            yaml.dump({"labels": {"criticality": "wrong"}}), encoding="utf-8"
        )
        result = runner.invoke(app, ["check", "--strict", "--project-dir", str(partitioned)])
        assert result.exit_code == 1
        assert "Partition" in result.output and "not in allowed values" in " ".join(result.output.split())
