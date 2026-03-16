from __future__ import annotations

import requests

from src.config.settings import Settings


class SupabaseAuthRepository:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def login_and_get_access_token(self, email: str, password: str) -> str:
        if not self._settings.supabase_anon_key:
            raise ValueError("SUPABASE_ANON_KEY is required to execute login")

        response = requests.post(
            f"{self._settings.supabase_url}/auth/v1/token?grant_type=password",
            headers={
                "Content-Type": "application/json",
                "apikey": self._settings.supabase_anon_key,
            },
            json={"email": email, "password": password},
            timeout=self._settings.http_timeout_seconds,
        )
        response.raise_for_status()

        token = response.json().get("access_token")
        if not isinstance(token, str) or not token:
            raise ValueError("Supabase login response does not contain access_token")

        return token
