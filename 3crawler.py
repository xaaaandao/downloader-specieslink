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
            print(f"i: {i} barcode: {b.barcode} total: {len(barcodes)}")
            self.form_data["barcode"] = b.barcode
            yield FormRequest(self.base_url,
                              formdata=self.form_data,
                              callback=self.parse,
                              meta={"barcode": b.barcode})

    def parse(self, response):
        barcode = response.meta["barcode"]
        urls = [url for url in response.xpath("//img/@src").extract() if self.url_valid(url)]
        self.session.query(Record).filter(Record.barcode.__eq__(barcode)).update({Record.images: urls})
        self.session.commit()

    def url_valid(self, url):
        return "https://storage.googleapis.com/cria-zoomify" in url


def main():
    engine, session = connect()
    engine.echo = False

    create_table(engine)

    process = CrawlerProcess(get_project_settings())
    process.crawl(SpeciesLink, session=session)
    process.start()

    session.close()
    engine.dispose()


if __name__ == '__main__':
    main()
