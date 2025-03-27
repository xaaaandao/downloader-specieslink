import os

import click
import scrapy

from scrapy.crawler import CrawlerProcess
from scrapy.http import FormRequest
from scrapy.utils.project import get_project_settings

from database import connect, create_table
from models import Record


class SpeciesLink(scrapy.Spider):
    name = "specieslink"
    base_url = "https://specieslink.net/search/index"
    form_data = {
        "action": "records",
        "graph_type": "horizontalBar",
        "graph_sort": "value",
        "from": "0",
        "recs_order_by": "random_order",
        "dups_mode": "collect_full_key",
        "coll_groups": "",
        "coll_networks": "",
        "flags": "photo",
    }

    def __init__(self, session):
        self.session = session

    def start_requests(self):
        # SELECT * FROM RECORD
        barcodes = self.session.query(Record).all()

        for i, b in enumerate(barcodes):
            print(f"i: {i} barcode: {b} total: {len(barcodes)}")
            self.form_data["barcode"] = b.barcode
            yield FormRequest(self.base_url,
                              formdata=self.form_data,
                              callback=self.parse)

    def parse(self, response):
        urls = [url for url in response.xpath("//img/@src").extract() if self.url_valid(url)]
        self.session.add_all(urls)
        self.session.commit()

    def url_valid(self, url):
        return "https://storage.googleapis.com/cria-zoomify" in url


@click.command()
@click.option("--reino", type=str)  # nao implementei :(
@click.option("--filo", type=str)  # nao implementei :(
@click.option("--classe", type=str)  # nao implementei :(
@click.option("--ordem", type=str)  # nao implementei :(
@click.option("--familia", type=str)
@click.option("--genero", type=str)  # nao implementei :(
@click.option("--epiteto_especifico", type=str)  # nao implementei :(
@click.option("--epiteto_infraespecifico", type=str)  # nao implementei :(
@click.option('--images', is_flag=True)
@click.version_option("2.0", prog_name="downloader-specieslink")
def main(classe,
         epiteto_especifico,
         epiteto_infraespecifico,
         familia,
         filo,
         genero,
         images,
         ordem,
         reino):
    engine, session = connect()
    engine.echo = False

    if not os.environ["SPLINK"]:
        raise ValueError

    create_table(engine)

    process = CrawlerProcess(get_project_settings())
    process.crawl(SpeciesLink, session=session)
    process.start()

    session.close()
    engine.dispose()


if __name__ == '__main__':
    main()
