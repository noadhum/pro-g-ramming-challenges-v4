import json

from pathlib import Path
from typing import Any, Dict

from .utilities import chunk_bytes

class JSON:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.data: Dict[str, Any] = {}

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
        
        with open(self.path, 'w') as f:
            json.dump(self.data, f, indent=4)

    def delete(self) -> None:
        """
        Delete JSON file.
        """

        if not self.path.exists():
            raise FileNotFoundError("File doesn't exist.")
        
        self.path.unlink()
        self.data = {}

class Resume(JSON):
    def __init__(self, path: Path) -> None:
        super().__init__(path)

    def initialize(self, url: str, length: int, threads: int):
        data: Dict[str, Any] = {
            'url': url,
            'length': length,
            'parts': []
        }

        for index, (start, end) in enumerate(chunk_bytes(length, threads)):
            data['parts'].append(
                {
                    'index': index,
                    'start': start,
                    'end': end,
                    'downloaded': 0,
                }
            )  

        self.create(data)
