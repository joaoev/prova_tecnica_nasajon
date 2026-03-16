from __future__ import annotations

from flask import Response, render_template


class HomeController:
    def index(self) -> str | Response:
        return render_template("index.html", title="Desafio Tecnico IBGE")
