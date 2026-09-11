"""Base connector. Each source implements fetch(); the runner handles the rest."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import date

from ..schema import Observation, SourceSpec


class Source(ABC):
    """One connector per data source.

    Contract:
      - `spec` declares identity, cadence, licence and coverage.
      - `fetch()` returns normalized Observations and nothing else. No scoring,
        no transforms, no market filtering beyond what the API requires.
      - Connectors must be idempotent: same args, same output.
      - Connectors must never raise on a single missing market. Emit an
        Observation with value=None so gaps are visible rather than silent.
    """

    spec: SourceSpec

    @abstractmethod
    def fetch(self, markets: list[str], since: date) -> Iterable[Observation]:
        ...

    def healthcheck(self) -> tuple[bool, str]:
        """Cheap liveness probe. Run before the daily pipeline commits anything."""
        return True, "not implemented"
