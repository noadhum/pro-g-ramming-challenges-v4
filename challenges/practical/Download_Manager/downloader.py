import argparse
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

if not requests:
    raise ModuleNotFoundError("Module 'requests' not found.")

if not tqdm:
    raise ModuleNotFoundError("Module 'tqdm' not found.")

import file_type

@dataclass(slots=True)
class Configuration:
    url: str
    chunk_size: int
    threads: int 
    output: Optional[Path]
    resume_path: Path

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

def extract_from_content_disposition(part: str) -> Optional[Tuple[str, str]]:
    for prefix in ('filename*=', 'filename='):
        if part.startswith(prefix):
            filename, ext = part[len(prefix):].strip('"').rsplit('.', 1)
            return filename, ext
    return None

def parse_url_path(config: Configuration) -> Optional[str]:
    path = urlparse(config.url).path
    filename = unquote(path.rsplit('/', 1)[-1])
    return filename if filename else None

def get_extension_from_type(info: Info) -> str:
    content_type = file_type.split_query_fragment(info.content_type)
    return file_type.TYPE_TO_EXTENSION.get(content_type, file_type.TYPE_TO_EXTENSION['application/octet-stream'])[0]

def resolve_initial_name(response: requests.Response, config: Configuration, info: Info) -> Tuple[str, str]:
    content_disposition = response.headers.get('Content-Disposition')
    if content_disposition:
        parts = parse_content_disposition(response)
        for part in parts:
            if extract_from_content_disposition(part):
                return extract_from_content_disposition(part)
    
    url_path = parse_url_path(config)
    if url_path:
        parts = url_path.split('.')
        if len(parts) > 1:
            return '.'.join(parts[:-1]), parts[-1]
        return url_path, 'oadm'
    
    if info.content_type and file_type.valid_type(info.content_type):
        extension = file_type.to_extension(info.content_type)
        return 'download', extension[0]
    return 'download', 'oadm'

def sniff_extension(config: Configuration) -> Tuple[str, str]:
    if config.output.exists():
        size = config.output.stat().st_size
        if size >= 4096:
            data = read_binary(config.output, 4096)
        else:
            data = read_binary(config.output, None)
        
        return 'download', file_type.sniff_bytes(data)
    return 'download', 'bin'

    
def chunk_bytes(config: Configuration, info: Info) -> Generator[Tuple[int, int]]:
    size = (info.length + config.threads - 1) // config.threads
    for start in range(0, info.length, size):
        yield start, min(start + size - 1, info.length - 1)

def init_resume(config: Configuration, info: Info) -> Dict[str, str | List[Dict[str, int]]]:
    if not info.length:
        return
    
    if not config.resume_path.exists():
        
        json_data = {
            'url': config.url,
            'length': info.length,
            'parts': []
        }

        for index, (start, end) in enumerate(chunk_bytes(config, info)):
            json_data['parts'].append(
                {
                    'index': index,
                    'start': start,
                    'end': end,
                    'downloaded': 0,
                }
            )

        write_json(str(config.resume_path), json_data)
    return str(config.resume_path)

def download_parts(config: Configuration, info: Info, part: Dict[str, int]):
    index = part['index']
    start = part['start']
    end = part['end']
    
    if part['downloaded'] >= end - start + 1:
        return

    resume_start = start + part['downloaded']
    headers = {'Range': f'bytes={resume_start}-{end}'}

    response = requests.get(url=config.url, headers=headers, stream=True)
    response.raise_for_status()
    
    size = 64 * 1024
    buffer = 0

    with open(config.output, 'r+b') as f:
        f.seek(resume_start)
        for chunk in response.iter_content(config.chunk_size):
            if chunk:
                f.write(chunk)
                buffer += len(chunk)

            if buffer >= size:
                with LOCK:
                    data = read_json(config.resume_path)
                    data['parts'][index]['downloaded'] += buffer
                    write_json(config.resume_path, data)
                    buffer = 0

        if buffer > 0:
            with LOCK:
                data = read_json(config.resume_path)
                data['parts'][index]['downloaded'] += buffer
                write_json(config.resume_path, data)

def multi_thread_download(config: Configuration, info: Info, ):
    if not config.output.exists():
        with open(config.output, 'w+b') as f:
                f.truncate(info.length)
    
    resume_path = init_resume(config, info)
    json_data = read_json(resume_path)
    parts = json_data['parts']

    with concurrent.futures.ThreadPoolExecutor(max_workers=config.threads) as executor:
        futures = []
        for part in parts:
            future = executor.submit(download_parts, config, info, part)
            futures.append(future)

        for future in futures:
            future.result()

def single_thread_download(config: Configuration):
    filename = config.output
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

        with open(config.output, 'wb') as f:
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

def read_binary(filename: str | Path, size: Optional[int]) -> bytes:
    if size:
        with open(filename, 'rb') as f:
            return f.read(size)
    
    with open(filename, 'rb') as f:
        return f.read()

# Simple JSON functions
def read_json(filename: str | Path) -> Dict[str, Any]:
    with open(filename, "r") as f:
        return json.load(f)
    
def write_json(filename: str | Path, data: Dict[str, Any]) -> None:
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def random_name(length: int = 8) -> str:
    return ''.join([random.choice(string.ascii_letters + string.digits) for c in range(length)])

# -- Main
def cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='Download Manager (oadm)',
        description='Simple Downloader made by me (https://github.com/noadhum)',
        usage='downloader.py <url> [options]',
        epilog="""
Examples:
    downloader.py https://example.com/file
    downloader.py https://example.com/file -o cat
""",
formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('url', type=str, help='URL to download')
    parser.add_argument('-s', '--size', type=int, help='Chunk size in bytes', default=1024)
    parser.add_argument('-t', '--threads', type=int, help='Number of threads', default=4)
    parser.add_argument('-o', '--output', type=str, help='Output name (without extension)', default=random_name())

    args = parser.parse_args()
    return args

def main() -> None:
    args = cli()

    filename = args.output

    config = Configuration(
        args.url,
        args.size,
        args.threads,
        Path(f"{filename or 'download'}.oadm"),
        Path(f"{filename or 'resume'}_oadm.json"))
    
    info = probe(config)
    if not info:
        return
    
    response = requests.get(url=config.url, stream=True)
    fname, temp_ext = resolve_initial_name(response, config, info)
    temp_path = Path(f'{filename or fname}.{temp_ext}')
    config.output = temp_path

    download(config, info)

    extension = sniff_extension(config)[-1]
    path = temp_path.with_suffix(f'.{extension}')
    temp_path.replace(path)

main()