from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher

from src.domain.models import IbgeMunicipality
from src.services.text_normalizer import normalize_name


@dataclass(frozen=True)
class MatchResult:
    municipality: IbgeMunicipality | None
    is_ambiguous: bool = False


class MunicipalityMatchingService:
    def __init__(self, municipalities: list[IbgeMunicipality], fuzzy_cutoff: float) -> None:
        self._fuzzy_cutoff = fuzzy_cutoff
        self._normalized_index: dict[str, list[IbgeMunicipality]] = {}
        for municipality in municipalities:
            normalized_name = normalize_name(municipality.official_name)
            self._normalized_index.setdefault(normalized_name, []).append(municipality)

        self._normalized_names = list(self._normalized_index.keys())

    def match(self, input_name: str) -> MatchResult:
        normalized_input = normalize_name(input_name)

        exact_matches = self._normalized_index.get(normalized_input, [])
        if len(exact_matches) == 1:
            return MatchResult(municipality=exact_matches[0])
        if len(exact_matches) > 1:
            return MatchResult(municipality=self._pick_deterministic_candidate(exact_matches))

        best_name, best_score, second_best_score = self._find_best_candidates(normalized_input)
        if best_name is None or best_score < self._fuzzy_cutoff:
            return MatchResult(municipality=None)

        if (best_score - second_best_score) <= 0.02 and second_best_score >= self._fuzzy_cutoff:
            return MatchResult(municipality=None, is_ambiguous=True)

        best_matches = self._normalized_index[best_name]
        if len(best_matches) != 1:
            return MatchResult(municipality=None)

        return MatchResult(municipality=best_matches[0])

    def _pick_deterministic_candidate(self, matches: list[IbgeMunicipality]) -> IbgeMunicipality:
        # Keep matching stable across runs for duplicated municipality names.
        return sorted(matches, key=lambda item: (item.uf, item.ibge_id), reverse=True)[0]

    def _find_best_candidates(self, normalized_input: str) -> tuple[str | None, float, float]:
        best_name: str | None = None
        best_score = 0.0
        second_best_score = 0.0

        for candidate in self._normalized_names:
            score = SequenceMatcher(None, normalized_input, candidate).ratio()
            if score > best_score:
                second_best_score = best_score
                best_score = score
                best_name = candidate
            elif score > second_best_score:
                second_best_score = score

        return best_name, best_score, second_best_score
