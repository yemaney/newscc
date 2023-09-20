from pprint import pprint
from richcrawl.newsfetch_common_crawl.get_latest_warc import main
from richcrawl.newsfetch_common_crawl.warc_extractor import extract
from richcrawl.newsfetch_common_crawl.warc_extracted_files_processor import process_warc_content_dir
from richcrawl.newsfetch_enrichers.run_enrichers import  enrich


def richcrawl():
    warc_file_name = main()
    raw_file_extract_gen =  extract(warc_file_name)
    processed_file_gen = process_warc_content_dir(raw_file_extract_gen)
    for i in enrich(processed_file_gen):
        pprint(i)
        print("\n")
        pprint(i.keys())
        break



if __name__ == "__main__":
    richcrawl()