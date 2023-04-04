import requests


class Sound:
    def __init__(self, title):
        self.title = title
        self.authors = list()
        self.sound = None
        self.cover = None

    def upload_to_database(self) -> bool:
        self.authors = set(self.authors)
        
        response = requests.post(
            'http://127.0.0.1:8000/api/sound/sounds/',

            data={
                'title': self.title,
                'authors': self.authors,
            },

            files={
                'cover': (f'{self.title}.jpg', self.cover),
                'sound': (f'{self.title}.mp3', self.sound)
            }
        )
        
        return response.ok
    
    @classmethod
    def get_sound_info(cls, id: str) -> dict:
        response = requests.get(
            f'http://127.0.0.1:8000/api/sound/sounds/?id={id}'
        )

        return response.json()[0]
    
    @classmethod
    def get_sound_file(cls, url: str):
        response = requests.get(
            f'http://127.0.0.1:8000/{url}/'
        ).content

        with open('new_file.mp3', 'wb') as handler:
            handler.write(response)

        with open('new_file.mp3', 'rb') as hander:
            return hander.read()

    @classmethod
    def search_sounds(cls, search: str, page: int = 1) -> list[dict]:
        response = requests.get(
            f'http://127.0.0.1:8000/api/sound/sounds/?search={search}'
        )
        
        return response.json()
    

class Album:
    def __init__(self, title):
        self.title = title
        self.sounds = list()
        self.cover = None

    def upload_to_database(self) -> bool:
        self.sounds = set(self.sounds)
        
        response = requests.post(
            'http://127.0.0.1:8000/api/sound/albums/',

            data={
                'title': self.title,
                'sounds': self.sounds,
            },

            files={
                'cover': (f'{self.title}.jpg', self.cover),
            }
        )
        
        return response.ok
    
    @classmethod
    def search_albums(cls, search: str) -> list[dict]:
        response = requests.get(
            f'http://127.0.0.1:8000/api/sound/albums/?search={search}'
        )
        
        return response.json()
    
    @classmethod
    def get_album_info(cls, id: str) -> dict:
        response = requests.get(
            f'http://127.0.0.1:8000/api/sound/albums/?id={id}'
        )

        return response.json()[0]
