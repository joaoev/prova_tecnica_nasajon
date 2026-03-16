from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from src.domain.interfaces import AuthProvider, MunicipalityProvider, StatsSubmissionProvider
from src.domain.models import EnrichedMunicipalityRecord, InputMunicipalityRecord, ProcessingStatus, SubmissionResult
from src.services.csv_service import CsvService
from src.services.matching_service import MunicipalityMatchingService
from src.services.stats_service import StatsService


@dataclass(frozen=True)
class ChallengeExecutionResult:
    output_file_path: Path
    stats: dict[str, object]
    submission_result: SubmissionResult | None
    submission_error: str | None


class ChallengeService:
    def __init__(
        self,
        csv_service: CsvService,
        stats_service: StatsService,
        municipality_provider: MunicipalityProvider,
        submission_provider: StatsSubmissionProvider,
        fuzzy_cutoff: float,
    ) -> None:
        self._csv_service = csv_service
        self._stats_service = stats_service
        self._municipality_provider = municipality_provider
        self._submission_provider = submission_provider
        self._fuzzy_cutoff = fuzzy_cutoff

    def execute(
        self,
        input_file_path: Path,
        output_file_path: Path,
        access_token: str | None,
        auth_provider: AuthProvider | None = None,
        email: str | None = None,
        password: str | None = None,
        should_submit: bool = True,
    ) -> ChallengeExecutionResult:
        input_records = self._csv_service.read_input(input_file_path)

        try:
            ibge_municipalities = self._municipality_provider.fetch_municipalities()
        except Exception as exc:
            records_with_error = [
                EnrichedMunicipalityRecord(
                    municipality_input=record.municipality_name,
                    population_input=record.population,
                    municipality_ibge="",
                    uf="",
                    region="",
                    ibge_id=None,
                    status=ProcessingStatus.ERRO_API,
                )
                for record in input_records
            ]
            self._csv_service.write_output(output_file_path, records_with_error)
            stats = self._stats_service.calculate(records_with_error)
            return ChallengeExecutionResult(
                output_file_path=output_file_path,
                stats=stats.to_payload(),
                submission_result=None,
                submission_error=f"Falha ao consultar API do IBGE: {exc}",
            )

        matcher = MunicipalityMatchingService(ibge_municipalities, self._fuzzy_cutoff)
        enriched_records = self._enrich_records(input_records, matcher)
        self._csv_service.write_output(output_file_path, enriched_records)

        calculated_stats = self._stats_service.calculate(enriched_records)

        if not should_submit:
            return ChallengeExecutionResult(
                output_file_path=output_file_path,
                stats=calculated_stats.to_payload(),
                submission_result=None,
                submission_error=None,
            )

        token_to_use = self._resolve_access_token(access_token, auth_provider, email, password)
        if not token_to_use:
            return ChallengeExecutionResult(
                output_file_path=output_file_path,
                stats=calculated_stats.to_payload(),
                submission_result=None,
                submission_error="ACCESS_TOKEN ausente. Envio nao realizado.",
            )

        try:
            submission = self._submission_provider.submit_stats(token_to_use, calculated_stats)
            return ChallengeExecutionResult(
                output_file_path=output_file_path,
                stats=calculated_stats.to_payload(),
                submission_result=submission,
                submission_error=None,
            )
        except Exception as exc:
            return ChallengeExecutionResult(
                output_file_path=output_file_path,
                stats=calculated_stats.to_payload(),
                submission_result=None,
                submission_error=f"Falha no envio: {exc}",
            )

    def _resolve_access_token(
        self,
        access_token: str | None,
        auth_provider: AuthProvider | None,
        email: str | None,
        password: str | None,
    ) -> str | None:
        if access_token:
            return access_token

        if auth_provider and email and password:
            return auth_provider.login_and_get_access_token(email, password)

        return None

    def _enrich_records(
        self,
        input_records: Sequence[InputMunicipalityRecord],
        matcher: MunicipalityMatchingService,
    ) -> list[EnrichedMunicipalityRecord]:
        output: list[EnrichedMunicipalityRecord] = []
        for record in input_records:
            match_result = matcher.match(record.municipality_name)
            municipality = match_result.municipality

            if municipality:
                output.append(
                    EnrichedMunicipalityRecord(
                        municipality_input=record.municipality_name,
                        population_input=record.population,
                        municipality_ibge=municipality.official_name,
                        uf=municipality.uf,
                        region=municipality.region,
                        ibge_id=municipality.ibge_id,
                        status=ProcessingStatus.OK,
                    )
                )
                continue

            status = ProcessingStatus.AMBIGUO if match_result.is_ambiguous else ProcessingStatus.NAO_ENCONTRADO
            output.append(
                EnrichedMunicipalityRecord(
                    municipality_input=record.municipality_name,
                    population_input=record.population,
                    municipality_ibge="",
                    uf="",
                    region="",
                    ibge_id=None,
                    status=status,
                )
            )

        return output
