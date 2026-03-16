from __future__ import annotations

import argparse
from pathlib import Path

from src.config.settings import load_settings
from src.repositories.correction_repository import CorrectionRepository
from src.repositories.ibge_repository import IbgeRepository
from src.repositories.supabase_auth_repository import SupabaseAuthRepository
from src.services.challenge_service import ChallengeService
from src.services.csv_service import CsvService
from src.services.stats_service import StatsService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Executa o desafio tecnico de municipios do IBGE.")
    parser.add_argument("--input", dest="input_file", default="input.csv", help="Arquivo CSV de entrada.")
    parser.add_argument("--output", dest="output_file", default="resultado.csv", help="Arquivo CSV de saida.")
    parser.add_argument("--access-token", dest="access_token", default=None, help="ACCESS_TOKEN para submissao.")
    parser.add_argument("--email", dest="email", default=None, help="Email para login no Supabase.")
    parser.add_argument("--password", dest="password", default=None, help="Senha para login no Supabase.")
    parser.add_argument(
        "--no-submit",
        dest="no_submit",
        action="store_true",
        help="Executa processamento sem enviar resultado para API de correcao.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    settings = load_settings()
    challenge_service = ChallengeService(
        csv_service=CsvService(),
        stats_service=StatsService(),
        municipality_provider=IbgeRepository(settings),
        submission_provider=CorrectionRepository(settings),
        fuzzy_cutoff=settings.fuzzy_cutoff,
    )
    auth_provider = SupabaseAuthRepository(settings)

    result = challenge_service.execute(
        input_file_path=Path(args.input_file),
        output_file_path=Path(args.output_file),
        access_token=args.access_token or settings.default_access_token,
        auth_provider=auth_provider,
        email=args.email or settings.supabase_email,
        password=args.password or settings.supabase_password,
        should_submit=not args.no_submit,
    )

    print("resultado.csv gerado em:", result.output_file_path)
    print("estatisticas:", result.stats)

    if result.submission_result:
        print("score:", result.submission_result.score)
        print("feedback:", result.submission_result.feedback)
    elif result.submission_error:
        print("envio:", result.submission_error)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
