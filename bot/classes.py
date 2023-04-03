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
