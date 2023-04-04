import requests


def get_sounds(search: str = '') -> list[dict]:
    response = requests.get(
        f'http://127.0.0.1:8000/api/sound/sounds/'
    )
    return response.json()

def get_random_sounds() -> list[dict]:
    response = requests.get(
        'http://127.0.0.1:8000/api/sound/sounds/'
    )
    return response.json()

def get_authors_by_title(title: str = '') -> list[dict]:
    response = requests.get(
        'http://127.0.0.1:8000/api/author/'
    )
    return response.json()

def get_cover(url: str):
    response = requests.get(
        f'http://127.0.0.1:8000/{url}/'
    ).content

    with open('new_image.jpg', 'wb') as handler:
        handler.write(response)

    with open('new_image.jpg', 'rb') as hander:
        return hander.read()
