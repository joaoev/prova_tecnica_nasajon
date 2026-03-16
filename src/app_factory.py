from __future__ import annotations

from flask import Flask
from flask import jsonify

from src.config.settings import load_settings
from src.controllers.challenge_controller import ChallengeController
from src.repositories.correction_repository import CorrectionRepository
from src.repositories.ibge_repository import IbgeRepository
from src.repositories.supabase_auth_repository import SupabaseAuthRepository
from src.services.challenge_service import ChallengeService
from src.services.csv_service import CsvService
from src.services.stats_service import StatsService


def create_app() -> Flask:
    settings = load_settings()

    csv_service = CsvService()
    stats_service = StatsService()
    municipality_repository = IbgeRepository(settings)
    correction_repository = CorrectionRepository(settings)
    auth_repository = SupabaseAuthRepository(settings)

    challenge_service = ChallengeService(
        csv_service=csv_service,
        stats_service=stats_service,
        municipality_provider=municipality_repository,
        submission_provider=correction_repository,
        fuzzy_cutoff=settings.fuzzy_cutoff,
    )

    challenge_controller = ChallengeController(challenge_service, auth_repository)

    app = Flask(__name__)

    @app.get("/")
    def health() -> tuple[dict[str, str], int]:
        return jsonify({"status": "ok"}), 200

    app.add_url_rule("/api/challenge/run", view_func=challenge_controller.run, methods=["POST"])

    return app
