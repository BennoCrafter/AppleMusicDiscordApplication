from flask import Flask, request
import json


class Server:
    def __init__(self):
        self.app = Flask(__name__)
        self.song = None
        self.setup_routes()

    def save_current_song(self, value):
        if value is not None:
            with open('current_song.txt', 'w') as file:
                file.write(value)

    def load_current_song(self):
        with open('current_song.txt', 'r') as file:
            return file.read()

    def setup_routes(self):
        @self.app.route('/', methods=['GET', 'POST'])
        def index():
            if request.method == 'POST':
                response = json.loads(request.get_data().decode('utf-8'))
                self.song = response.get('')
                self.save_current_song(self.song)
                return 'Song information loaded successfully via POST.'
            else:
                return 'This route only accepts POST requests.'

        @self.app.route('/get_song_info')
        def get_song_info():
            if self.song is not None:
                return f'The song value is: {self.song}'
            else:
                self.song = self.load_current_song()
                if self.song:
                    return f'The song value is: {self.song}'
                else:
                    return 'No song loaded.'

    def run(self):
        self.app.run()

if __name__ == '__main__':
    server = Server()
    server.run()
