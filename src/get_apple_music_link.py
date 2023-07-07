import requests


class GetAppleMusicLink:
    def __init__(self, artist, title):
        self.artist = artist
        self.title = title

        self.links = list(self.get_apple_music_links())

    def get_apple_music_links(self):
        def encode_uri(text):
            return requests.utils.quote(text, safe='')

        req_param = encode_uri(f'{self.title} {self.artist}')
        response = requests.get(f'https://itunes.apple.com/search?term={req_param}&entity=musicTrack')

        if response.status_code == 200:
            data = response.json()
            if data['resultCount'] > 0:
                result = data['results'][0]
                track_url = result['trackViewUrl']
                artist_url = result['artistViewUrl']
                return track_url, artist_url

        return None, None


if __name__ == "__main__":
    # Example usage:

    get_apple_music_links = GetAppleMusicLink("In My Head", "Bedroom")
    apple_music_track_link, apple_music_artist_link = get_apple_music_links.get_apple_music_links()

    if apple_music_track_link:
        print(f'Apple Music Track Link: {apple_music_track_link}')
    else:
        print('Track not found on Apple Music.')

    if apple_music_artist_link:
        print(f'Apple Music Artist Link: {apple_music_artist_link}')
    else:
        print('Artist not found on Apple Music.')
