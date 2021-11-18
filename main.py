import datetime
import logging
import requests
import os
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
import telegram


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
        filename_to_write = split_file_name(cleared_link)
        image_downloader(cleared_link, f'./images/{filename_to_write}')
        logging.info(filename_to_write)


def split_file_name(url):
    parse_url = urlparse(url)
    path_to_file = parse_url.path
    name_of_file = os.path.split(path_to_file)[1]
    return name_of_file


def nasa_images_get(link_to_download, key):
    params = {'api_key': key,
              'count': 30,
              }
    response = requests.get(link_to_download, params=params)
    response.raise_for_status()
    print(response.json())
    roster_of_space_data = response.json()
    for dirty_link_to_image in roster_of_space_data:
        image_url = dirty_link_to_image['url']
        #print(image_url)
        filename_to_write = split_file_name(image_url)
        print(filename_to_write)
        image_downloader(image_url, f'./images/{filename_to_write}')
        logging.info(filename_to_write)


def nasa_earth_images_get(url_earth_nasa, key, not_full_link_to_image_earth):
    params = {'api_key': key}
    response = requests.get(url_earth_nasa, params=params)
    response.raise_for_status()
    background_information = response.json()
    for dirty_data in background_information:
        name_of_image = dirty_data['image']
        date_of_creation = dirty_data['date']
        parsed_data = datetime.datetime.strptime(
            date_of_creation, '%Y-%m-%d %H:%M:%S'
        )
        full_link_to_image_earth = f'{not_full_link_to_image_earth}/{parsed_data.year}/{parsed_data.month}/{parsed_data.day}/png/{name_of_image}.png?api_key={key_nasa}'
        filename_to_write = split_file_name(full_link_to_image_earth)
        image_downloader(
            full_link_to_image_earth, f'./images/{filename_to_write}'
        )
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
    url_earth_nasa = 'https://api.nasa.gov/EPIC/api/natural'
    not_full_link_to_image_earth = 'https://api.nasa.gov/EPIC/archive/natural'
    key_nasa = os.getenv('NASA_KEY')

    #nasa_images_get(url_nasa, key_nasa)
    #fetch_spacex_last_launch(url_spacex)
    #nasa_earth_images_get(url_earth_nasa, key_nasa, not_full_link_to_image_earth)

bot = telegram.Bot(token=os.getenv('TELEGRAMM_BOT_KEY'))
bot.send_message(text='Hi! samurai!', chat_id=os.getenv('MY_TEST_GROUP_ID'))




