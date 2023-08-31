import json

import requests
from settings import settings


def fetch_user(user_id: int):
    url = f'{settings.BASE_URL}:{settings.USER_PORT}/registration'
    params = {'user_id': user_id}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        if response.status_code == 200:
            user_data = response.json().get('data')
            return user_data
        else:
            print(f"Unexpected response status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error making the request: {str(e)}")
        return None


def fetch_label(label_id: list):
    url = f'{settings.BASE_URL}:{settings.LABEL_PORT}/retrieve/'
    payload = {'label_id': label_id}
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, json=payload, headers=headers)

    response.raise_for_status()

    return response.json().get('data')