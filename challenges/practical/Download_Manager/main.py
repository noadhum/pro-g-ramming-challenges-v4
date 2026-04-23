import argparse

from pathlib import Path

from downloader.model import Input
from downloader.download import Downloader, HTTPClient
from downloader.utilities import random_name

def cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='OADownloadManager',
        description='A simple download manager.',
        usage=f'{__name__}.py <url> [options]',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        'url',
        type=str,
        help='URL of the file to download'
    )

    parser.add_argument(
        '-html', '--allow-html',
        action='store_true',
        help='Allow downloading HTML content'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output filename, without extension',
    )

    parser.add_argument(
        '-r', '--resume',
        action='store_true',
        help='Toggle JSON resume'
    )

    parser.add_argument(
        '--resume-path',
        type=str,
        help='JSON resume file path',
    )

    parser.add_argument(
        '-c', '--chunk-size',
        type=int,
        help='Chunk size in KB',
        default=64,
    )

    parser.add_argument(
        '-t', '--threads',
        type=int,
        help='Number of download threads',
        default=4,
    )

    parser.add_argument(
        '-ua', '--user-agent',
        type=str,
        help='User-Agent header for HTTP requests',
        default='OADownloadManager/1.0'
    )
    
    return parser.parse_args()

def main() -> None:
    args = cli()
    
    filename = args.output or random_name()
    output = Path(f'{filename}.oadm')
    resume_path = Path(args.resume_path) if args.resume_path else Path(f'{filename}_oadm.json')

    user_input = Input(
        args.url,
        args.chunk_size,
        args.threads,
        args.allow_html,
        output,
        args.resume,
        resume_path,
        args.user_agent
    )
    
    client = HTTPClient()
    info = client.probe(user_input.url)

    downloader = Downloader(user_input, client, info)
    downloader.download()

main()