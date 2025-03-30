import os

import click
import json

import requests

def create_url(images, limits, start):
    # Is necessary pass kingdom to avoid Fungi and Animale.
    url = f"https://specieslink.net/ws/1.0/search?apikey={os.environ["SPLINK"]}&offset={start}&limit={limits}&kingdom=Plantae"

    if images:
        url = url + "&images=yes"

    print(f"url {url}")
    return url

def make_request(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            json = response.json()
            if len(json) > 0:
                return json
    except requests.exceptions:
        raise ValueError


def get_numbers_matched_returned(images):
    url = create_url(images, 1, 0)

    json = make_request(url)
    if "numberReturned" in json and "numberMatched" in json:
        return json["numberMatched"], json["numberReturned"]

    return None, None

def save_json(i, j):
    filename = os.path.join("output", f"{i}+data.json")
    print(f"filename: {filename}")
    with open(filename, 'w') as file:
        json.dump(j, file)


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
    if not os.environ["SPLINK"]:
        raise ValueError

    number_matched, number_returned = get_numbers_matched_returned(images)

    print(f"number_returned {number_returned}")
    print(f"number_matched {number_matched}")

    if not number_matched and not number_returned:
        raise ValueError

    start = 0
    increment = 100
    limits = increment - 1
    number_reimaned = number_matched

    os.makedirs("output", exist_ok=True)

    i = 0
    while number_reimaned > 0:
        print(f"start: {start} limits: {limits} ")
        url = create_url(images, limits, start)
        j = make_request(url)
        save_json(i, j)

        i = i + 1
        start = limits + 1
        limits = (start + increment) - 1
        number_reimaned = number_reimaned - increment


if __name__ == '__main__':
    main()