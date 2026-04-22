from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass(slots=True)
class Input:
    url: str
    threads: int
    chunk_size: int
    output: Path
    user_agent: str

@dataclass(slots=True)
class Result:
    url: str
    output: str
    length: Optional[int]

@dataclass(slots=True)
class FileInfo:
    url: str
    length: Optional[int]
    mime_type: str
    content: Optional[str]
    ranges: Optional[str]