"""
Connexion PostgreSQL en lecture seule.

Séparée de session.py (qui utilise l'utilisateur admin) : le SQL Tool
n'utilisera JAMAIS engine depuis session.py, uniquement celui-ci.
"""

from sqlalchemy import create_engine

from app.core.config import settings

readonly_engine = create_engine(
    settings.database_url_readonly,
    pool_pre_ping=True,
    # Filet de sécurité supplémentaire au niveau de la connexion elle-même :
    # même si le rôle PostgreSQL avait par erreur des droits d'écriture,
    # cette option refuse toute transaction d'écriture sur CETTE connexion.
    connect_args={"options": "-c default_transaction_read_only=on"},
)
