from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ProcessingStatus(StrEnum):
    OK = "OK"
    NAO_ENCONTRADO = "NAO_ENCONTRADO"
    ERRO_API = "ERRO_API"
    AMBIGUO = "AMBIGUO"


@dataclass(frozen=True)
class InputMunicipalityRecord:
    municipality_name: str
    population: int


@dataclass(frozen=True)
class IbgeMunicipality:
    ibge_id: int
    official_name: str
    uf: str
    region: str


@dataclass(frozen=True)
class EnrichedMunicipalityRecord:
    municipality_input: str
    population_input: int
    municipality_ibge: str
    uf: str
    region: str
    ibge_id: int | None
    status: ProcessingStatus


@dataclass(frozen=True)
class ChallengeStats:
    total_municipios: int
    total_ok: int
    total_nao_encontrado: int
    total_erro_api: int
    pop_total_ok: int
    medias_por_regiao: dict[str, float]

    def to_payload(self) -> dict[str, object]:
        return {
            "total_municipios": self.total_municipios,
            "total_ok": self.total_ok,
            "total_nao_encontrado": self.total_nao_encontrado,
            "total_erro_api": self.total_erro_api,
            "pop_total_ok": self.pop_total_ok,
            "medias_por_regiao": self.medias_por_regiao,
        }


@dataclass(frozen=True)
class SubmissionResult:
    user_id: str
    email: str
    score: float
    feedback: str
    components: dict[str, object]
