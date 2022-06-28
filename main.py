import urllib
import argparse
import os
from dotenv import load_dotenv
import requests


def get_args():
    parser = argparse.ArgumentParser(
        description='Взаимодействие с сервисом "bitly.com"'
    )
    parser.add_argument("url")
    return parser.parse_args()


def get_short_link(token, long_url):
    headers = {
        'Authorization': 'Bearer {}'.format(token),
        'Content-Type': 'application/json'
    }
    payload = { 'long_url': long_url, 'domain': 'bit.ly'}
    response = requests.post(
        'https://api-ssl.bitly.com/v4/shorten',
        headers=headers,
        json=payload
    )
    response.raise_for_status()
    json_response = response.json()
    bitlink = json_response['link']
    return bitlink


def get_link_click_summary(url, token):
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = (('unit', 'month'), ('units', '1'))
    response = requests.get(
        'https://api-ssl.bitly.com/v4/bitlinks/{}/clicks/summary'.format(url),
        headers=headers,
        params=params
    )
    response.raise_for_status()
    click_count = response.json()['total_clicks']
    return click_count


def is_bitlink(link,token):
    headers = {'Authorization': 'Bearer {}'.format(token)}
    response = requests.get(
        f'https://api-ssl.bitly.com/v4/bitlinks/{link}',
        headers=headers
    )
    return response.ok


def main():
    load_dotenv()
    token = os.getenv("BITLY_TOKEN")
    args = get_args()
    user_link = args.url
    url_components = urllib.parse.urlparse(user_link)
    link = f'{url_components.netloc}{url_components.path}'
    try:
        if is_bitlink(link, token):
            click_count = get_link_click_summary(link, token)
            print('По Вашей ссылке {} переходов'.format(click_count))
        else:
            short_link = get_short_link(token, user_link)
            print('Сокращенная ссылка -  {}'.format(short_link))
    except (requests.ConnectionError, requests.HTTPError):
        print('Проверьте введенные данные!')


if __name__ == '__main__':
    main()
