from app.core.database import Base, engine
from app import models  # noqa: F401  # this import registers the models


def init_db():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables registered in metadata:", list(Base.metadata.tables.keys()))


if __name__ == "__main__":
    init_db()
