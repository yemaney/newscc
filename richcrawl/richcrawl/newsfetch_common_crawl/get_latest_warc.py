import gzip
import io
import logging
import os
import pathlib
import sys
import urllib.request
from datetime import datetime
import shutil
import requests

import time

from richcrawl.newsfetch_common_crawl import config

logging.basicConfig(level=os.environ.get("LOGLEVEL", "ERROR"))

COMMOM_CRAWL_BUCKET = 'commoncrawl'
COMMOM_CRAWL_CC_NEWS_PREFIX = 'crawl-data/CC-NEWS'
now = datetime.now()
CC_DATA_ROOT = f"https://data.commoncrawl.org/"
WARC_LISTING_FILE_URL = f"{CC_DATA_ROOT}{COMMOM_CRAWL_CC_NEWS_PREFIX}/{now.year}/{now.strftime('%m')}/warc.paths.gz"

class GetLatestNewsWarcArchive():
    def fetch_most_recent_file(self, common_crawl_data_dir: str) -> tuple[str, str]:
        logging.info("fetching most recent warc file from common crawl...")
        logging.info("destination folder is %s", common_crawl_data_dir)

        warc_file_partial_suffix_path = self.get_latest_warc_file_from_recent_warc_listing()
        warc_file_name = warc_file_partial_suffix_path.split('/')[-1]
        destination_file = os.path.join(common_crawl_data_dir, warc_file_name)
        pathlib.Path(destination_file).parent.mkdir(parents=True, exist_ok=True)

        if os.path.exists(destination_file):
            logging.info("warc file already exists, skipping download...")
            return warc_file_name, destination_file

        warc_file_url = CC_DATA_ROOT + warc_file_partial_suffix_path
        logging.info("downloading warc file from %s and saving to %s...", warc_file_url, destination_file)
        #urlretrieve(warc_file_url, destination_file)
        # self.download_file(warc_file_url, destination_file)

        logging.info("downloaded most recent warc file to %s", destination_file)
        return warc_file_name, destination_file

    def download_file(self, url, destination_file):
        with requests.get(url, stream=True) as r:
            with open(destination_file, 'wb') as f:
                shutil.copyfileobj(r.raw, f, length=16*1024*1024)

    def get_latest_warc_file_from_recent_warc_listing(self):
        logging.info("fetching warc listing from %s...", WARC_LISTING_FILE_URL)

        response = urllib.request.urlopen(WARC_LISTING_FILE_URL)
        compressed_file = io.BytesIO(response.read())
        decompressed_file = gzip.GzipFile(fileobj=compressed_file)
        data = decompressed_file.readlines()
        data_str = str(data[-1], "utf-8").strip()
        logging.info("latest warc file is: %s", data_str)
        return data_str

    def get_latest_warc_listing(self):
        logging.info("fetching warc listing from %s...", WARC_LISTING_FILE_URL)

        response = urllib.request.urlopen(WARC_LISTING_FILE_URL)
        compressed_file = io.BytesIO(response.read())
        decompressed_file = gzip.GzipFile(fileobj=compressed_file)
        data = decompressed_file.readlines()
        data_str = str(data[-1], "utf-8").strip()
        logging.info("latest warc file is: %s", data_str)
        return data

    def fetch_all_files(self, common_crawl_data_dir: str):
        for data in self.get_latest_warc_listing():
            warc_file_partial_suffix_path = str(data, "utf-8").strip()

            warc_file_name = warc_file_partial_suffix_path.split('/')[-1]
            destination_file = os.path.join(common_crawl_data_dir, warc_file_name)
            pathlib.Path(destination_file).parent.mkdir(parents=True, exist_ok=True)

            if os.path.exists(destination_file):
                logging.info("warc file already exists, skipping download...")
                yield warc_file_name, destination_file

            warc_file_url = CC_DATA_ROOT + warc_file_partial_suffix_path
            logging.info("downloading warc file from %s and saving to %s...", warc_file_url, destination_file)
            #urlretrieve(warc_file_url, destination_file)
            # self.download_file(warc_file_url, destination_file)

            logging.info("downloaded most recent warc file to %s", destination_file)
            yield warc_file_name, destination_file

def main():
    for warc_file_name, _ in GetLatestNewsWarcArchive().fetch_all_files(config.COMMON_CRAWL_DATA_DIR):
        yield warc_file_name


if __name__ == '__main__':
    for wf in main():
        print(wf)
    exit(0)

