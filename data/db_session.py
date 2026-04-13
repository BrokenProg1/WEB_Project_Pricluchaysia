"""Создание сессии с БД, с которой будут проходить взаимодействие"""

import sqlalchemy as sa
import sqlalchemy.orm as orm

from sqlalchemy.orm import Session


DeclaratingDataBase = orm.declarative_base()

__factory = None

def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("You need write name of a database")

    conn_str = f"sqlite:///{db_file.strip()}?check_same_thread=False"
    print(f"Connecting to the database {conn_str}...")

    engine = sa.create_engine(conn_str, echo=False, pool_pre_ping=True)
    __factory = orm.sessionmaker(bind=engine)

    from . import __all_models

    DeclaratingDataBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()