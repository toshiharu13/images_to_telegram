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
img_ext = ('.jpg', '.gif', '.png', '.jpeg')


def download_images(source, destination):
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
    logging.info(response.json())
    links = response.json()['links']['patch']
    logging.info(links)
    for image_data in links:
        image_url = links[image_data]
        image_filename = split_file_name(image_url)
        download_images(image_url, f'./images/{image_filename}')
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
    params = {'api_key': key,
              'count': 30,
              }
    response = requests.get(link_to_download, params=params)
    response.raise_for_status()
    spacex_links = response.json()
    logging.info(spacex_links)
    for spacex_link in spacex_links:
        image_url = spacex_link['url']
        image_filename = split_file_name(image_url)
        if not check_for_ext(image_filename):
            logging.info(f'{image_url} not image! canceling')
            continue
        download_images(image_url, f'./images/{image_filename}')
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
        download_images(
            full_link_to_image_earth, f'./images/{image_filename}'
        )
        logging.info(image_filename)


def clear_image_folder(folder):
    """
    Функия очистки папки с изображениями
    :param folder: папка которую надо чистить(для гибгости)
    :return: None
    """
    for file_name in os.listdir(folder):
        file_path = os.path.join(folder, file_name)
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
    spacex_url = 'https://api.spacexdata.com/v4/launches/latest'
    nasa_url = 'https://api.nasa.gov/planetary/apod'
    nasa_earth_url = 'https://api.nasa.gov/EPIC/api/natural'
    image_link_to_build = 'https://api.nasa.gov/EPIC/archive/natural'
    nasa_key = os.getenv('NASA_KEY')

    while True:
        clear_image_folder('./images')
        get_nasa_images(nasa_url, nasa_key)
        fetch_spacex_last_launch(spacex_url)
        get_nasa_earth_images(nasa_earth_url, nasa_key, image_link_to_build)

        bot = telegram.Bot(token=os.getenv('TELEGRAMM_BOT_KEY'))
        images = os.listdir('./images')
        for image_count in range(len(images)):
            image_filename = random.choice(images)
            with open(f'images/{image_filename}', 'rb') as image_file:
                bot.send_photo(
                    chat_id=os.getenv('TELEGRAM_GROUP_ID'), photo=image_file
                )
            logging.info(f' send {image_filename} to telegram')
            images.remove(image_filename)
            time.sleep(int(os.getenv('TIME_TO_SLEEP', default=86400)))
