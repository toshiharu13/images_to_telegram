import datetime
import logging
import os
import random
import shutil
import time
from pathlib import Path
from urllib.parse import urlparse

import requests
import telegram
from dotenv import load_dotenv

#  Кортеж с ожидаемыми расширениями изображений
#  используется в check_for_ext
IMG_EXT = ('.jpg', '.gif', '.png', '.jpeg')


def download_image(source, destination):
    """
    Функция скачивания изображения в локальную папку
    :param source: ссылка на скачивание
    :param destination: локальная папка
    :return: None
    """
    response = requests.get(source)
    response.raise_for_status()

    with open(destination, 'wb') as file:
        file.write(response.content)


def fetch_spacex_last_launch(link_to_download):
    """
    Функция скачивания изображений с сайта SpaceX
    :param link_to_download: ссылка на источник
    :return: None
    """
    response = requests.get(link_to_download)
    response.raise_for_status()
    spacex_api_data = response.json()
    logging.info(spacex_api_data)
    links = spacex_api_data['links']['patch']
    logging.info(links)
    for image_data in links:
        image_url = links[image_data]
        image_filename = split_file_name(image_url)
        copy_destination = Path.cwd()/'images'/image_filename
        download_image(image_url, copy_destination)
        logging.info(image_filename)


def split_file_name(url):
    """
    Функция парсинга имени файла из ссылки
    :param url: ссылка на скачивание
    :return: имя файла
    """
    parse_url = urlparse(url)
    path_to_file = parse_url.path
    file_name = os.path.split(path_to_file)[1]
    return file_name


def get_nasa_images(link_to_download, key):
    """
    Функция скачивания изображений(кроме земли) с сайта NASA
    :param link_to_download: ссылка на источник
    :param key: ключ к NASA
    :return: None
    """
    params = {'api_key': key, 'count': 30}
    response = requests.get(link_to_download, params=params)
    response.raise_for_status()
    spacex_links = response.json()
    logging.info(spacex_links)
    for spacex_link in spacex_links:
        image_url = spacex_link['url']
        image_filename = split_file_name(image_url)
        if not check_for_ext(image_filename):
            logging.info(f'{image_filename} not image! canceling')
            continue
        copy_destination = Path.cwd() / 'images' / image_filename
        download_image(image_url, copy_destination)
        logging.info(image_filename)


def get_nasa_earth_images(url_earth_nasa, key, not_full_link_to_image_earth):
    """
    Функция скачивания фотографий земли с сайта NASA.
    После передачи ссылки и ключа, функция собирает ссылку из ответа json,
    и по этой ссылке скачивает изображения
    :param url_earth_nasa: ссылка для первоначального запроса
    :param key:  ключ к сайту NASA
    :param not_full_link_to_image_earth: часть будущей ссылки на скачивание
    :return: None
    """
    params = {'api_key': key}
    response = requests.get(url_earth_nasa, params=params)
    response.raise_for_status()
    links_information = response.json()
    logging.info(links_information)
    for link_information in links_information:
        image_name = link_information['image']
        image_creation = link_information['date']
        parsed_image_creation = datetime.datetime.strptime(
            image_creation, '%Y-%m-%d %H:%M:%S'
        )
        full_link_to_image_earth = (f'{not_full_link_to_image_earth}'
                                    f'/{parsed_image_creation.year}'
                                    f'/{parsed_image_creation.month}'
                                    f'/{parsed_image_creation.day}/png'
                                    f'/{image_name}.png?api_key={nasa_key}')
        image_filename = split_file_name(full_link_to_image_earth)
        copy_destination = Path.cwd() / 'images' / image_filename
        download_image(full_link_to_image_earth, copy_destination)
        logging.info(image_filename)


def clear_image_folder(folder):
    """
    Функия очистки папки с изображениями
    :param folder: папка которую надо чистить(для гибгости)
    :return: None
    """
    try:
        shutil.rmtree(folder)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (folder, e))


def check_for_ext(filename):
    """
    Функция проверки расширения у полученого файла
    :param filename: проверяемый файл
    :return: True/False
    """
    splitted_ext = os.path.splitext(filename)[1]
    return splitted_ext in IMG_EXT


if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s; %(levelname)s; %(name)s; %(message)s',
        filename='logs.lod',
        filemode='w',
    )
    spacex_url = 'https://api.spacexdata.com/v4/launches/latest'
    nasa_url = 'https://api.nasa.gov/planetary/apod'
    nasa_earth_url = 'https://api.nasa.gov/EPIC/api/natural'
    image_link_to_build = 'https://api.nasa.gov/EPIC/archive/natural'
    nasa_key = os.getenv('NASA_KEY')

    while True:
        image_folder = Path.cwd()/'images'
        clear_image_folder(image_folder)
        Path(image_folder).mkdir(parents=True, exist_ok=True)
        get_nasa_images(nasa_url, nasa_key)
        fetch_spacex_last_launch(spacex_url)
        get_nasa_earth_images(nasa_earth_url, nasa_key, image_link_to_build)

        bot = telegram.Bot(token=os.getenv('TELEGRAMM_BOT_KEY'))
        images = os.listdir(image_folder)
        for image_count in images:
            image_filename = random.choice(images)
            with open(Path(image_folder/image_filename), 'rb') as image_file:
                bot.send_photo(
                    chat_id=os.getenv('TELEGRAM_GROUP_ID'), photo=image_file
                )
            logging.info(f' send {image_filename} to telegram')
            images.remove(image_filename)
            time.sleep(int(os.getenv('TIME_TO_SLEEP', default=86400)))
