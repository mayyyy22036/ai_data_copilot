"""
Test de sécurité du Pandas Tool : la liste blanche de colonnes doit
rejeter toute colonne non autorisée AVANT d'accéder aux données —
ces tests ne touchent jamais PostgreSQL (validation avant chargement).
"""

import pytest

from app.tools.pandas_tool import compute_correlation, compute_groupby_stats


def test_correlation_rejects_disallowed_column():
    with pytest.raises(ValueError):
        compute_correlation("sales", "colonne_inexistante")


def test_groupby_rejects_disallowed_group_column():
    with pytest.raises(ValueError):
        compute_groupby_stats("colonne_inexistante", "sales", "mean")


def test_groupby_rejects_disallowed_agg_column():
    with pytest.raises(ValueError):
        compute_groupby_stats("store_type", "colonne_inexistante", "mean")


def test_groupby_rejects_disallowed_agg_func():
    with pytest.raises(ValueError):
        compute_groupby_stats("store_type", "sales", "DROP TABLE sales")
