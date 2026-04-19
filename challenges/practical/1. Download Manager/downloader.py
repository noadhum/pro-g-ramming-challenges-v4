import concurrent.futures
import json
import random
import string
import threading

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse, unquote
from typing import Any, Dict, Generator, List, Optional, Tuple

import requests
import tqdm

import file_type

@dataclass(slots=True)
class Configuration:
    url: str
    chunk_size: int
    threads: int 
    output: Optional[Path]

@dataclass(slots=True)
class Info:
    url: str
    length: Optional[int]
    content_type: str
    accepts_range: str

# trying if i can download these files
urls = {
    'png':'https://avatars.githubusercontent.com/u/171996203',
    'pdf':'https://file-examples.com/wp-content/uploads/2017/10/file-example_PDF_1MB.pdf',
    'zip':'https://sample-files.com/downloads/compressed/zip/basic-text.zip',
    'zip2':'https://samplefile.com/samples/download/archive/zip/zip_sample_file_25MB.zip/',
    'ogg':'https://commondatastorage.googleapis.com/codeskulptor-assets/Evillaugh.ogg',

    'c_dis':'https://miro.medium.com/v2/resize:fit:1222/1*OMzkvx96Stzs7LovaGjTFg.jpeg'
}

LOCK = threading.Lock()

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

def parse_content_disposition(response: requests.Response) -> Optional[List[str]]:
    content_disposition = response.headers.get('Content-Disposition', None)

    if not content_disposition:
        return
    
    buffer = ''
    result = []
    in_quote = False

    for char in content_disposition:
        if char == '"':
            in_quote = not in_quote
 
        if char == ';' and not in_quote:
            if buffer.strip():
                result.append(buffer.strip())
            buffer = ''
        else:
            buffer += char
    result.append(buffer.strip())
    return result

def extract_from_content_disposition(part: str) -> Optional[List[str]]:
    for prefix in ('filename*=', 'filename='):
        if part.startswith(prefix):
            return part[len(prefix):].strip('"').rsplit('.', 1)
    return None

def parse_url_path(config: Configuration) -> Optional[str]:
    path = urlparse(config.url).path
    filename = unquote(path.rsplit('/', 1)[-1])
    return filename if filename else None

def get_extension_from_type(info: Info) -> str:
    content_type = file_type.split_query_fragment(info.content_type)
    return file_type.TYPE_TO_EXTENSION.get(content_type, file_type.TYPE_TO_EXTENSION['application/octet-stream'])

def temp_filename_ext(response: requests.Response, config: Configuration, info: Info) -> Tuple[str, str]:
    # Content-Disposition
    content_disposition = response.headers.get('Content-Disposition')
    if content_disposition:
        parts = parse_content_disposition(response)
        for part in parts:
            if extract_from_content_disposition(part):
                return extract_from_content_disposition(part)
    
    # URL Path
    url_path = parse_url_path(config)
    if url_path:
        parts = url_path.split('.')
        if len(parts) > 1:
            return '.'.join(parts[:-1]), parts[-1]
        return url_path, 'bin'
    
    # Content-Type
    if info.content_type and file_type.valid_type(info.content_type):
        extension = file_type.to_extension(info.content_type)
        return 'download', extension[0]
    return 'download', 'bin'

def get_filename_ext(config: Configuration) -> Tuple[str, str]:
    if config.output.exists():
        with open(config.output, 'rb') as f:
            data = f.read()
        extension = file_type.sniff_bytes(data)
        return 'download', extension
    return 'download', 'bin'
    
def chunk_bytes(config: Configuration, info: Info) -> Generator[Tuple[int, int]]:
    size = (info.length + config.threads - 1) // config.threads
    for start in range(0, info.length, size):
        yield start, min(start + size - 1, info.length - 1)

def download_parts(config: Configuration, info: Info, start: int, end: int):
        headers = {'Range': f'bytes={start}-{end}'}
        response = requests.get(url=config.url, headers=headers, stream=True)
        response.raise_for_status()

        with open(config.output or 'testing.png', 'r+b') as f:
            f.seek(start)
            for chunk in response.iter_content(config.chunk_size):
                if chunk:
                    f.write(chunk)
        
        with LOCK:
            # resume json
            pass

def multi_thread_download(config: Configuration, info: Info):
    with open(config.output or 'testing.png', 'w+b') as f:
            f.truncate(info.length)

    with concurrent.futures.ThreadPoolExecutor(max_workers=config.threads) as executor:
        futures = []
        for start, end in chunk_bytes(config, info):
            future = executor.submit(download_parts, config, info, start, end)
            futures.append(future)

        for future in futures:
            future.result()

def single_thread_download(config: Configuration):
    filename = config.output or Path('testing.png')
    existing = filename.stat().st_size if filename.exists() else 0
    headers = {'Range':f'bytes={existing}-'} if existing > 0 else None
    mode = 'ab' if existing > 0 else 'wb'

    response = requests.get(url=config.url, headers=headers, stream=True)
    response.raise_for_status()

    with open(filename, mode) as f:
        for chunk in response.iter_content(config.chunk_size):
            if chunk:
                f.write(chunk)

def download(config: Configuration, info: Info):
    if info.length is None:
        response = requests.get(url=config.url, stream=True)
        response.raise_for_status()

        with open(config.output or 'testing.png', 'wb') as f:
            for chunk in response.iter_content(config.chunk_size):
                if chunk:
                    f.write(chunk)
        return
    
    response = requests.get(url=config.url, headers={'Range':'bytes=0-0'})
    if response.status_code == 206:
        multi_thread_download(config, info)
    elif response.status_code == 200:
        single_thread_download(config)

# -- Utilites
def format_size(num: int, decimal: bool = False) -> str:
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

def read_json(filename: str) -> Dict[str, Any]:
    with open(filename, "r") as f:
        return json.load(f)
    
def write_json(filename: str, data: Dict[str, Any]) -> None:
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def random_name(length: int = 8) -> str:
    return ''.join([random.choice(string.ascii_letters + string.digits) for letter in range(length)])
    
# r for response, c for config, and i for info, testing variables
r = requests.get(url=urls['png'])
c = Configuration(urls['png'], 1024, 4, None)
i = probe(c)

# -- Main
def main() -> None:
    pass