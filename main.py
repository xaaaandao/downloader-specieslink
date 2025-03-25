import collections
import os

import click
import datetime
import json

import numpy as np
import pandas as pd
import re

import sqlalchemy as sa

import requests
import scrapy
from requests import session

from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import CloseSpider
from scrapy.http import FormRequest
from scrapy.utils.project import get_project_settings

from database import connect
from models import Record, get_base


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
        start = 0

        while True:
            print(start)
            self.form_data["from"] = str(start)
            yield FormRequest(self.base_url,
                                formdata=self.form_data,
                                callback=self.parse)
            start = int(start) + 100


    def parse(self, response):
        tables = response.xpath("//table[contains(@class, 'recs-table')]")
        # print(tables)
        if len(tables) == 0:
            raise CloseSpider("table is empty!")

        for table_index, table in enumerate(tables):
            tN_texts = table.xpath(".//span[contains(@class, 'tN')]/text()").extract_first()

            tF_texts = table.xpath(".//span[contains(@class, 'tF')]/text()").extract_first()

            img_srcs = table.xpath(".//img/@src")
            img_srcs = [i for i in img_srcs.extract() if "https://storage.googleapis.com/cria-zoomify" in i]
            # print(tN_texts, tF_texts, img_srcs)
            records = Record(barcode=tN_texts, family=tF_texts, json=None, images=img_srcs)
            self.session.add(records)

        self.session.commit()


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


@click.command()
@click.option("--reino", type=str)  # nao implementei :(
@click.option("--filo", type=str)  # nao implementei :(
@click.option("--classe", type=str)  # nao implementei :(
@click.option("--ordem", type=str)  # nao implementei :(
@click.option("--familia", type=str)
@click.option("--genero", type=str)  # nao implementei :(
@click.option("--epitetoespecifico", type=str)  # nao implementei :(
@click.option("--epitetoinfraespecifico", type=str)  # nao implementei :(
@click.option('--images', is_flag=True)
@click.version_option("2.0", prog_name="downloader-specieslink")
def main(reino, filo, classe, ordem, familia, genero, epitetoespecifico, epitetoinfraespecifico, images):
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
