from richcrawl.newsfetch_common_crawl.get_latest_warc import main
from richcrawl.newsfetch_common_crawl.warc_extractor import extract
from richcrawl.newsfetch_common_crawl.warc_extracted_files_processor import process_warc_content_dir
from richcrawl.newsfetch_enrichers.run_enrichers import  enrich

import boto3

import json


s3 = boto3.client('s3')


def richcrawl():
    i = 0
    for warc_file_name in  main():
        print(f"{warc_file_name = }")
        for raw_file in  extract(warc_file_name):
            print(f"{raw_file[0][2].keys() = }")
            for processed_file in process_warc_content_dir(raw_file):
                print(f"{processed_file.keys() = }")
                enriched_file = enrich(processed_file)
                print(f"{enriched_file.keys() = }")

                json_data = json.dumps(enriched_file)
                bucket_name = 'newsfetch-cc'
                object_key = f'{enriched_file["published_date"]}/{enriched_file["dataset_id"]}.json'
                s3.put_object(Bucket=bucket_name, Key=object_key, Body=json_data)

                i+=1
                print(f"uploaded {object_key}")
                print("#######"*10, i, "#"*10)

if __name__ == "__main__":
    richcrawl()
