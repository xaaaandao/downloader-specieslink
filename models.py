import sqlalchemy as sa
import sqlalchemy.ext.declarative

Base = sa.ext.declarative.declarative_base()

def get_base():
    return Base


class Record(Base):
    __tablename__ = "record"


    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    barcode = sa.Column(sa.String, nullable=True)
    family = sa.Column(sa.String, nullable=True)
    json = sa.Column(sa.JSON, nullable=True)
    images = sa.Column(sa.ARRAY(sa.String()), nullable=True)