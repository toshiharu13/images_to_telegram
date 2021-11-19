# images_to_telegram
Прогамма для загрузки изображений в телеграм-канале

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)

## Техническое описание

Программа предназначена для скачивания Изображений из открытых источников, и передачи их в телеграм канал с заданный интервалом.
Для скачивания используются три источника:
 - SpaceX

        https://api.spacexdata.com/v4/launches/latest
 - NASA

       https://api.nasa.gov/planetary/apod

       https://api.nasa.gov/EPIC/api/natural

 В бесконечном цикле:
 - изображения скачиваются в локальную паку
 - передаются в заранее настроенную группу telegram
 - после передачи последнего изображения, удаляются

## Системные требования
- [Python 3](https://www.python.org/)

## Установка

 - Cклонировать проект


        $ https://github.com/toshiharu13/images_to_telegram.git

 - Установить requirements.txt


        $ pip install -r requirements.txt

- Создать файл .env и заполнить в нем переменные:

   - NASA_KEY=<ваш токен, полученый на сайте NASA>
   - TELEGRAMM_BOT_KEY=<токен вашего телеграм бота>
   - TELEGRAM_GROUP_ID=<ID телеграм группы>
   - TIME_TO_SLEEP=<время задержки между публикациями фотографий>

Бот должен быть администратором telegram группы. Если не указывать TIME_TO_SLEEP, дефолтная задержка составит сутки.

## Запуск

      $ python3 main.py