"""Asset retrieval functions"""
import re
import secrets
from os.path import basename, join
import tempfile
from urllib.parse import urlparse
import iscc_sdk as idk
import requests
from constance import config
from ninja.errors import HttpError
from iscc_generator.models import Media
from iscc_generator.storage import clean_filename, store_local_temp


def download_media(media_obj: Media):
    # type: (Media) -> str
    """
    Download Media file to temporary local storage.

    :param Media media_obj: Media object
    :return: local filepath
    """
    filename = basename(media_obj.source_file.name)
    with media_obj.source_file.open("rb") as infile:
        tmpfile_path = store_local_temp(infile, filename)
    return tmpfile_path


def download_url(url):
    # type: (str) -> str
    """
    Download file from url to temporary local storage

    :param str url: Url for file download
    :return: local filepath
    """
    headers = {"user-agent": f"ISCC/{idk.__version__} +http://iscc.codes"}
    stream = requests.get(
        url,
        headers=headers,
        stream=True,
        verify=config.DOWNLOAD_VERIFY_TLS,
        timeout=config.DOWNLOAD_TIMEOUT,
    )

    # Check file size
    size = stream.headers.get("content-length")
    if size:
        size = int(size)
        limit = config.DOWNLOAD_SIZE_LIMIT * 1000000
        if size and size > limit:
            raise HttpError(400, message=f"Download of {size} for {url} exceeds {limit} limit")

    # Get filename
    filename = None
    codi = stream.headers.get("content-disposition")
    if codi:
        try:
            filename = re.findall("filename=(.+)", codi)[0]
        except IndexError:
            pass
    if not filename:
        url_obj = urlparse(url)
        filename = basename(url_obj.path or url_obj.netloc)
    if not filename:
        filename = secrets.token_hex(64)
    filename = clean_filename(filename)

    # Stream to local temp storage
    tempdir = tempfile.mkdtemp()
    tmpfile_path = join(tempdir, filename)
    with open(tmpfile_path, "wb") as tmpfile:
        chunk_size = 1024 * 1024
        for chunk in stream.iter_content(chunk_size):
            tmpfile.write(chunk)
    return tmpfile_path
