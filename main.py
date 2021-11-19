import datetime
import logging
import random
import requests
import os
from pathlib import Path
import shutil
import time
from urllib.parse import urlparse

from dotenv import load_dotenv
import telegram


img_ext = ('.jpg', '.gif', '.png', '.jpeg')


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
    roster_of_space_data = response.json()
    for dirty_link_to_image in roster_of_space_data:
        image_url = dirty_link_to_image['url']
        filename_to_write = split_file_name(image_url)
        if not check_for_ext(filename_to_write):
            logging.info(f'{image_url} not image! canceling')
            continue
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


def clear_image_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def check_for_ext(file):
    """
    Функция проверки расширения у полученого файла
    :param file: проверяемый файл
    :return: True/False
    """
    splitted_ext = os.path.splitext(file)[1]
    if splitted_ext:
        if splitted_ext in img_ext:
            return True
    return False


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

    while True:
        clear_image_folder('./images')
        nasa_images_get(url_nasa, key_nasa)
        fetch_spacex_last_launch(url_spacex)
        nasa_earth_images_get(
            url_earth_nasa, key_nasa, not_full_link_to_image_earth
        )

        bot = telegram.Bot(token=os.getenv('TELEGRAMM_BOT_KEY'))
        images_roster = os.listdir('./images')
        for image_count in range(len(images_roster)):
            image_in_focus = random.choice(images_roster)
            bot.send_photo(
                chat_id=os.getenv('MY_TEST_GROUP_ID'),
                photo=open(f'images/{image_in_focus}', 'rb')
            )
            print(image_in_focus)
            images_roster.remove(image_in_focus)
            time.sleep(int(os.getenv('TIME_TO_SLEEP', default=86400)))
