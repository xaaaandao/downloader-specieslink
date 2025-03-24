import collections
import os

import click
import datetime
import json

import numpy as np
import pandas as pd
import re

import requests
import scrapy

from scrapy.crawler import CrawlerProcess
from scrapy.http import FormRequest
from scrapy.utils.project import get_project_settings

from database import connect
from models import Record


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


@click.command()
@click.option('--reino', type=str)  # nao implementei :(
@click.option('--filo', type=str)  # nao implementei :(
@click.option('--classe', type=str)  # nao implementei :(
@click.option('--ordem', type=str)  # nao implementei :(
@click.option('--familia', type=str)
@click.option('--genero', type=str)  # nao implementei :(
@click.option('--epitetoespecifico', type=str)  # nao implementei :(
@click.option('--epitetoinfraespecifico', type=str)  # nao implementei :(
# @click.option('--images', is_flag=True)
@click.version_option('0.0.1', prog_name='downloader-specieslink')
def main(reino, filo, classe, ordem, familia, genero, epitetoespecifico, epitetoinfraespecifico):

    engine, session = connect()
    engine.echo = False

    # if not os.environ["SPLINK"]:
    #     raise ValueError
    #
    # start = 0
    # limit = 5000
    # families = []
    # while True:
    #     url = f"https://specieslink.net/ws/1.0/search?apikey={os.environ["SPLINK"]}&offset={start}&limit={limit}&flags=photo"
    #     print(f"url {url}")
    #
    #     # if images:
    #     #     url = url + "&flags=photo"
    #
    #     try:
    #         response = requests.get(url)
    #         if response.status_code == 200:
    #             records = response.json()
    #             if len(records) > 0:
    #                 families = families + [Record(r["properties"]["barcode"], r["properties"]["family"]) for r in records["features"]  if "properties" in r and "family" in r["properties"]]
    #
    #     except requests.exceptions:
    #         break
    #
    #     start = limit + 1
    #     limit = limit + limit


    session.close()
    engine.dispose()


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
