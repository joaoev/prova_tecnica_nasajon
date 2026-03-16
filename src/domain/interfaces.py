from __future__ import annotations

from typing import Protocol

from src.domain.models import ChallengeStats, IbgeMunicipality, SubmissionResult


class MunicipalityProvider(Protocol):
    def fetch_municipalities(self) -> list[IbgeMunicipality]:
        ...


class AuthProvider(Protocol):
    def login_and_get_access_token(self, email: str, password: str) -> str:
        ...


class StatsSubmissionProvider(Protocol):
    def submit_stats(self, access_token: str, stats: ChallengeStats) -> SubmissionResult:
        ...
