from decouple import config
from sqlmodel import SQLModel, create_engine

database_url = config("DATABASE_URL")
debug = config("DEBUG", default=False, cast=bool)

engine = create_engine(database_url, echo=debug)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
