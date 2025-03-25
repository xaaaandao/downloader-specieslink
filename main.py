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

from scrapy.crawler import CrawlerProcess
from scrapy.http import FormRequest
from scrapy.utils.project import get_project_settings

from database import connect
from models import Record, get_base


class SpeciesLink(scrapy.Spider):
    name = 'specieslink'
    base_url = 'https://specieslink.net/search/index'
    form_data = {
        'action': 'records',
        'graph_type': 'horizontalBar',
        'graph_sort': 'value',
        'from': '0',
        'recs_order_by': 'random_order',
        'dups_mode': 'collect_full_key',
        'coll_groups': '',
        'coll_networks': '',
    }

    def __init__(self, barcodes, urls):
        self.barcodes = barcodes
        self.urls = urls

    def start_requests(self):
        for i, barcode in enumerate(self.barcodes):
            print('%d-%d' % (i, len(self.barcodes)))
            self.form_data['barcode'] = barcode

            yield FormRequest(self.base_url,
                              formdata=self.form_data,
                              callback=self.parse)

    def parse(self, response):
        for url in response.xpath('//img/@src').extract():
            if 'https://storage.googleapis.com/cria-zoomify' in url:
                if url not in self.urls:
                    self.urls.append(url)


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

    start = 0
    limit = 5000
    while True:
        url = f"https://specieslink.net/ws/1.0/search?apikey={os.environ["SPLINK"]}&offset={start}&limit={limit}"

        if images:
            url = url + "&flags=photo"

        print(f"url {url}")

        try:
            make_request(session, url)
        except requests.exceptions:
            break

        start = limit + 1
        limit = start + 5000

    session.close()
    engine.dispose()


def make_request(session, url):
    response = requests.get(url)
    if response.status_code == 200:
        json = response.json()
        if len(json) > 0:
            records = [Record(barcode=j["properties"]["barcode"], family=j["properties"]["family"], json=j["properties"]) for j in json["features"] if "properties" in j if has_barcode_and_family(j)]
            session.add_all(records)
            session.commit()


def has_barcode_and_family(j):
    return "barcode" in j["properties"] and "family" in j["properties"]


# def save_urls(familia, imagens, urls):
#     df = pd.DataFrame({'urls': urls})
#     df.to_csv(get_filename('csv', familia, imagens), quoting=2, sep=";")
#
#
# def save_json(family, images, records):
#     filename = get_filename('json', family, images)
#     with open(filename, 'w') as file:
#         json.dump(records, file)
#
#
# def get_filename(extension, family, images):
#     filename = 'request+family+%s' % family
#     if images:
#         filename = filename + '+images'
#     current_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y+%m+%d')
#     filename = filename + '+%s.%s' % (current_date, extension)
#     print('save %s' % filename)
#     return filename


if __name__ == '__main__':
    main()
