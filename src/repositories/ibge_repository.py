from __future__ import annotations

from typing import Any

import requests

from src.config.settings import Settings
from src.domain.models import IbgeMunicipality


class IbgeRepository:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def fetch_municipalities(self) -> list[IbgeMunicipality]:
        response = requests.get(
            self._settings.ibge_api_url,
            timeout=self._settings.http_timeout_seconds,
        )
        response.raise_for_status()

        payload = response.json()
        if not isinstance(payload, list):
            raise ValueError("Unexpected IBGE response format")

        municipalities: list[IbgeMunicipality] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            try:
                municipalities.append(self._map_item(item))
            except (KeyError, TypeError, ValueError):
                # Ignore malformed rows so a single null field does not break the full import.
                continue

        if not municipalities:
            raise ValueError("No valid municipalities found in IBGE response")

        return municipalities

    def _map_item(self, item: dict[str, Any]) -> IbgeMunicipality:
        uf_data = self._extract_uf_data(item)
        region_data = uf_data.get("regiao")
        if not isinstance(region_data, dict):
            raise ValueError(f"Missing region data in IBGE municipality: {item.get('id')}")

        return IbgeMunicipality(
            ibge_id=int(item["id"]),
            official_name=str(item["nome"]),
            uf=str(uf_data["sigla"]),
            region=str(region_data["nome"]),
        )

    def _extract_uf_data(self, item: dict[str, Any]) -> dict[str, Any]:
        microregion = item.get("microrregiao")
        if isinstance(microregion, dict):
            mesoregion = microregion.get("mesorregiao")
            if isinstance(mesoregion, dict):
                uf_data = mesoregion.get("UF")
                if isinstance(uf_data, dict):
                    return uf_data

        immediate_region = item.get("regiao-imediata")
        if isinstance(immediate_region, dict):
            intermediate_region = immediate_region.get("regiao-intermediaria")
            if isinstance(intermediate_region, dict):
                uf_data = intermediate_region.get("UF")
                if isinstance(uf_data, dict):
                    return uf_data

        raise ValueError(f"Missing UF data in IBGE municipality: {item.get('id')}")
