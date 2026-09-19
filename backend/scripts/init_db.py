from app.database.models import Sales, Store  # noqa: F401
from app.database.session import Base, engine


def main():
    print(f"Connexion à : {engine.url}")

    print(f"Tables détectées par SQLAlchemy : {list(Base.metadata.tables.keys())}")

    Base.metadata.create_all(bind=engine)

    print("Tables créées avec succès : stores, sales")


if __name__ == "__main__":
    main()