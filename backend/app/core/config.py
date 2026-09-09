"""
Configuration centralisée de l'application.

Pourquoi ce fichier existe :
- Un seul endroit lit les variables d'environnement (pas de os.getenv() éparpillé
  dans 15 fichiers différents).
- Pydantic valide automatiquement les types (ex: PORT doit être un int).
- Le code métier importe `settings` et n'a jamais besoin de savoir si on est
  en local ou sur Cloud Run : c'est cette classe qui absorbe la différence.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- LLM ---
    gemini_api_key: str
    gemini_model: str = "gemini-1.5-flash"

    # --- Base de données ---
    database_url: str

    # --- Vector store ---
    chroma_persist_dir: str = "./chroma_db"

    # --- Application ---
    # Cloud Run définit automatiquement la variable PORT au démarrage du
    # conteneur. En local, on retombe sur 8000 par défaut.
    port: int = 8000
    environment: str = "local"
    log_level: str = "INFO"

    # --- CORS ---
    allowed_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Instance unique, importée partout ailleurs dans l'app : `from app.core.config import settings`
settings = Settings()
