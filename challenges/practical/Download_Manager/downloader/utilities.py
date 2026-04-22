import random
import string

from typing import Generator, List, Optional, Tuple
from urllib.parse import urlparse, unquote

from .file_type import split_query_fragment, TYPE_TO_EXTENSION

# -- Chunking --
def chunk_bytes(length: int, threads: int) -> Generator[Tuple[int, int]]:
    size = (length + threads - 1) // threads
    for start in range(0, length, size):
        yield start, min(start + size - 1, length - 1)

# -- Parsing --
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

    Example: 'https://site.com/cat.png' -> ('cat', 'png')

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

def guess_extension(type: str) -> Tuple[str, str]:
    """
    Guess file extension from its mime type.

    Example:
        'text/html' -> ('download', 'html')
        In the example, 'download' is a placeholder for a filename

    Returns:
        Tuple[str, str]: A pair containing (filename, extension)
    """

    mime_type = split_query_fragment(type)
    return (
        'download',
        TYPE_TO_EXTENSION.get(mime_type,
        TYPE_TO_EXTENSION['application/octet-stream'])[0]
    )

# -- Random --
def random_name(length: int = 8) -> str:
    text = string.ascii_letters + string.digits
    return (
        ''.join([
        random.choice(text)
        for _ in range(length)
        ])
    )