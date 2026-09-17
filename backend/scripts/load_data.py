"""
Charge les CSV Rossmann bruts dans PostgreSQL.

Usage (depuis backend/, venv activé, fichiers dans data/raw/) :
    python scripts/load_data.py

Idempotent : on vide les tables avant de recharger, pour pouvoir relancer
ce script sans dupliquer les données si jamais tu changes quelque chose.
"""

import pandas as pd
from sqlalchemy import text

from app.database.session import engine, Base
from app.database import models  # noqa: F401 — nécessaire pour enregistrer les modèles

RAW_DIR = "data/raw"


def load_stores() -> pd.DataFrame:
    df = pd.read_csv(f"{RAW_DIR}/store.csv")

    df = df.rename(
        columns={
            "Store": "store_id",
            "StoreType": "store_type",
            "Assortment": "assortment",
            "CompetitionDistance": "competition_distance",
            "CompetitionOpenSinceMonth": "competition_open_since_month",
            "CompetitionOpenSinceYear": "competition_open_since_year",
            "Promo2": "promo2",
            "Promo2SinceWeek": "promo2_since_week",
            "Promo2SinceYear": "promo2_since_year",
            "PromoInterval": "promo_interval",
        }
    )

    df["promo2"] = df["promo2"].astype(bool)

    # pandas représente les valeurs manquantes en NaN (float) ; PostgreSQL
    # veut un vrai NULL. On convertit explicitement.
    df = df.where(pd.notnull(df), None)

    return df[
        [
            "store_id",
            "store_type",
            "assortment",
            "competition_distance",
            "competition_open_since_month",
            "competition_open_since_year",
            "promo2",
            "promo2_since_week",
            "promo2_since_year",
            "promo_interval",
        ]
    ]


def load_sales() -> pd.DataFrame:
    # dtype forcé sur StateHoliday : le CSV mélange 0 (int) et 'a'/'b'/'c'
    # (str) dans la même colonne, un piège classique de ce dataset.
    df = pd.read_csv(f"{RAW_DIR}/train.csv", dtype={"StateHoliday": str})

    df = df.rename(
        columns={
            "Store": "store_id",
            "DayOfWeek": "day_of_week",
            "Date": "date",
            "Sales": "sales",
            "Customers": "customers",
            "Open": "open",
            "Promo": "promo",
            "StateHoliday": "state_holiday",
            "SchoolHoliday": "school_holiday",
        }
    )

    df["open"] = df["open"].astype(bool)
    df["promo"] = df["promo"].astype(bool)
    df["school_holiday"] = df["school_holiday"].astype(bool)
    df["date"] = pd.to_datetime(df["date"]).dt.date

    df = df.where(pd.notnull(df), None)

    return df[
        [
            "store_id",
            "date",
            "day_of_week",
            "sales",
            "customers",
            "open",
            "promo",
            "state_holiday",
            "school_holiday",
        ]
    ]


def main():
    print("Lecture des CSV...")
    stores_df = load_stores()
    sales_df = load_sales()
    print(f"  {len(stores_df)} magasins, {len(sales_df)} lignes de ventes")

    print("Vérification/création des tables...")
    Base.metadata.create_all(bind=engine)

    with engine.begin() as conn:
        print("Nettoyage des tables (idempotence)...")
        # CASCADE nécessaire car sales dépend de stores (clé étrangère)
        conn.execute(text("TRUNCATE TABLE sales, stores RESTART IDENTITY CASCADE"))

        print("Insertion des magasins (stores)...")
        stores_df.to_sql("stores", conn, if_exists="append", index=False)

        print("Insertion des ventes (sales) — peut prendre 1-2 minutes...")
        sales_df.to_sql("sales", conn, if_exists="append", index=False, chunksize=5000)

    print("Chargement terminé avec succès.")


if __name__ == "__main__":
    main()