import concurrent.futures as futures
import threading

from typing import Any, List, Tuple

try:
    import requests
except ImportError:
    raise ModuleNotFoundError("Error: required 'requests' library not found, install it with: 'pip install requests'")

import model
import utilities

LOCK = threading.Lock()

class HTTPClient:
    def __init__(self, ua: str) -> None:
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': ua})
    
    def get(self, url: str, **kwargs: Any) -> requests.Response:
        response = self.session.get(url, **kwargs)
        response.raise_for_status()
        return response
    
    def probe(self, url: str) -> model.FileInfo:
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

        return model.FileInfo(url, length, mime_type, content_disposition, ranges)

class Downloader:
    def __init__(self, client: HTTPClient, input: model.Input, info: model.FileInfo) -> None:
        self.client = client
        self.input = input
        self.info = info

    def single_thread(self):
        response = self.client.get(self.input.url, stream=True)
        
        with open(self.input.output, 'wb') as f:
            for chunk in response.iter_content(self.input.chunk_size):
                if chunk:
                    f.write(chunk)
    
    def _download_part(self, part: Tuple[int, int]):
        pass

    def multi_thread(self):
        if self.info.length is None:
            raise ValueError("Cannot use multi-thread without 'Content-Length'.")

        with futures.ThreadPoolExecutor(self.input.threads) as exc:
            tasks: List[futures.Future[None]] = []
            for start, end in utilities.chunk_bytes(self.info.length, self.input.threads):
                task = exc.submit(self._download_part, (start, end))
                tasks.append(task)
            
            for task in tasks:
                task.result()