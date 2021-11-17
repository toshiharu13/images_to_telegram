import requests
from pathlib import Path
from urllib.parse import urlparse


def image_downloader(source, destination):
    response = requests.get(source)
    response.raise_for_status()

    with open(destination, 'wb') as file:
        file.write(response.content)


if __name__ == "__main__":
    # filename = './images/hubble.jpeg'
    # url_wiki_img = 'https://upload.wikimedia.org/wikipedia/commons/3/3f/HST-SM4.jpeg'
    Path('./images').mkdir(parents=True, exist_ok=True)
    url_spacex = 'https://api.spacexdata.com/v4/launches/latest'

    response = requests.get(url_spacex)
    response.raise_for_status()
    roster_of_links = response.json()['links']['patch']
    # print(roster_of_links)
    for link_image in roster_of_links:
        cleared_link = roster_of_links[link_image]
        # print(cleared_link)
        parsed_link = urlparse(cleared_link)
        image_name_from_link = parsed_link.path
        filename_to_write = f'./images{image_name_from_link}'
        image_downloader(cleared_link, filename_to_write)
        # print(filename_to_write)


    # image_downloader(url_wiki_img, filename)



