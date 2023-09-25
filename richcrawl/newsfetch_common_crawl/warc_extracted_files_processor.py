import argparse
import concurrent.futures
import json
import logging
import os
import datetime
import time

from richcrawl.newsfetch_core.common import util
from richcrawl.newsfetch_newsplease.newplease_adapter import NewsPleaseHtmlAdapter
from . import config

logging.basicConfig(level=os.environ.get("LOGLEVEL", "ERROR"))

# add list of sites to skip
stop_sites = []

def process_warc_content_dir(extract_data):
    # logging.debug(f'processing warc content dir: {warc_extract_dir}...')
    futures = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for result in extract_data:
            domain, file_name, data = result
            content_processor_wrapper = ContentProcessorWrapper(data)
            futures.append(executor.submit(content_processor_wrapper.process_warc_content))
            break
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        if result is not None:
            if result["language"] == "en":
                yield result



class ContentProcessorWrapper():
    def __init__(self, data):
        self.data = data

    def process_warc_content(self):
        try:
            warc_extract = self.data
            uri = warc_extract["uri"]
            logging.debug(f'extracting content for: {uri}...')

            domain = warc_extract["domain"]
            dataset_id = warc_extract["dataset_id"]
            article_html = warc_extract["article_html"]

            if domain in stop_sites:
                logging.warning(f'WARNING: did not extract content for: {uri}... domain in stop list')
                return

            article = NewsPleaseHtmlAdapter(article_html, uri).get_article()

            meta_info = {
                "dataset_id": dataset_id,
                "dataset": warc_extract["dataset"],
                "dataset_content_length": warc_extract["dataset_content_length"],
                "warc_sourced_date": warc_extract["warc_sourced_date"],
                "warc_extracted_date": warc_extract["warc_extracted_date"],
                "warc_processed_date": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
            }

            article_json = article.dict()
            if article_json["published_date"]:
                article_json["published_date"] = article_json["published_date"].strftime('%Y-%m-%dT%H:%M:%SZ')

            article_json["meta_info"] = meta_info

            file_name = dataset_id + config.JSON_OUT_FILE_EXT
            # util.write_json_to_file([self.root_dir, config.PROCESSED_CONTENT_DIR, domain], file_name, data=article_json)
            print("Process: ", file_name)
            return article_json
        except Exception as e:
            # print(f'exception occurred processing warc file: {file_name} -> {e}')
            return None


