import os

import sqlalchemy as sa
import sqlalchemy.orm

cfg = {
    'host': 'localhost',
    'user': os.environ['USERPG'],
    'password': os.environ['PWDPG']
}

def connect(echo=True):
    try:
        url = 'postgresql+psycopg2://%s:%s@%s:5432/herbario' % (cfg['user'], cfg['password'], cfg['host'])
        engine = sa.create_engine(url, echo=echo, pool_pre_ping=True)
        session = sqlalchemy.orm.sessionmaker(bind=engine)
        session.configure(bind=engine)
        db = session()
        if engine.connect():
            return engine, db
    except Exception as e:
        print('problems with host %s (%s)' % (cfg['host'], e))