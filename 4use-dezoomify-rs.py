import click
import os

from database import connect
from models import Record

@click.command()
@click.option("--output", required=True, default="./images")
def main(output):
    engine, session = connect()
    engine.echo = False

    if not os.environ["SPLINK"]:
        raise ValueError

    os.makedirs(output, exist_ok=True)

    # SELECT * FROM RECORD
    records = session.query(Record).all()
    for r in records:
        for u in r.images:
            if "https://storage.googleapis.com/cria-zoomify/" in u:
                image_code, u = make_url(u)
                print(u, image_code)

                os.makedirs(os.path.join(output, r.family), exist_ok=True)
                filename = os.path.join(output, r.family, image_code)
                if not os.path.exists(filename):
                    os.system('./dezoomify-rs -H Referer: %s %s.jpg -l' % (u, filename))

    session.close()
    engine.dispose()


def make_url(u):
    u = u[0:u.index("/TileGroup0/")]
    image_code = u[u.rindex("/") + 1:]
    u = u + "/ImageProperties.xml"
    return image_code, u


if __name__ == "__main__":
    main()