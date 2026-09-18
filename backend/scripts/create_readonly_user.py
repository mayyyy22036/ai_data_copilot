"""
Crée un rôle PostgreSQL en lecture seule, séparé de l'utilisateur admin
(copilot_user), destiné exclusivement aux requêtes générées par le LLM.

Usage (depuis backend/, venv activé) :
    python -m scripts.create_readonly_user

Idempotent : peut être relancé sans erreur si le rôle existe déjà.
"""

from sqlalchemy import text

from app.core.config import settings
from app.database.session import engine  # connexion ADMIN, utilisée une seule fois ici

READONLY_ROLE = "readonly_agent"


def main():
    with engine.begin() as conn:
        print(f"Création du rôle '{READONLY_ROLE}' (s'il n'existe pas déjà)...")
        conn.execute(
            text(
                f"""
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '{READONLY_ROLE}') THEN
                        CREATE ROLE {READONLY_ROLE} WITH LOGIN PASSWORD :password;
                    END IF;
                END
                $$;
                """
            ),
            {"password": settings.readonly_db_password},
        )

        print("Attribution des permissions SELECT uniquement...")
        conn.execute(text(f"GRANT CONNECT ON DATABASE copilot_db TO {READONLY_ROLE}"))
        conn.execute(text(f"GRANT USAGE ON SCHEMA public TO {READONLY_ROLE}"))
        conn.execute(text(f"GRANT SELECT ON ALL TABLES IN SCHEMA public TO {READONLY_ROLE}"))
        # S'applique aussi aux tables créées APRÈS ce script (utile si le
        # schéma évolue plus tard).
        conn.execute(
            text(
                f"ALTER DEFAULT PRIVILEGES IN SCHEMA public "
                f"GRANT SELECT ON TABLES TO {READONLY_ROLE}"
            )
        )

    print(f"Rôle '{READONLY_ROLE}' prêt : SELECT uniquement, aucune écriture possible.")


if __name__ == "__main__":
    main()
