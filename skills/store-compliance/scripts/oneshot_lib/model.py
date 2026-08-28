"""Core data model for oneshot findings."""
from __future__ import annotations

import dataclasses
import json
from typing import Any, Iterable, Optional

SEVERITIES = ["BLOCKER", "HIGH", "MEDIUM", "LOW", "INFO"]
SEVERITY_RANK = {s: i for i, s in enumerate(SEVERITIES)}

APPLE = "apple"
PLAY = "google_play"
BOTH = "both"


@dataclasses.dataclass
class Finding:
    rule_id: str
    severity: str
    store: str  # apple | google_play | both
    guideline: str
    title: str
    fix: str
    file: str = ""
    line: int = 0
    evidence: str = ""
    impact: str = ""
    suggested_value: str = ""
    auto_fixable: bool = False
    confidence: str = "high"  # high | medium | low
    found_by: Optional[list] = None

    def __post_init__(self) -> None:
        if self.severity not in SEVERITY_RANK:
            raise ValueError(f"bad severity {self.severity!r} on {self.rule_id}")
        if self.store not in (APPLE, PLAY, BOTH):
            raise ValueError(f"bad store {self.store!r} on {self.rule_id}")
        if self.found_by is None:
            self.found_by = ["scanner"]

    @property
    def sort_key(self):
        conf = {"high": 0, "medium": 1, "low": 2}.get(self.confidence, 3)
        return (SEVERITY_RANK[self.severity], conf, self.rule_id, self.file, self.line)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    @property
    def location(self) -> str:
        if not self.file:
            return "(project-wide)"
        return f"{self.file}:{self.line}" if self.line else self.file


class FindingList(list):
    """A list of Findings with a few conveniences."""

    def add(self, *args, **kwargs) -> None:
        self.append(Finding(*args, **kwargs))

    def extend_from(self, it: Iterable[Finding]) -> None:
        for f in it:
            self.append(f)

    def ranked(self) -> "FindingList":
        return FindingList(sorted(self, key=lambda f: f.sort_key))

    def counts(self) -> dict:
        out = {s: 0 for s in SEVERITIES}
        for f in self:
            out[f.severity] += 1
        return out

    def by_store(self, store: str) -> "FindingList":
        return FindingList(f for f in self if f.store in (store, BOTH))

    def dedupe(self) -> "FindingList":
        seen: dict[Any, Finding] = {}
        for f in self:
            key = (f.rule_id, f.file, f.line)
            prev = seen.get(key)
            if prev is None:
                seen[key] = f
                continue
            # keep the highest severity; union evidence and found_by
            keep = prev if SEVERITY_RANK[prev.severity] <= SEVERITY_RANK[f.severity] else f
            other = f if keep is prev else prev
            if other.evidence and other.evidence not in keep.evidence:
                keep.evidence = (keep.evidence + "\n" + other.evidence).strip()
            keep.found_by = sorted(set((keep.found_by or []) + (other.found_by or [])))
            seen[key] = keep
        return FindingList(seen.values())

    def to_json(self, meta: dict | None = None) -> str:
        return json.dumps(
            {
                "meta": meta or {},
                "counts": self.counts(),
                "findings": [f.to_dict() for f in self.ranked()],
            },
            indent=2,
        )
