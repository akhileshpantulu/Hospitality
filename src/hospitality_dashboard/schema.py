"""Normalized observation schema.

Every source - licensed or public, daily or annual, metro-level or national -
lands in the `Observation` shape below. The scoring engine reads only this
shape, so adding a source never requires touching scoring logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any


class Frequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    EVENT = "event"          # irregular: advisories, strikes, one-off news


class GeoLevel(str, Enum):
    MARKET = "market"        # STR market boundary; the spine
    SUBMARKET = "submarket"
    NUTS = "nuts"            # Eurostat statistical region
    COUNTRY = "country"
    AIRPORT = "airport"


class Direction(str, Enum):
    """Which way is good for a hotel owner in this market."""
    HIGHER_IS_TAILWIND = "higher_is_tailwind"   # e.g. inbound air seats
    HIGHER_IS_HEADWIND = "higher_is_headwind"   # e.g. rooms under construction
    CONTEXT_ONLY = "context_only"               # displayed, never scored


class License(str, Enum):
    PUBLIC = "public"                   # redistributable as-is
    ATTRIBUTION = "attribution"         # redistributable with credit
    RESTRICTED = "restricted"           # derived index only, no raw values
    INTERNAL = "internal"               # never leaves Highgate


@dataclass(frozen=True)
class Indicator:
    """Metadata for one measurable series. Defined once in config/indicators.yml."""
    id: str
    name: str
    category: str                       # demand_air | demand_lodging | tourism |
                                        # group | supply | macro | fx | news |
                                        # risk | cost | capital
    unit: str
    direction: Direction
    frequency: Frequency
    source_id: str
    transform: str = "yoy"              # level | yoy | qoq | zscore | index
    publication_lag_days: int = 0       # how stale the freshest print is
    license: License = License.PUBLIC
    notes: str = ""


@dataclass(frozen=True)
class Observation:
    """One value, for one indicator, for one market, for one period."""
    market_id: str
    indicator_id: str
    source_id: str
    geo_level: GeoLevel
    geo_code: str                       # the code actually queried at the source
    period_start: date
    period_end: date
    frequency: Frequency
    value: float | None                 # None = source returned no data, not zero
    unit: str

    # Point-in-time correctness. A score computed on 2026-03-01 must be
    # reproducible later even after the underlying series is revised.
    retrieved_at: datetime = field(default_factory=lambda: datetime.now())
    vintage: str | None = None          # source's own release/vintage tag

    # Provenance and quality
    is_estimate: bool = False
    is_revision: bool = False
    confidence: float = 1.0             # 0-1; downweight proxied or modelled values
    raw: dict[str, Any] = field(default_factory=dict)   # as-fetched payload slice


@dataclass(frozen=True)
class SourceSpec:
    """Registry entry for a data source. Mirrors one block in config/sources.yml."""
    id: str
    name: str
    provider: str
    category: str
    access: str                         # api | bulk_download | scrape | manual_upload
    auth: str | None                    # env var name holding the credential
    refresh_interval_hours: int         # scheduler honours this, not the daily tick
    geo_level: GeoLevel
    coverage: str                       # which markets it actually reaches
    license: License
    cost: str
    status: str                         # proposed | approved | wired | rejected
    indicators: list[str] = field(default_factory=list)
    notes: str = ""
