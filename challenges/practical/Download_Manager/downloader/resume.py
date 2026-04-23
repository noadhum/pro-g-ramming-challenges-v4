import json
import time
import threading

from pathlib import Path
from typing import Any, Dict

from .utilities import chunk_bytes

class JSON:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.data: Dict[str, Any] = {}
        self._lock = threading.Lock()

    def create(self, data: Dict[str, Any]) -> None:
        """
        Create a new JSON file if doesn't exist yet.
        """

        if self.path.exists():
            raise FileExistsError('File is already created.')
        
        self.data = data
        self.save()
    
    def load(self) -> None:
        """
        Load data from existing file into memory
        """

        if not self.path.exists():
            raise FileNotFoundError('File not found, try create() instead.')
        
        with open(self.path, 'r') as f:
            self.data = json.load(f)

    def save(self) -> None:
        """
        Save current data to file.
        """

        tmp = self.path.with_suffix('.tmp')
        with open(tmp, 'w') as f:
            json.dump(self.data, f, indent=4)

        tmp.replace(self.path)
    def delete(self) -> None:
        """
        Delete JSON file.
        """

        if not self.path.exists():
            raise FileNotFoundError("File doesn't exist.")
        
        self.path.unlink()
        self.data = {}
    
    def set(self, attr: str, val: Any) -> None:
        self.data[attr] = val
    
    def get(self, attr: str) -> Any:
        return self.data.get(attr)

class Resume(JSON):
    def __init__(self, path: Path) -> None:
        self._last_save = time.time()
        self._interval = 1.0

        super().__init__(path)

    def initialize(self, url: str, length: int, threads: int):
        data: Dict[str, Any] = {
            'data': {
                'url': url,
                'length': length,
                'threads': threads,
            },
            'parts': []
        }

        for index, (start, end) in enumerate(chunk_bytes(length, threads)):
            data['parts'].append(
                {
                    'index': index,
                    'start': start,
                    'end': end,
                    'downloaded': 0,
                    'done': False
                }
            )  

        if not self.path.exists():
            self.create(data)
        else:
            self.load()
            if self.data['data']['url'] != url:
                raise ValueError('Resume file url mismatch.')
    
    def _in_cooldown(self) -> bool:
        now = time.time()
        return (now - self._last_save >= self._interval)
    
    def update_part(self, index: int, buffer: int):
        with self._lock:
            part = self.data['parts'][index]
            total = part['end'] - part['start'] + 1
            part['downloaded'] = min(part['downloaded'] + buffer, total)

            if part['downloaded'] >= (part['end'] - part['start'] + 1):
                part['done'] = True
            
            if not self._in_cooldown():
                self._last_save = time.time()
                self.save()