# TODO: refactor this file bcuz its ugly

from collections import defaultdict
from typing import Callable, Dict, DefaultDict, List, Generator

EXTENSION_TO_TYPE: Dict[str, List[str]] = {
    # -- Audio --
    'aac': ['audio/aac', 'audio/x-aac'],
    'flac': ['audio/flac'],
    'm4a': ['audio/mp4'],
    'mp3': ['audio/mpeg'],
    'ogg': ['audio/ogg'],
    'wav': ['audio/wav'],

    # -- Application/Document --
    'docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
    'pptx': ['application/vnd.openxmlformats-officedocument.presentationml.presentation'],
    'xlsx': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
    'doc': ['application/msword'],
    'ppt': ['application/vnd.ms-powerpoint'],
    'xls': ['application/vnd.ms-excel'],
    'pdf': ['application/pdf'],
    'pyc': ['application/x-python-code'],
    'pyo': ['application/x-python-code'],

    # -- Font --
    'otf': ['font/otf'],
    'ttf': ['font/ttf'],
    'woff': ['font/woff'],
    'woff2': ['font/woff2'],

    # -- Image --
    'avif': ['image/avif'],
    'bmp': ['image/bmp'],
    'gif': ['image/gif'],
    'heic': ['image/heic'],
    'ico': ['image/x-icon', 'image/vnd.microsoft.icon'],
    'jpg': ['image/jpeg'],
    'png': ['image/png'],
    'tif': ['image/tiff'],
    'tiff': ['image/tiff'],
    'webp': ['image/webp'],

    # -- Package --
    '7z': ['application/x-7z-compressed'],
    'bz2': ['application/x-bzip2'],
    'deb': ['application/x-debian-package', 'application/x-deb'],
    'dmg': ['application/x-apple-diskimage'],
    'gz': ['application/gzip'],
    'rar': ['application/x-rar-compressed', 'application/vnd.rar'],
    'rpm': ['application/x-rpm'],
    'tar': ['application/x-tar'],
    'xz': ['application/x-xz'],
    'zip': ['application/zip'],

    # -- Text/Script --
    'css': ['text/css'],
    'csv': ['text/csv'],
    'htm': ['text/html'],
    'html': ['text/html'],
    'idml': ['application/xml'],
    'js': ['text/javascript', 'application/javascript'],
    'json': ['application/json'],
    'lua': ['text/x-lua'],
    'map': ['text/javascript'],
    'md': ['text/markdown'],
    'markdown': ['text/markdown'],
    'mjs': ['text/javascript'],
    'py': ['text/x-python'],
    'tsv': ['text/tab-separated-values'],
    'txt': ['text/plain'],
    'xml': ['application/xml'],
    'xmp': ['application/xml'],
    'yaml': ['application/x-yaml', 'text/yaml', 'application/yaml'],

    # -- Video --
    'm4v': ['video/mp4', 'video/x-m4v'],
    'mp4': ['video/mp4'],
    'mpg': ['video/mpeg'],
    'ogv': ['video/ogg'],
    'qt': ['video/quicktime'],
    'webm': ['video/webm'],

    # -- Other --
    'bin': ['application/octet-stream'],
    'dll': ['application/x-msdownload'],
    'exe': ['application/x-msdownload'],
}

TYPE_TO_EXTENSION: DefaultDict[str, List[str]] = defaultdict(list)

for key, value in EXTENSION_TO_TYPE.items():
    for filetype in value:
        TYPE_TO_EXTENSION[filetype].append(key)

TYPE_FUNCTIONS: Dict[str, Callable[[bytes], bool]] = {}

MAX_RANGE = 65536 # 64kb

# -- Main --
def sniff_bytes(data: bytes) -> str:
    """
    Sniff the given data and return an extension.
    """
    for ext in EXTENSION_TO_TYPE:
        func = TYPE_FUNCTIONS.get(ext)
        if func and func(data):
            return ext
    return 'bin'

def to_type(filename_or_extension: str) -> List[str]:
    """
    Convert filename or extension into possible MIME Types.
    """
    
    file_parts = split_query_fragment(filename_or_extension).lower().split('.')

    if len(file_parts) <= 1:
        return EXTENSION_TO_TYPE.get(file_parts[0], EXTENSION_TO_TYPE['bin'])

    for extension in _possible_extensions(file_parts):
        if extension in EXTENSION_TO_TYPE:
            return EXTENSION_TO_TYPE[extension]
    return EXTENSION_TO_TYPE['bin']

def to_extension(content_type: str) -> List[str]:
    """
    Convert Content-Type into possible extensions.
    """

    file_type = split_query_fragment(content_type).lower().strip()
    return TYPE_TO_EXTENSION.get(file_type, TYPE_TO_EXTENSION['application/octet-stream'])

def valid_ext(filename_or_extension: str) -> bool:
    """
    Check if given extension is valid.
    """
    
    extension = split_query_fragment(filename_or_extension).split('.')[-1]
    return extension in EXTENSION_TO_TYPE

def valid_type(ftype: str) -> bool:
    """
    Check if given Content/Media Type is valid.
    """
    
    return ftype in TYPE_TO_EXTENSION

# -- Helper --
def split_query_fragment(filename_or_extension_or_type: str) -> str:
    
    for prefix in ('?', '#', '&', ';'):
        if prefix in filename_or_extension_or_type:
            extension = filename_or_extension_or_type.split(prefix, 1)[0]
            return extension
    return filename_or_extension_or_type

def _possible_extensions(parts: List[str]) -> Generator[str]:
    for i, _ in enumerate(parts):
        if parts[i+1:]:
            yield '.'.join(parts[i+1:])

# -- Decorator --
def add_filetype(ext: str):
    def wrapper(func: Callable[[bytes], bool]) -> Callable[[bytes], bool]:
        TYPE_FUNCTIONS[ext.lower()] = func
        return func
    return wrapper

# -- Functions --
# - Audio -
@add_filetype('aac')
def is_aac(data: bytes) -> bool:
    """
    Check if given bytes represents a AAC file.
    """
    return (len(data) >= 2 and (data[0:2] in (b'\xFF\xF1', b'\xFF\xF9')))

@add_filetype('flac')
def is_flac(data: bytes) -> bool:
    """
    Check if given bytes represents a FLAC file.
    """
    return (len(data) >= 4
            and (data[0:4] == b'\x66\x4C\x61\x43'))

@add_filetype('m4a')
def is_m4a(data: bytes) -> bool:
    """
    Check if given bytes represents a M4A file.
    """
    return (len(data) >= 11 and (data[0:4] == b'\x4D\x34\x41\x20'
            or data[4:11] == b'\x66\x74\x79\x70\x4D\x34\x41'))

@add_filetype('mp3')
def is_mp3(data: bytes) -> bool:
    """
    Check if given bytes represents a MP3 file.
    """
    if len(data) >= 3:
        if data[0:3] == b'\x49\x44\x33':
            return True
        
        if data[1] in (0xE2, 0xE3, 0xF2, 0xF3, 0xFA, 0xFB):
            return True
    return False

@add_filetype('ogg')
def is_ogg(data: bytes) -> bool:
    """
    Check if given bytes represents a OGG file.
    """
    return (len(data) >= 4
            and data[0:4] == b'\x4F\x67\x67\x53'
            and data[4:8] != b'\x00\x02\x00\x00')

@add_filetype('wav')
def is_wav(data: bytes) -> bool:
    """
    Check if given bytes represents a WAV file.
    """
    return (len(data) >= 12 and (data[0:4] == b'\x52\x49\x46\x46' and data[8:12] == b'\x57\x41\x56\x45'))

# - Application/Document -
@add_filetype('docx')
def is_docx(data: bytes) -> bool:
    """
    Check if given bytes represents a DOCX file.
    """
    if len(data) >= MAX_RANGE and is_zip(data):
        return b'word/' in data
    return False

@add_filetype('pptx')
def is_pptx(data: bytes) -> bool:
    """
    Check if given bytes represents a PPTX file.
    """
    if len(data) >= MAX_RANGE and is_zip(data):
        return b'ppt/' in data
    return False

@add_filetype('xlsx')
def is_xlsx(data: bytes) -> bool:
    """
    Check if given bytes represents a XLSX file.
    """
    if len(data) >= MAX_RANGE and is_zip(data):
        return b'xl/' in data
    return False

@add_filetype('doc')
def is_doc(data: bytes) -> bool:
    """
    Check if given bytes represents a DOC file.
    """
    if len(data) >= 516 and data[0:8] == b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1':
        if data[512:516] ==  b'\xEC\xA5\xC1\x00':
            return True
        
        if len(data) > 2142 and (
            b'\x00\x0A\x00\x00\x00\x4D\x53\x57\x6F\x72\x64\x44\x6F\x63\x00\x10\x00\x00\x00\x57\x6F\x72\x64\x2E\x44\x6F\x63\x75\x6D\x65\x6E\x74\x2E\x38\x00\xF4\x39\xB2\x71'
            in data[2075:2142]
            or b'\x57\x00\x6F\x00\x72\x00\x64\x00\x44\x00\x6F\x00\x63\x00\x75\x00\x6D\x00\x65\x00\x6E\x00\x74\x00'
            in data[1408:1432]):
            return True
        
        if b'Document' in data:
            return True

    return False

@add_filetype('ppt')
def is_ppt(data: bytes) -> bool:
    """
    Check if given bytes represents a PPT file.
    """
    if len(data) >= 2096 and data[0:8] == b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1':
        if data[512:516] == b'\xA0\x46\x1D\xF0':
            return True

        if data[512:516] == b'\x00\x6E\x1E\xF0':
            return True
        
        if data[512:516] == b'\x0F\x00\xE8\x03':
            return True

        if data[2072:2096] == b'\x00\xB9\x29\xE8\x11\x00\x00\x00\x4D\x53\x20\x50\x6F\x77\x65\x72\x50\x6F\x69\x6E\x74\x20\x39\x37':
            return True
        
        if (b'PowerPoint' in data[:MAX_RANGE]
            or b'PowerPoint' in data[MAX_RANGE:]):
            return True

    return False

@add_filetype('xls')
def is_xls(data: bytes) -> bool:
    """
    Check if given bytes represents a XLS file.
    """
    if len(data) >= 2095 and data[0:8] == b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1':
        if data[512:516] == b'\xFD\xFF\xFF\xFF' and (data[518] == 0 or data[518] == 2):
            return True
        
        if data[512:520] == b'\x09\x08\x10\x00\x00\x06\x05\x00':
            return True
        
        if b'\xE2\x00\x00\x00\x5C\x00\x70\x00\x04\x00\x00Calc' in data[1568:2095]:
            return True
        
        if (b'Workbook' in data
            or b'Book' in data):
            return True
        
    return False

@add_filetype('pdf')
def is_pdf(data: bytes) -> bool:
    """
    Check if given bytes represents a PDF file.
    """
    return (len(data) >= 4 and (data[0:4] == b'\x25\x50\x44\x46'))

# - Font
@add_filetype('otf')
def is_otf(data: bytes) -> bool:
    """
    Check if given bytes represents an OTF file..
    """
    return (len(data) >= 5 and data[0:5] == b'\x4F\x54\x54\x4F\x00')

@add_filetype('ttf')
def is_ttf(data: bytes) -> bool:
    """
    Check if given bytes represents a TTF file.
    """
    return (len(data) >= 5 and (
        data[0:5] in (b'\x00\x01\x00\x00\x00', b'\x74\x72\x75\x65\x00')))

@add_filetype('woff')
def is_woff(data: bytes) -> bool:
    """
    Check if given bytes represents a WOFF file.
    """
    return (len(data) >= 4 and data[0:4] == b'\x77\x4F\x46\x46')

@add_filetype('woff2')
def is_woff2(data: bytes) -> bool:
    """
    Check if given bytes represents a WOFF2 file.
    """
    return (len(data) >= 4 and data[0:4] == b'\x77\x4F\x46\x32')

# - Image -
@add_filetype('avif')
def is_avif(data: bytes) -> bool:
    """
    Check if given bytes represents a AVIF file.
    """
    return (len(data) >= 12 and data[4:12] == b'\x66\x74\x79\x70\x61\x76\x69\x66')

@add_filetype('bmp')
def is_bmp(data: bytes) -> bool:
    """
    Check if given bytes represents a BMP file.
    """
    return (len(data) >= 2 and data[0:2] == b'\x42\x4D')

@add_filetype('gif')
def is_gif(data: bytes) -> bool:
    """
    Check if given bytes represents a GIF file.
    """
    return (len(data) >= 3 and data[0:3] == b'\x47\x49\x46')

@add_filetype('heic')
def is_heic(data: bytes) -> bool:
    """
    Check if given bytes represents a HEIC file.
    """
    return (len(data) >= 12 and data[4:12] == b'\x66\x74\x79\x70\x68\x65\x69\x63')

@add_filetype('ico')
def is_ico(data: bytes) -> bool:
    """
    Check if given bytes represents an ICO file.
    """
    return (len(data) >= 4 and data[0:4] == b'\x00\x00\x01\x00')

@add_filetype('jpg')
def is_jpg(data: bytes) -> bool:
    """
    Check if given bytes represents a JPG file.
    """
    return (len(data) >= 3 and data[0:3] == b'\xFF\xD8\xFF')

@add_filetype('png')
def is_png(data: bytes) -> bool:
    """
    Check if given bytes represents a PNG file.
    """
    return (len(data) >= 4 and data[0:4] == b'\x89\x50\x4E\x47')

@add_filetype('tiff')
def is_tiff(data: bytes) -> bool:
    """
    Check if given bytes represents a TIF/TIFF file.
    """
    if len(data) >= 4:
        if data[0:4] in (b'MM*\x00', b'MM\x00*', b'MM\x00+', b'II*\x00'):
            return True
    return False

@add_filetype('webp')
def is_webp(data: bytes) -> bool:
    """
    Check if given bytes represents a WEBP file.
    """
    return (len(data) >= 12 and (data[0:4] ==  b'\x52\x49\x46\x46' and data[8:12] == b'\x57\x45\x42\x50'))

# - Package -
@add_filetype('7z')
def is_7z(data: bytes) -> bool:
    """
    Check if given bytes represents a 7Z file.
    """
    return (len(data) >= 6 and data[0:6] == b'\x37\x7A\xBC\xAF\x27\x1C')

@add_filetype('bz2')
def is_bz2(data: bytes) -> bool:
    """
    Check if given bytes represents a BZ2 file.
    """
    return (len(data) >= 3 and data[0:3] == b'\x42\x5A\x68')

@add_filetype('deb')
def is_deb(data: bytes) -> bool:
    """
    Check if given bytes represents a DEB file.
    """
    return (len(data) >= 21
            and data[0:21] == b'\x21\x3C\x61\x72\x63\x68\x3E\x0A\x64\x65\x62\x69\x61\x6E\x2D\x62\x69\x6E\x61\x72\x79')

@add_filetype('dmg')
def is_dmg(data: bytes) -> bool:
    """
    Check if given bytes represents a DMG file.
    """
    return (len(data) >= 4 and data[0:4] == b'\x6B\x6F\x6C\x79')

@add_filetype('gz')
def is_gz(data: bytes) -> bool:
    """
    Check if given bytes represents a GZ file.
    """
    return (len(data) >= 3 and data[0:3] == b'\x1F\x8B\x08')

@add_filetype('rar')
def is_rar(data: bytes) -> bool:
    """
    Check if given bytes represents a RAR file.
    """
    return (len(data) >= 7
            and (data[0:7] in (b'\x52\x61\x72\x21\x1A\x07\x00', b'\x52\x61\x72\x21\x1A\x07\x01')))

@add_filetype('rpm')
def is_rpm(data: bytes) -> bool:
    """
    Check if given bytes represents a RPM file.
    """
    return (len(data) >= 4 and data[0:4] == b'\xED\xAB\xEE\xDB')

@add_filetype('tar')
def is_tar(data: bytes) -> bool:
    """
    Check if given bytes represents a TAR file.
    """
    return (len(data) >= 262 and data[257:262] == b'\x75\x73\x74\x61\x72')

@add_filetype('xz')
def is_xz(data: bytes) -> bool:
    """
    Check if given bytes represents a XZ file.
    """
    return (len(data) >= 6 and data[0:6] == b'\xFD\x37\x7A\x58\x5A\x00')

@add_filetype('zip')
def is_zip(data: bytes) -> bool:
    """
    Check if given bytes represents a ZIP file.
    """
    return (len(data) >= 4 and (data[0:4] in (b'\x50\x4B\x03\x04', b'\x50\x4B\x05\x06', b'\x50\x4B\x07\x08')))

# - Text/Script -
@add_filetype('html')
def is_html(data: bytes) -> bool:
    """
    Check if given bytes represent an HTML file.

    Not 100% accurate
    """
    return (b'<htm' in data.lower()
            or b'<?doctype' in data.lower()
            )

@add_filetype('xml')
def is_xml(data: bytes) -> bool:
    """
    Check if given bytes represents a XML file.
    """
    return (len(data) >= 100
            and (data.lstrip().startswith(b'\x3C\x3F\x78\x6D\x6C')))

# - Video -
@add_filetype('m4v')
def is_m4v(data: bytes) -> bool:
    """
    Check if given bytes represents a M4V file.
    """
    return (len(data) >= 11
            and (b'ftypM4V' in data[4:11]))

@add_filetype('mp4')
def is_mp4(data: bytes) -> bool:
    """
    Check if given bytes represents a MP4 file.
    """
    return (len(data) >= 12
            and (data[4:8] == b'\x66\x74\x79\x70')
            and data[8:12]
            in (b'mp41', b'mp42', b'isom', b'iso2', b'avc1'))

@add_filetype('mpg')
def is_mpg(data: bytes) -> bool:
    """
    Check if given bytes represents a MPG file.
    """
    return (len(data) >= 4 and (data[0:4] in (b'\x00\x00\x01\xBA', b'\x00\x00\x01\xB3')))

@add_filetype('ogv')
def is_ogv(data: bytes) -> bool:
    """
    Check if given bytes represents an OGV file.
    """
    return (len(data) >= 8 and data[0:8] == b'\x4F\x67\x67\x53\x00\x02\x00\x00')

@add_filetype('qt')
def is_qt(data: bytes) -> bool:
    """
    Check if given bytes represents a QT file.
    """
    return (len(data) >= 9 and (data[4:9] in (b'\x6D\x6F\x6F\x76\x00', b'\x6D\x64\x61\x74\x00')))

@add_filetype('webm')
def is_webm(data: bytes) -> bool:
    """
    Check if given bytes represents a WEBM file.
    """
    return (len(data) >= 4 and data[0:4] == b'\x1A\x45\xDF\xA3')
