from __future__ import annotations

from pathlib import Path

from flask import jsonify, request

from src.domain.interfaces import AuthProvider
from src.services.challenge_service import ChallengeExecutionResult, ChallengeService


class ChallengeController:
    def __init__(self, challenge_service: ChallengeService, auth_provider: AuthProvider) -> None:
        self._challenge_service = challenge_service
        self._auth_provider = auth_provider

    def run(self):
        payload = request.get_json(silent=True) or {}

        input_file_path = Path(payload.get("input_file", "input.csv"))
        output_file_path = Path(payload.get("output_file", "resultado.csv"))

        should_submit = bool(payload.get("should_submit", True))
        access_token = payload.get("access_token")
        email = payload.get("email")
        password = payload.get("password")

        try:
            result = self._challenge_service.execute(
                input_file_path=input_file_path,
                output_file_path=output_file_path,
                access_token=access_token,
                auth_provider=self._auth_provider,
                email=email,
                password=password,
                should_submit=should_submit,
            )
            return jsonify(self._to_http_response(result)), 200
        except Exception as exc:
            return jsonify({"error": str(exc)}), 400

    def _to_http_response(self, result: ChallengeExecutionResult) -> dict[str, object]:
        response: dict[str, object] = {
            "output_file": str(result.output_file_path),
            "stats": result.stats,
            "submission_error": result.submission_error,
        }

        if result.submission_result is not None:
            response["submission"] = {
                "user_id": result.submission_result.user_id,
                "email": result.submission_result.email,
                "score": result.submission_result.score,
                "feedback": result.submission_result.feedback,
                "components": result.submission_result.components,
            }

        return response
