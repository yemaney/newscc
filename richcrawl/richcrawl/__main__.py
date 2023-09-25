import json

import boto3

from richcrawl.newsfetch_common_crawl.get_latest_warc import main
from richcrawl.newsfetch_common_crawl.warc_extractor import extract
from richcrawl.newsfetch_common_crawl.warc_extracted_files_processor import process_warc_content_dir
from richcrawl.newsfetch_enrichers.run_enrichers import  enrich



s3 = boto3.client('s3')


def richcrawl():
    for warc_file_name in  main():
        print(warc_file_name)
        raw_file_extract_gen =  extract(warc_file_name)
        processed_file_gen = process_warc_content_dir(raw_file_extract_gen)
        enriched_file_gen = enrich(processed_file_gen)
        for file in enriched_file_gen:
            json_data = json.dumps(file)
            bucket_name = 'newsfetch-cc'
            object_key = f'{file["published_date"]}/{file["dataset_id"]}.json'
            s3.put_object(Bucket=bucket_name, Key=object_key, Body=json_data)


if __name__ == "__main__":
    richcrawl()