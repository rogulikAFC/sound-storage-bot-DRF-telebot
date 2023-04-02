import requests


def get_sounds(search: str='', page: int=1) -> list[dict]:
    response = requests.get(
        'http://127.0.0.1:8000/api/sound/sounds/'
    )
    return response.json()

def get_random_sounds() -> list[dict]:
    response = requests.get(
        'http://127.0.0.1:8000/api/sound/sounds/'
    )
    return response.json()
