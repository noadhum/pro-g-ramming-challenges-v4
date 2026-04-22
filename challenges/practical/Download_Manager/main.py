from pathlib import Path

from downloader.model import Input
from downloader.download import Downloader, HTTPClient

DEFAULT_UA = 'OADownloadManager/1.0'

def cli():
    pass

def main() -> None:
    user_input = Input('https://avatars.githubusercontent.com/u/171996203', 1024, 4, Path('testing.png'), True, DEFAULT_UA)
    
    client = HTTPClient(DEFAULT_UA)
    info = client.probe(user_input.url)

    downloader = Downloader(client, user_input, info)
    downloader.download()

main()