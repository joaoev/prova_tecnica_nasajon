from __future__ import annotations

import csv
from pathlib import Path

from src.domain.models import EnrichedMunicipalityRecord, InputMunicipalityRecord


class CsvService:
    def read_input(self, input_file_path: Path) -> list[InputMunicipalityRecord]:
        records: list[InputMunicipalityRecord] = []
        with input_file_path.open("r", encoding="utf-8", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            expected_headers = {"municipio", "populacao"}
            if reader.fieldnames is None or set(reader.fieldnames) != expected_headers:
                raise ValueError("input.csv must contain exactly: municipio,populacao")

            for row in reader:
                municipality = row["municipio"].strip()
                population = int(row["populacao"])
                records.append(
                    InputMunicipalityRecord(
                        municipality_name=municipality,
                        population=population,
                    )
                )

        return records

    def write_output(self, output_file_path: Path, records: list[EnrichedMunicipalityRecord]) -> None:
        with output_file_path.open("w", encoding="utf-8", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(
                [
                    "municipio_input",
                    "populacao_input",
                    "municipio_ibge",
                    "uf",
                    "regiao",
                    "id_ibge",
                    "status",
                ]
            )
            for item in records:
                writer.writerow(
                    [
                        item.municipality_input,
                        item.population_input,
                        item.municipality_ibge,
                        item.uf,
                        item.region,
                        "" if item.ibge_id is None else item.ibge_id,
                        item.status.value,
                    ]
                )
