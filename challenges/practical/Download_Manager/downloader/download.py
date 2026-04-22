import concurrent.futures as futures
import threading

from typing import Any, List, Tuple

from .model import Input, FileInfo
from .utilities import chunk_bytes

try:
    import requests
except ImportError:
    raise ModuleNotFoundError("Error: required 'requests' library not found, install it with: 'pip install requests'")

LOCK = threading.Lock()

class HTTPClient:
    def __init__(self, ua: str) -> None:
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': ua})
    
    def get(self, url: str, **kwargs: Any) -> requests.Response:
        response = self.session.get(url, **kwargs)
        response.raise_for_status()
        return response
    
    def probe(self, url: str) -> FileInfo:
        response = self.session.head(url)
        response.raise_for_status()
        headers = response.headers

        content_length = headers.get('Content-Length')
        length = int(content_length) if content_length else None

        mime_type = (
            headers.get('Content-Type')
            or headers.get('Transfer-Encoding')
            or 'application/octet-stream'
        )

        ranges = headers.get('Accept-Ranges')
        content_disposition = headers.get('Content-Disposition')

        return FileInfo(url, length, mime_type, content_disposition, ranges)

class Downloader:
    def __init__(self, client: HTTPClient, input: Input, info: FileInfo) -> None:
        self.client = client
        self.input = input
        self.info = info

    def single_thread(self):
        """
        Download file using a single streaming request.
        """

        response = self.client.get(self.input.url, stream=True)
        
        with open(self.input.file_path, 'wb') as f:
            for chunk in response.iter_content(self.input.chunk_size):
                if chunk:
                    f.write(chunk)
    
    def _download_part(self, part: Tuple[int, int]):
        """
        Download specific byte-range of the file
        """

        if not self.input.file_path.exists():
            with open(self.input.file_path, 'w+b') as f:
                f.truncate(self.info.length)

        start, end = part
        headers = {'Range': f'bytes={start}-{end}'}
        response = self.client.get(self.input.url, headers=headers, stream=True)

        with open(self.input.file_path, 'r+b') as f:
            f.seek(start)
            for chunk in response.iter_content(self.input.chunk_size):
                if chunk:
                    f.write(chunk)

    def multi_thread(self):
        """
        Download file using multiple threads with byte-range splitting.
        """

        if self.info.length is None:
            return self.single_thread()

        with futures.ThreadPoolExecutor(self.input.threads) as exc:
            tasks: List[futures.Future[None]] = []
            for start, end in chunk_bytes(self.info.length, self.input.threads):
                task = exc.submit(self._download_part, (start, end))
                tasks.append(task)
            
            for task in tasks:
                task.result()
    
    def basic_download(self):
        """
        Fallback download for unknown file size.
        """
        
        response = self.client.get(self.input.url, stream=True)
        with open(self.input.file_path, 'wb') as f:
            for chunk in response.iter_content(self.input.chunk_size):
                if chunk:
                    f.write(chunk)
    
    def download(self):
        """
        Download file from the url.
        """
        if self.info.length is None:
            return self.basic_download()

        response = self.client.get(self.input.url, headers={'Range':'bytes=0-0'})
        if response.status_code == 206:
            return self.multi_thread()
        
        return self.single_thread()