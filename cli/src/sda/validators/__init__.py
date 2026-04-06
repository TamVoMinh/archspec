from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class CheckResult:
    severity: Severity
    message: str
    file: Path | None = None

    @property
    def is_error(self) -> bool:
        return self.severity == Severity.ERROR

    @property
    def is_warning(self) -> bool:
        return self.severity == Severity.WARNING

    def __str__(self) -> str:
        location = f" [{self.file}]" if self.file else ""
        return f"[{self.severity.value.upper()}]{location} {self.message}"


def errors(results: list[CheckResult]) -> list[CheckResult]:
    return [r for r in results if r.is_error]


def warnings(results: list[CheckResult]) -> list[CheckResult]:
    return [r for r in results if r.is_warning]
