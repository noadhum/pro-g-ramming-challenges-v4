import concurrent.futures as futures

from typing import Any, Dict, List

from .model import Input, FileInfo
from .resume import Resume

try:
    import requests
except ImportError:
    raise ModuleNotFoundError("Error: required 'requests' library not found, install it with: 'pip install requests'")

try:
    from tqdm import tqdm
except ImportError:
    raise ModuleNotFoundError("Error: required 'tqdm' library not found, install it with: 'pip install tqdm'")


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

class Validator:
    def __init__(self, input: Input, info: FileInfo) -> None:
        self.input = input
        self.info = info
    
    def validate(self):
        self._check_threads()
        self._check_html()

    def _check_threads(self):
        if self.input.threads < 1:
            raise ValueError('Thread must be more than 1.')
        
        if self.input.threads > 8:
            raise ValueError('Too many threads, max allowed: 8.')

    def _check_html(self):
        if not self.input.allow_html and 'text/html' in self.info.mime_type:
            raise ValueError('HTML not allowed.')

class Downloader:
    def __init__(self, input: Input, client: HTTPClient, info: FileInfo) -> None:
        self.input = input
        self.client = client
        self.info = info
        self.resume = Resume(self.input.resume_path)

        validator = Validator(self.input, self.info)
        validator.validate()

        self.progress_bar = tqdm(
            total=self.info.length,
            leave=False,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
            desc='Downloading',
            initial=(
                self.input.file_path.stat().st_size
                if self.input.file_path.exists()
                else 0
            )
        )

    def single_thread(self):
        """
        Download file using a single streaming request.
        """

        file = self.input.file_path
        existing = file.stat().st_size if file.exists() else 0
        headers = {'Range':f'bytes={existing}-'} if existing > 0 else None
        mode = 'ab' if existing > 0 else 'wb'

        response = self.client.get(self.input.url, headers=headers, stream=True)
        
        with open(file, mode) as f:
            for chunk in response.iter_content(self.input.chunk_size * 1024):
                if chunk:
                    f.write(chunk)
                    self.progress_bar.update(len(chunk))

    
    def _download_part(self, part: Dict[str, int]):
        """
        Download specific byte-range of the file
        """

        index = part['index']
        start, end = part['start'], part['end']
        downloaded = part['downloaded']
        done = part['done']

        if done:
            return
        
        resume_start = start + downloaded
        headers = {'Range': f'bytes={resume_start}-{end}'}
        response = self.client.get(self.input.url, headers=headers, stream=True)

        buffer = 0
        size = 64 * 1024

        with open(self.input.file_path, 'r+b') as f:
            f.seek(resume_start)
            for chunk in response.iter_content(self.input.chunk_size * 1024):
                if chunk:
                    f.write(chunk)
                    buffer += len(chunk)
                    self.progress_bar.update(len(chunk))
                
                if buffer >= size:
                    self.resume.update_part(index, buffer)

            if buffer > 0:
                self.resume.update_part(index, buffer)

    def multi_thread(self):
        """
        Download file using multiple threads with byte-range splitting.
        """

        if self.info.length is None:
            return self.basic_download()
        
        if not self.input.file_path.exists():
            with open(self.input.file_path, 'w+b') as f:
                f.truncate(self.info.length)
        
        self.resume.initialize(
            self.input.url,
            self.info.length,
            self.input.threads
        )

        parts = self.resume.get('parts')

        with futures.ThreadPoolExecutor(self.input.threads) as exc:
            tasks: List[futures.Future[None]] = []
            for part in parts:
                task = exc.submit(self._download_part, part)
                tasks.append(task)
            
            for task in tasks:
                task.result()
    
    def basic_download(self):
        """
        Fallback download for unknown file size.
        """
        
        response = self.client.get(self.input.url, stream=True)
        with open(self.input.file_path, 'wb') as f:
            for chunk in response.iter_content(self.input.chunk_size * 1024):
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
    
    def is_complete(self):
        self.resume.load()

        parts = self.resume.data['parts']
        if not parts:
            return
        
        return (all(part.get('done', False) for part in parts)
                and (self.input.file_path.stat().st_size == self.info.length))
    
    def cleanup(self):
        if self.is_complete():
            self.resume.delete()