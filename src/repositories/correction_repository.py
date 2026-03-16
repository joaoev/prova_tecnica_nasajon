from __future__ import annotations

from typing import Any

import requests

from src.config.settings import Settings
from src.domain.models import ChallengeStats, SubmissionResult


class CorrectionRepository:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def submit_stats(self, access_token: str, stats: ChallengeStats) -> SubmissionResult:
        response = requests.post(
            self._settings.correction_function_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            },
            json={"stats": stats.to_payload()},
            timeout=self._settings.http_timeout_seconds,
        )
        response.raise_for_status()

        payload = response.json()
        return self._map_response(payload)

    def _map_response(self, payload: dict[str, Any]) -> SubmissionResult:
        return SubmissionResult(
            user_id=str(payload.get("user_id", "")),
            email=str(payload.get("email", "")),
            score=float(payload.get("score", 0.0)),
            feedback=str(payload.get("feedback", "")),
            components=payload.get("components", {}) if isinstance(payload.get("components", {}), dict) else {},
        )
