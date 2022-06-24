
import argparse
import os
from dotenv import load_dotenv
import requests

load_dotenv()

def get_args():
    parser = argparse.ArgumentParser(description='Взаимодействие с сервисом "bitly.com"')
    parser.add_argument("url")
    return parser.parse_args()

def get_short_link(token, long_url):
    headers = {
        'Authorization': 'Bearer {}'.format(token),
        'Content-Type': 'application/json'}
    payload = { 'long_url': long_url, 'domain': 'bit.ly'}
    response = requests.post('https://api-ssl.bitly.com/v4/shorten', headers=headers, json=payload)
    response.raise_for_status()
    json_response = response.json()
    bitlink = json_response['link']
    return bitlink

def is_url_available(url):
    response = requests.get(url)
    return response.ok


def get_link_click_summary(url, token):
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = (('unit', 'month'), ('units', '1'))
    response = requests.get('https://api-ssl.bitly.com/v4/bitlinks/{}/clicks/summary'.format(url),
                            headers=headers, params=params)
    response.raise_for_status()
    click_count = response.json()['total_clicks']
    return click_count


def is_bitlink(link,token):
    headers = {'Authorization': 'Bearer {}'.format(token)}
    response = requests.get(f'https://api-ssl.bitly.com/v4/bitlinks/{link}', headers=headers)
    return response.ok


def main():

    token = os.getenv("BITLY_TOKEN")
    args = get_args()
    user_link = args.url
    bitly_url = "https://api-ssl.bitly.com/"
    try:
        link_is_available = is_url_available(user_link)
    except (requests.exceptions.ConnectionError, requests.HTTPError,
            requests.exceptions.MissingSchema, requests.exceptions.InvalidURL, requests.exceptions.InvalidSchema ):
         link_is_available = False
    if not link_is_available:
        exit('возможно вы ввели не корректную ссылку или проблема с подключением')
    if not is_url_available(bitly_url):
        exit(f'Сервис {bitly_url} временно не доступен ')
    _, cutten_link = user_link.split('://')
    if is_bitlink(cutten_link, token):
        try:
            click_count = get_link_click_summary(cutten_link, token)
            exit("Количество переходов по битлинку - {} ".format(click_count))
        except (requests.HTTPError, requests.ConnectionError):
            exit('Ошибка HTTP или ошибка подключения')
    if link_is_available:
        try:
            shorter_url = get_short_link(token, user_link)
            exit("Сокращенная ссылка - {}".format(shorter_url))
        except (requests.HTTPError, requests.ConnectionError):
            exit('Ошибка HTTP или ошибка подключения')

if __name__ == '__main__':
    main()
