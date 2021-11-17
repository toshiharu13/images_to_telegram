import requests
from pathlib import Path


def image_downloader(source, destination):
    response = requests.get(source)
    response.raise_for_status()

    with open(destination, 'wb') as file:
        file.write(response.content)


if __name__ == "__main__":
    filename = './images/hubble.jpeg'
    url_wiki_img = 'https://upload.wikimedia.org/wikipedia/commons/3/3f/HST-SM4.jpeg'
    Path('./images').mkdir(parents=True, exist_ok=True)
    url_spacex = 'https://api.spacexdata.com/v4/launches/latest'

    image_downloader(url_wiki_img, filename)

    response = requests.get(url_spacex)
    response.raise_for_status()
    print(response.json()['links']['patch'])



