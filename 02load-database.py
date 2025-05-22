import click
import json
import os
import pathlib


from database import connect, create_table
from models import Record


@click.command()
@click.option("--input", required=True)
@click.version_option("2.0", prog_name="load-database")
def main(input):
    if not os.path.exists(input):
        raise IsADirectoryError

    engine, session = connect()
    engine.echo = False

    create_table(engine)
    records = []

    for p in pathlib.Path(input).rglob("*.json"):
        print(p)

        with open(p) as file:
            data = json.load(file)

        if len(data) > 0:
            records = records + [Record(barcode=d["properties"]["barcode"], kingdom=d["properties"]["kingdom"], family=d["properties"]["family"], json=d)
                                 for d in data["features"]
                                 if "properties" in d and "barcode" in d["properties"] and
                                 has_family(d) and
                                 has_kingdom(d) and
                                 not has_barcode(d["properties"]["barcode"], session)]
            
            session.add_all(records)

        session.commit()

    session.close()
    engine.dispose()


def has_barcode(barcode, session):
    # SELECT COUNT(*) RECORD R WHERE R.BARCODE=BARCODE;
    return session.query(Record).filter(Record.barcode.__eq__(barcode)).count() > 0


def has_family(d):
    return "family" in d["properties"]

def has_kingdom(d):
    return "kingdom" in d["properties"]


if __name__ == '__main__':
    main()
