from __future__ import annotations

from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


DEFAULT_SUPABASE_URL = "https://mynxlubykylncinttggu.supabase.co"
DEFAULT_FUNCTION_URL = "https://mynxlubykylncinttggu.functions.supabase.co/ibge-submit"
DEFAULT_IBGE_API_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"


@dataclass(frozen=True)
class Settings:
    supabase_url: str
    supabase_anon_key: str
    correction_function_url: str
    ibge_api_url: str
    default_access_token: str | None = None
    supabase_email: str | None = None
    supabase_password: str | None = None
    http_timeout_seconds: int = 30
    fuzzy_cutoff: float = 0.82


def load_settings() -> Settings:
    access_token = os.getenv("ACCESS_TOKEN")
    email = os.getenv("SUPABASE_EMAIL")
    password = os.getenv("SUPABASE_PASSWORD")

    return Settings(
        supabase_url=os.getenv("SUPABASE_URL", DEFAULT_SUPABASE_URL),
        supabase_anon_key=os.getenv("SUPABASE_ANON_KEY", ""),
        correction_function_url=os.getenv("CORRECTION_FUNCTION_URL", DEFAULT_FUNCTION_URL),
        ibge_api_url=os.getenv("IBGE_API_URL", DEFAULT_IBGE_API_URL),
        default_access_token=access_token if access_token else None,
        supabase_email=email if email else None,
        supabase_password=password if password else None,
        http_timeout_seconds=int(os.getenv("HTTP_TIMEOUT_SECONDS", "30")),
        fuzzy_cutoff=float(os.getenv("FUZZY_CUTOFF", "0.82")),
    )
