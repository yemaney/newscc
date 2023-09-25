import concurrent.futures
import logging
import os
import datetime
import time
import argparse

from warcio import ArchiveIterator
from urllib.parse import urlparse

from richcrawl.newsfetch_core.common import constants, util

from . import config

logging.basicConfig(level=os.environ.get("LOGLEVEL", "ERROR"))

class CommonCrawlWarcExtractor:
    def process(self, warc_file_path, limit=False):
        warc_file_name = util.get_warc_file_name(warc_file_path)
        try:
            os.makedirs(warc_file_name, exist_ok=True)
            logging.debug(f"created {warc_file_name} directory!")
        except OSError as error:
            logging.error(f"could not create {warc_file_name} directory!")
            exit(1)

        num_processed = 0
        with open(warc_file_path, 'rb') as stream:
            futures = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for record in ArchiveIterator(stream):
                    if num_processed >= 1:
                        break
                    if record.rec_type == 'request':
                        continue

                    if record.rec_type == 'response':
                        warc_record_id = record.rec_headers.get_header('WARC-Record-ID')
                        warc_target_uri = record.rec_headers.get_header('WARC-Target-URI')
                        warc_date = record.rec_headers.get_header('WARC-Date')
                        warc_content_length = record.rec_headers.get_header('Content-Length')

                        if not warc_target_uri or int(warc_content_length) <= 0:
                            logging.warning(
                                f'WARNING: did not extract content for: {warc_target_uri}... no warc_target_uri, or warc_content_length is 0')
                            return

                        domain = urlparse(warc_target_uri).netloc

                        logging.info(f'extracting content for: {warc_target_uri}...')

                        article_html = record.content_stream().read()

                        record_processor_wrapper = RecordProcessorWrapper(warc_file_name, warc_record_id,
                                                                          warc_target_uri,
                                                                          warc_content_length, warc_date,
                                                                          domain, article_html)
                        num_processed = num_processed + 1
                        futures.append(executor.submit(record_processor_wrapper.process))

            i = 0
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result[0] is not None:
                    i+=1
                    yield result, i

class RecordProcessorWrapper():
    def __init__(self, warc_file_name, warc_record_id,
                 warc_target_uri, warc_content_length,
                 warc_date, domain, article_html):
        self.warc_file_name = warc_file_name
        self.warc_record_id = warc_record_id
        self.warc_target_uri = warc_target_uri
        self.warc_content_length = warc_content_length
        self.warc_date = warc_date
        self.domain = domain
        self.article_html = article_html

    def process(self):
        try:
            dataset_id = self.warc_record_id.split(":")[-1].split(">")[0]
            data = {
                "dataset_id": dataset_id,
                "dataset": constants.DATASET_NEWS_CC,
                "dataset_content_length": self.warc_content_length,
                "uri": self.warc_target_uri,
                "warc_sourced_date": self.warc_date,
                "warc_extracted_date": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
                "domain": self.domain,
                "article_html": self.article_html.decode("utf-8", "ignore")
            }

            file_name = dataset_id + config.JSON_OUT_FILE_EXT
            # util.write_json_to_file([self.warc_file_name, config.WARC_EXTRACT_DIR, self.domain], file_name, data=data)
            # print(self.warc_file_name, config.WARC_EXTRACT_DIR, self.domain, file_name)
            return self.domain, file_name, data
        except Exception as e:
            logging.error('An exception occurred: {}'.format(e))
            return None, None, None

def extract(warc_file_name: str):
    file_path = os.path.join(f"{config.COMMON_CRAWL_DATA_DIR}/{warc_file_name}")
    logging.info(f"processing warc file: {file_path}...")
    common_crawl_warc_extractor = CommonCrawlWarcExtractor()
    gen = common_crawl_warc_extractor.process(file_path, limit=False)
    return gen