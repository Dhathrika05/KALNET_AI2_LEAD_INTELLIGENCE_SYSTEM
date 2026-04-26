# scrapers/aishe/__init__.py
# ─────────────────────────────────────────────────────────────────────────────
# Makes `scrapers/aishe/` a Python package.
# Exposes the main entry point so other modules can do:
#
#     from scrapers.aishe import run
#     run()
#
# ─────────────────────────────────────────────────────────────────────────────

from .aishe_main import run

__all__ = ["run"]
