import os

import sqlalchemy as sa
import sqlalchemy.orm

from models import get_base, Record


def show_tables(engine):
    return sa.inspect(engine).get_table_names()


def table_exists(engine, table_name):
    return True if table_name in show_tables(engine) else False


def create_table(engine):
    tables = [Record]
    for t in tables:
        if not table_exists(engine, t.__tablename__):
            base = get_base()
            base.metadata.tables[t.__tablename__].create(bind=engine)
            print(f"create table: {t.__tablename__}")
        else:
            print(f"table {t.__tablename__} already exists")

def connect(database="herbario",
            echo=True,
            host="localhost",
            password=os.environ["PWDPG"],
            port="5432",
            user=os.environ["USERPG"]):
    try:
        url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
        engine = sa.create_engine(url, echo=echo, pool_pre_ping=True)
        session = sqlalchemy.orm.sessionmaker(bind=engine)
        session.configure(bind=engine)
        db = session()
        if engine.connect():
            return engine, db
    except Exception as e:
        raise e