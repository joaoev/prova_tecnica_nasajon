from __future__ import annotations

from collections import defaultdict

from src.domain.models import ChallengeStats, EnrichedMunicipalityRecord, ProcessingStatus


class StatsService:
    def calculate(self, records: list[EnrichedMunicipalityRecord]) -> ChallengeStats:
        total_municipios = len(records)
        total_ok = sum(1 for item in records if item.status is ProcessingStatus.OK)
        total_nao_encontrado = sum(1 for item in records if item.status is ProcessingStatus.NAO_ENCONTRADO)
        total_erro_api = sum(1 for item in records if item.status is ProcessingStatus.ERRO_API)
        pop_total_ok = sum(item.population_input for item in records if item.status is ProcessingStatus.OK)

        region_sums: dict[str, int] = defaultdict(int)
        region_counts: dict[str, int] = defaultdict(int)
        for item in records:
            if item.status is not ProcessingStatus.OK:
                continue
            region_sums[item.region] += item.population_input
            region_counts[item.region] += 1

        medias_por_regiao = {
            region: round(region_sums[region] / region_counts[region], 2)
            for region in sorted(region_sums.keys())
        }

        return ChallengeStats(
            total_municipios=total_municipios,
            total_ok=total_ok,
            total_nao_encontrado=total_nao_encontrado,
            total_erro_api=total_erro_api,
            pop_total_ok=pop_total_ok,
            medias_por_regiao=medias_por_regiao,
        )
