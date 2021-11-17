import logging
import requests
import os
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv


def image_downloader(source, destination):
    response = requests.get(source)
    response.raise_for_status()

    with open(destination, 'wb') as file:
        file.write(response.content)


def fetch_spacex_last_launch(link_to_download):
    response = requests.get(link_to_download)
    response.raise_for_status()
    roster_of_links = response.json()['links']['patch']
    logging.info(roster_of_links)
    for link_image in roster_of_links:
        cleared_link = roster_of_links[link_image]
        parsed_link = urlparse(cleared_link)
        image_name_from_link = parsed_link.path
        filename_to_write = f'./images{image_name_from_link}'
        image_downloader(cleared_link, filename_to_write)
        logging.info(filename_to_write)



if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s; %(levelname)s; %(name)s; %(message)s',
        filename='logs.lod',
        filemode='w',
    )
    Path('./images').mkdir(parents=True, exist_ok=True)
    url_spacex = 'https://api.spacexdata.com/v4/launches/latest'
    url_nasa = 'https://api.nasa.gov/planetary/apod'
    key_nasa = os.getenv('NASA_KEY')
    params = {'api_key': key_nasa}
    nasa_response = requests.get(url_nasa, params=params)
    nasa_response.raise_for_status()
    # print(nasa_response.json())
    nasa_image_url = nasa_response.json()['hdurl']
    print(nasa_image_url)
    nasa_parse_url = urlparse(nasa_image_url)
    path_to_file = nasa_parse_url.path
    print(path_to_file)
    print(os.path.split(path_to_file))
    name_of_file = os.path.split(path_to_file)[1]
    print(name_of_file)
    print(os.path.splitext(name_of_file)[1])


    #fetch_spacex_last_launch(url_spacex)






