import random
import string

from typing import Generator, List, Optional, Tuple
from pathlib import Path
from urllib.parse import urlparse, unquote

from .model import FileInfo
from .types.data import EXTENSIONS, TYPES, FUNCTIONS

# -- Chunking --
def chunk_bytes(length: int, threads: int) -> Generator[Tuple[int, int]]:
    size = (length + threads - 1) // threads
    for start in range(0, length, size):
        yield start, min(start + size - 1, length - 1)

# -- Parse/Split --
def _parse_disposition(content: str) -> List[str]:
    """
    Parsing 'Content-Disposition' header into pieces.

    Example: inline; filename*="cat" -> ['inline', 'filename*="cat.png"']

    Args:
        content: A 'Content-Disposition' header,

    Returns:
        List[str]: A list containing parsed 'Content-Disposition' header.
    """
    buffer = ''
    result: List[str] = []
    in_quote = False

    for character in content:
        if character == '"':
            in_quote = not in_quote
        
        if character == ';' and not in_quote:
            if buffer.strip():
                result.append(buffer.strip())
            buffer = ''
        else:
            buffer += character

    if buffer.strip():
        result.append(buffer.strip())
    return result

def resolve_filename(content: str) -> str:
    """
    Resolve the download filename and its extension.

    Example: 'inline; filename*="cat.png"' -> 'png' or 'bin'
    
    Args:
        content: A 'Content-Disposition' header,

    Returns:
        Optional[str]: File extension
    """

    parts = _parse_disposition(content)
    if not parts:
        return 'bin'
    
    for part in parts:
        for prefix in ('filename*=', 'filename='):
            if part.startswith(prefix):
                filename = part[len(prefix):].strip('"')

                if '.' not in part:
                    return 'bin'
                
                extension = filename.rsplit('.')[-1]
                return extension
    return 'bin'

def parse_url(url: str) -> str:
    """
    Parse the file url.

    Example: 'https://example.com/cat.png' -> 'png'

    Args:
        url: URL of a file,

    Returns:
        str: File extension 
    """

    path = urlparse(url).path
    fullname = unquote(path.rsplit('/', 1)[-1])
    if '.' not in fullname:
        return 'bin'
    
    extension = fullname.rsplit('.', 1)[-1]
    return extension

def parse_query(name_or_type: str) -> str:
    """
    Parse the query of a filename or MIME type.

    Example:
        'download.bin?query...' -> 'download.bin'
        'text/html; charset="utf-8";' -> 'text/html'
    
    Returns:
        str: Parsed filename or extension
    """
    
    for prefix in ('?', '#', '&', ';'):
        if prefix in name_or_type:
            extension = name_or_type.split(prefix, 1)[0]
            return extension
    return name_or_type

def guess_from_metadata(info: FileInfo) -> str:
    if info.content_disposition:
        ext = resolve_filename(info.content_disposition)
        if ext != 'bin':
            return ext
        
    ext = parse_url(info.url)
    if ext != 'bin':
        return ext
    
    ext_list = guess_extension(info.mime_type)
    if ext_list:
        return ext_list[0]
    return 'bin'

# -- Extension-Related --
def guess_from_bytes(data: bytes) -> str:
    """
    Guess given bytes into extension.

    Example:
        bytes of a png file... -> 'png'
    """

    for extension in TYPES:
        func = FUNCTIONS.get(extension)
        if func and func(data):
            return extension
    return 'bin'

def guess_extension(type: str) -> List[str]:
    """
    Guess file extension from its MIME type.

    Example:
        'text/html' -> ('download', 'html')
        In the example, 'download' is a placeholder for a filename

    Returns:
        List[str]: A list containing extensions
    """

    mime_type = parse_query(type)
    return (
        EXTENSIONS.get(mime_type,
        EXTENSIONS['application/octet-stream'])
    )

def _possible_extensions(parts: List[str]) -> Generator[str]:
    for i, _ in enumerate(parts):
        if parts[i+1:]:
            yield '.'.join(parts[i+1:])

def guess_type(name_or_extension: str) -> List[str]:
    """
    Guess MIME type from its file extension.

    Example:
        'cat.png' -> 'image/png'
    
    Returns:
        List[str]: A list containing 
    """

    file_parts = parse_query(name_or_extension).lower().split('.')

    if len(file_parts) <= 1:
        return TYPES.get(file_parts[0], TYPES['bin'])

    for extension in _possible_extensions(file_parts):
        if extension in TYPES:
            return TYPES[extension]
    return TYPES['bin']

# -- Other --
def read_binary(file_path: Path, size: Optional[int] = 64 * 1024):
    with open(file_path, 'rb') as f:
        return f.read(size)

def random_name(length: int = 8) -> str:
    text = string.ascii_letters + string.digits
    return (
        ''.join([
        random.choice(text)
        for _ in range(length)
        ])
    )

def format_size(num: float) -> str:
    i = 0
    units = ['KB', 'MB', 'GB', 'TB']
    while num >= 1024 and i < len(units) - 1:
        num /= 1024
        i += 1
    return f'{num:.2f}{units[i]}'