"""
Test de sécurité du SQL Tool. Important : ces tests prouvent que
validate_sql() bloque les requêtes dangereuses PAR ELLE-MÊME, sans jamais
dépendre du LLM pour "bien se comporter". Le LLM peut halluciner ou être
manipulé par prompt injection — cette couche ne doit pas en dépendre.
"""

import pytest

from app.tools.sql_tool import validate_sql


def test_valid_select_is_accepted():
    result = validate_sql("SELECT * FROM sales")
    assert result.upper().startswith("SELECT")


def test_limit_is_auto_appended_when_missing():
    result = validate_sql("SELECT * FROM sales")
    assert "LIMIT" in result.upper()


def test_existing_limit_is_not_duplicated():
    result = validate_sql("SELECT * FROM sales LIMIT 10")
    assert result.upper().count("LIMIT") == 1


@pytest.mark.parametrize(
    "dangerous_sql",
    [
        "DELETE FROM sales",
        "DROP TABLE sales",
        "UPDATE sales SET sales = 0",
        "INSERT INTO sales (store_id) VALUES (1)",
        "TRUNCATE TABLE sales",
        "ALTER TABLE sales ADD COLUMN hacked INT",
        "GRANT ALL ON sales TO public",
    ],
)
def test_dangerous_statements_are_rejected(dangerous_sql):
    with pytest.raises(ValueError):
        validate_sql(dangerous_sql)


def test_multiple_statements_are_rejected():
    # Tentative classique d'injection : une requête légitime suivie d'une
    # deuxième instruction malveillante.
    with pytest.raises(ValueError):
        validate_sql("SELECT * FROM sales; DROP TABLE sales;")


def test_non_select_statement_is_rejected():
    with pytest.raises(ValueError):
        validate_sql("EXPLAIN SELECT * FROM sales")
