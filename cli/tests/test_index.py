"""Tests for sda index — partitioned and flat mode index generation."""

import yaml
import pytest
from pathlib import Path
from typer.testing import CliRunner

from sda.main import app

runner = CliRunner()


def _write_problem(inbox: Path, prob_id: str, *, system: str | None = None, services: list[str] | None = None) -> Path:
    content = f"id: {prob_id}\ntitle: test\nstatus: active\n"
    if system:
        content += f"system: {system}\n"
    if services:
        content += f"services: [{', '.join(services)}]\n"
    f = inbox / f"{prob_id}.yaml"
    f.write_text(content, encoding="utf-8")
    return f


def _write_services(path: Path, services: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump({"services": services}), encoding="utf-8")


def _write_adr(adr_dir: Path, name: str, *, status: str = "accepted", services: list[str] | None = None) -> Path:
    adr_dir.mkdir(parents=True, exist_ok=True)
    svc_section = ""
    if services:
        svc_section = "\n## Affected Services\n" + "\n".join(f"- {s}" for s in services) + "\n"
    content = f"# {name}\n\n## Metadata\n- status: {status}\n- links: []\n{svc_section}"
    f = adr_dir / f"{name}.md"
    f.write_text(content, encoding="utf-8")
    return f


@pytest.fixture
def flat_project(tmp_path: Path) -> Path:
    """Standard flat layout — no partitions."""
    (tmp_path / "architecture" / "inbox").mkdir(parents=True)
    (tmp_path / "architecture" / "model").mkdir(parents=True)
    (tmp_path / "architecture" / "adr").mkdir(parents=True)
    return tmp_path


@pytest.fixture
def partitioned_project(tmp_path: Path) -> Path:
    """Two partitions: payments and catalog."""
    (tmp_path / "architecture" / "inbox").mkdir(parents=True)
    (tmp_path / "architecture" / "payments" / "model").mkdir(parents=True)
    (tmp_path / "architecture" / "payments" / "adr").mkdir(parents=True)
    (tmp_path / "architecture" / "catalog" / "model").mkdir(parents=True)
    (tmp_path / "architecture" / "adr").mkdir(parents=True)  # root-level
    return tmp_path


class TestFlatIndex:

    def test_generates_index(self, flat_project: Path) -> None:
        inbox = flat_project / "architecture" / "inbox"
        _write_problem(inbox, "PROB-001", services=["svc-a"])
        _write_services(flat_project / "architecture" / "model" / "services.yaml", {"svc-a": {}})

        result = runner.invoke(app, ["index", "--project-dir", str(flat_project)])
        assert result.exit_code == 0

        index_file = flat_project / "architecture" / "index.yaml"
        assert index_file.exists()
        data = yaml.safe_load(index_file.read_text())
        assert "systems" not in data  # flat mode has no systems key
        assert "PROB-001" in data["graph"]
        assert data["graph"]["svc-a"]["type"] == "service"

    def test_no_systems_key(self, flat_project: Path) -> None:
        result = runner.invoke(app, ["index", "--project-dir", str(flat_project)])
        assert result.exit_code == 0
        data = yaml.safe_load((flat_project / "architecture" / "index.yaml").read_text())
        assert "systems" not in data


class TestPartitionedIndex:

    def test_generates_per_partition_index(self, partitioned_project: Path) -> None:
        inbox = partitioned_project / "architecture" / "inbox"
        _write_problem(inbox, "PROB-001", system="payments", services=["svc-orders"])
        _write_problem(inbox, "PROB-002", system="catalog", services=["catalog-api"])
        _write_services(partitioned_project / "architecture" / "payments" / "model" / "services.yaml", {"svc-orders": {}})
        _write_services(partitioned_project / "architecture" / "catalog" / "model" / "services.yaml", {"catalog-api": {}})

        result = runner.invoke(app, ["index", "--project-dir", str(partitioned_project)])
        assert result.exit_code == 0

        # Per-partition indexes exist
        payments_index = partitioned_project / "architecture" / "payments" / "index.yaml"
        dc_index = partitioned_project / "architecture" / "catalog" / "index.yaml"
        assert payments_index.exists()
        assert dc_index.exists()

        # payments index has only its nodes
        payments_data = yaml.safe_load(payments_index.read_text())
        assert "PROB-001" in payments_data["graph"]
        assert "PROB-002" not in payments_data["graph"]

        # catalog index has only its nodes
        dc_data = yaml.safe_load(dc_index.read_text())
        assert "PROB-002" in dc_data["graph"]
        assert "PROB-001" not in dc_data["graph"]

    def test_master_index_is_manifest(self, partitioned_project: Path) -> None:
        _write_services(partitioned_project / "architecture" / "payments" / "model" / "services.yaml", {"svc-orders": {}})
        _write_services(partitioned_project / "architecture" / "catalog" / "model" / "services.yaml", {"catalog-api": {}})

        result = runner.invoke(app, ["index", "--project-dir", str(partitioned_project)])
        assert result.exit_code == 0

        data = yaml.safe_load((partitioned_project / "architecture" / "index.yaml").read_text())
        assert data["systems"] == ["catalog", "payments"]
        assert "graph" not in data  # manifest has no full graph
        assert "partitions" in data
        assert data["partitions"]["payments"]["index"] == "payments/index.yaml"
        assert data["partitions"]["catalog"]["index"] == "catalog/index.yaml"

    def test_manifest_has_partition_counts(self, partitioned_project: Path) -> None:
        inbox = partitioned_project / "architecture" / "inbox"
        _write_problem(inbox, "PROB-001", system="payments", services=["svc-orders"])
        _write_services(partitioned_project / "architecture" / "payments" / "model" / "services.yaml", {"svc-orders": {}})
        _write_services(partitioned_project / "architecture" / "catalog" / "model" / "services.yaml", {})

        result = runner.invoke(app, ["index", "--project-dir", str(partitioned_project)])
        assert result.exit_code == 0

        data = yaml.safe_load((partitioned_project / "architecture" / "index.yaml").read_text())
        assert data["partitions"]["payments"]["problems"] == 1
        assert data["partitions"]["payments"]["services"] == 1

    def test_unrouted_problem_in_unscoped(self, partitioned_project: Path) -> None:
        inbox = partitioned_project / "architecture" / "inbox"
        _write_problem(inbox, "PROB-001", system="payments")
        _write_problem(inbox, "PROB-099")  # no system
        _write_services(partitioned_project / "architecture" / "payments" / "model" / "services.yaml", {})
        _write_services(partitioned_project / "architecture" / "catalog" / "model" / "services.yaml", {})

        result = runner.invoke(app, ["index", "--project-dir", str(partitioned_project)])
        assert result.exit_code == 0

        master = yaml.safe_load((partitioned_project / "architecture" / "index.yaml").read_text())
        assert "PROB-099" in master["unscoped"]
        assert "system" not in master["unscoped"]["PROB-099"]

        payments = yaml.safe_load((partitioned_project / "architecture" / "payments" / "index.yaml").read_text())
        assert "PROB-099" not in payments["graph"]

    def test_root_adr_in_unscoped(self, partitioned_project: Path) -> None:
        root_adr_dir = partitioned_project / "architecture" / "adr"
        _write_adr(root_adr_dir, "001-governance", services=["svc-orders"])
        _write_services(partitioned_project / "architecture" / "payments" / "model" / "services.yaml", {"svc-orders": {}})
        _write_services(partitioned_project / "architecture" / "catalog" / "model" / "services.yaml", {})

        result = runner.invoke(app, ["index", "--project-dir", str(partitioned_project)])
        assert result.exit_code == 0

        master = yaml.safe_load((partitioned_project / "architecture" / "index.yaml").read_text())
        assert "001-GOVERNANCE" in master["unscoped"]

        payments = yaml.safe_load((partitioned_project / "architecture" / "payments" / "index.yaml").read_text())
        assert "001-GOVERNANCE" not in payments["graph"]

    def test_partition_adr_in_partition_index(self, partitioned_project: Path) -> None:
        """A partition ADR should appear in its partition index with full graph data."""
        inbox = partitioned_project / "architecture" / "inbox"
        _write_problem(inbox, "PROB-001", system="payments", services=["svc-orders"])
        _write_services(partitioned_project / "architecture" / "payments" / "model" / "services.yaml", {"svc-orders": {}})
        _write_services(partitioned_project / "architecture" / "catalog" / "model" / "services.yaml", {})
        _write_adr(partitioned_project / "architecture" / "payments" / "adr", "001-caching", services=["svc-orders"])

        result = runner.invoke(app, ["index", "--project-dir", str(partitioned_project)])
        assert result.exit_code == 0

        # Partition index has the ADR
        payments = yaml.safe_load((partitioned_project / "architecture" / "payments" / "index.yaml").read_text())
        assert "001-CACHING" in payments["graph"]
        assert "svc-orders" in payments["graph"]["001-CACHING"]["linked_services"]
        assert "001-CACHING" in payments["graph"]["svc-orders"]["adrs"]
        assert "PROB-001" in payments["graph"]["svc-orders"]["problems"]

        # Master manifest counts the ADR
        master = yaml.safe_load((partitioned_project / "architecture" / "index.yaml").read_text())
        assert master["partitions"]["payments"]["adrs"] == 1
