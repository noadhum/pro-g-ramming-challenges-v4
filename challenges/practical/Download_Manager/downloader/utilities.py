import random
import string

from typing import Generator, List, Optional, Tuple
from urllib.parse import urlparse, unquote

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

def resolve_filename(content: str) -> Optional[Tuple[str, str]]:
    """
    Resolve the download filename and its extension.

    Example: 'inline; filename*="cat"' -> ('cat', 'png') or ('cat', 'bin')
    
    Args:
        content: A 'Content-Disposition' header,

    Returns:
        Tuple[str, str]: A pair containing (filename, extension).
    """

    parts = _parse_disposition(content)
    if not parts:
        return
    
    for part in parts:
        for prefix in ('filename*=', 'filename='):
            if part.startswith(prefix):
                filename = part[len(prefix):].strip('"')

                if '.' not in part:
                    return filename, 'bin'
                
                filename, extension = filename.rsplit('.')
                return filename, extension
    return None

def parse_url(url: str) -> Tuple[str, str]:
    """
    Parse the file url.

    Example: 'https://example.com/cat.png' -> ('cat', 'png')

    Args:
        url: URL of a file,

    Returns:
        Tuple[str, str]: A pair containing (filename, extension)
    """

    path = urlparse(url).path
    fullname = unquote(path.rsplit('/', 1)[-1])
    if '.' not in fullname:
        return fullname, 'bin'
    
    filename, extension = fullname.rsplit('.', 1)
    return filename, extension

def parse_query(name_or_type: str) -> str:
    """
    Parse the query of a filename or MIME type.

    Example:
        'download.bin?query...' -> 'download.bin'
        'text/html; charset="utf-8";' -> 'text.html'
    
    Returns:
        str: Parsed filename or extension
    """
    
    for prefix in ('?', '#', '&', ';'):
        if prefix in name_or_type:
            extension = name_or_type.split(prefix, 1)[0]
            return extension
    return name_or_type

# -- Extension-Related --
def _possible_extensions(parts: List[str]) -> Generator[str]:
    for i, _ in enumerate(parts):
        if parts[i+1:]:
            yield '.'.join(parts[i+1:])

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

def guess_from_bytes(data: bytes) -> str:
    """
    Guess given bytes into extension.

    Example:
        b'\x89\x50\x4E\x47' -> 'png'
    """

    for extension in TYPES:
        func = FUNCTIONS.get(extension)
        if func and func(data):
            return extension
    return 'bin'

# -- Random --
def random_name(length: int = 8) -> str:
    text = string.ascii_letters + string.digits
    return (
        ''.join([
        random.choice(text)
        for _ in range(length)
        ])
    )