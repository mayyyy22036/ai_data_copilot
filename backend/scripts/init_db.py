from app.database.session import engine, Base
from app.database.models import Store, Sales  # noqa: F401


def main():
    print(f"Connexion à : {engine.url}")

    print(f"Tables détectées par SQLAlchemy : {list(Base.metadata.tables.keys())}")

    Base.metadata.create_all(bind=engine)

    print("Tables créées avec succès : stores, sales")


if __name__ == "__main__":
    main()