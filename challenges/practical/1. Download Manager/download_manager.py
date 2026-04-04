import concurrent.futures
import requests
import threading

from dataclasses import dataclass
from typing import Generator

@dataclass(slots=True)
class Configuration:
    url: str
    chunk_size: int
    threads: int 

@dataclass(slots=True)
class Info:
    url: str
    length: int | None
    content_type: str
    accepts_range: str

def probe(config: Configuration) -> Info | None:
    try:
        response = requests.head(config.url)
        response.raise_for_status()
        h = response.headers

        raw_length = h.get('Content-Length')
        length = int(raw_length) if raw_length else None

        content_type = h.get('Content-Type') or h.get('Transfer-Encoding') or 'unknown'
        accepts_ranges = h.get('Accept-Ranges', 'none')
        return Info(url=config.url, length=length, content_type=content_type, accepts_range=accepts_ranges)
    except requests.HTTPError as http_err:
        print(f'Network/HTTP Error: {http_err}')
    except Exception as err:
        print(f'Error: {err}')
    return None

def chunk_bytes(config: Configuration, info: Info) -> Generator[tuple]:
    size = (info.length + config.threads - 1) // config.threads
    for start in range(0, info.length, size):
        yield start, min(start + size - 1, info.length - 1)

def download_parts(config: Configuration, start: int, end: int):
        headers = {'Range': f'bytes={start}-{end}'}
        response = requests.get(url=config.url, headers=headers, stream=True)
        response.raise_for_status()

        with open('testing.png', 'r+b') as f:
            f.seek(start)
            for chunk in response.iter_content(config.chunk_size):
                if chunk:
                    f.write(chunk)

def download(config: Configuration, info: Info):
    if info.length is None:
        print('unknown size file.')
        response = requests.get(url=config.url, stream=True)
        response.raise_for_status()

        with open('testing.png', 'wb') as f:
            for chunk in response.iter_content(config.chunk_size):
                if chunk:
                    f.write(chunk)
        return

    with open('testing.png', 'wb') as f:
        f.truncate(info.length)
   
    if info.accepts_range == 'bytes':
        with concurrent.futures.ThreadPoolExecutor(max_workers=config.threads) as executor:
            futures = []

            for start, end in chunk_bytes(config, info):
                future = executor.submit(download_parts, config, start, end)
                futures.append(future)

            for future in futures:
                future.result()
    else:
        # here

        response = requests.get(url=config.url, stream=True)
        response.raise_for_status()

        with open('testing.png', 'wb') as f:
            for chunk in response.iter_content(config.chunk_size):
                if chunk:
                    f.write(chunk)

# c and i, testing variables for configuration and info
c = Configuration('https://avatars.githubusercontent.com/u/171996203', 1024, 4)
i = probe(c)

def suffix(num: int, decimal: bool = False) -> str:
    i = 0
    if decimal:
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        while num >= 1000 and i < len(units) - 1:
            num /= 1000
            i += 1
        return f'{num:.2f}{units[i]}'
    else:
        units = ['B', 'KiB', 'MiB', 'GiB', 'TiB']
        while num >= 1024 and i < len(units) - 1:
            num /= 1024
            i += 1
        return f'{num:.2f}{units[i]}'

