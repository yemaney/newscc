import argparse
import json
import logging
import os.path
import time
from datetime import datetime
from glob import glob

from richcrawl.newsfetch_enrichers import config
from richcrawl.newsfetch_enrichers.common import util
from richcrawl.newsfetch_enrichers.common.datatypes import EnrichmentInput
from richcrawl.newsfetch_enrichers.newsfetch_enrichers.enricher_model_factory import EnricherModelFactory
from richcrawl.newsfetch_enrichers.newsfetch_enrichers.named_entities_aggregator import MultiModelNamedEntitiesAggregator

logging.basicConfig(level=config.LOGLEVEL)

factory = EnricherModelFactory()


def enrich_function_caller(clazz, method_name: str, *args, **kwargs):
    if hasattr(clazz, method_name) and callable(func := getattr(clazz, method_name)):
        return func(*args, **kwargs)


def list_files(root_dir: str, pattern: str):
    path_pattern = os.path.join(root_dir, pattern)
    files = glob(path_pattern, recursive=True)
    return files


def enrich_ner_agg(ner1: str, ner2: str, root_dir: str, target_dir: str):
    with(open(ner1)) as f1, open(ner2) as f2:
        enrichments1 = json.load(f1)
        enrichments2 = json.load(f2)
        multi_model_aggregator = MultiModelNamedEntitiesAggregator()
        enrichment_aggregates = multi_model_aggregator.aggregate([enrichments1, enrichments2])

        out_dir = os.path.join(root_dir, target_dir)
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, os.path.basename(ner1))
        with open(out_file, "w") as f:
            json.dump(enrichment_aggregates.json(), f)
    return out_file


def build_enrichment_input(enricher, model_source, model_name, category, target_languages):
    enrichment_input = EnrichmentInput(enricher_clazz=enricher)
    enrichment_input.model_source = model_source
    enrichment_input.model_name = model_name
    enrichment_input.category = category
    if target_languages:
        enrichment_input.target_languages = target_languages
    return enrichment_input


def build_enrichers(file_name, enrichment_inputs_metadata) -> list[tuple[EnrichmentInput, str]]:
    enrichers = []
    for metadata in enrichment_inputs_metadata:
        target_languages = metadata["target_languages"] if "target_languages" in metadata else None
        enrichment_input = build_enrichment_input(enricher=metadata["enricher"],
                                                  model_source=metadata["model_source"],
                                                  model_name=metadata["model_name"],
                                                  category=metadata["category"],
                                                  target_languages=target_languages)
        enrichers.append((enrichment_input, file_name))

    return enrichers


def enrich_content(enricher: tuple[EnrichmentInput, str], article_json):
    enrichment_input, file_name = enricher
    logging.info(f'enriching: {file_name} with {enrichment_input.model_name}:{enrichment_input.model_source}...')

    processed_content = article_json
    logging.info(f'enriching content for: {processed_content["url"]}...')

    text = processed_content["content"]

    detected_language = processed_content["language"]
    if detected_language not in enrichment_input.target_languages:
        logging.warning(
            f"{detected_language} language in content is not in the target list: {enrichment_input.target_languages}")
        return

    enrichments = enrich_function_caller(enrichment_input.enricher_clazz, enrichment_input.enrich_method_name, text)
    if enrichments:
        enrichment_response = {} # util.build_enrichment_payload(processed_content, enrichment_input)
        try:
            # enrichment_response.update(enrichments.dict())
            enrichment_response = enrichments
        except Exception:
            logging.info(f"enrichments results {enrichments} was not a dict! check JSON output!!")
            # enrichment_response.update(enrichments)
        return enrichment_response




def create_enrichers(enrichment_inputs_metadata):
    for metadata in enrichment_inputs_metadata:
        enricher_clazz = factory.get_enricher(metadata["model_source"], metadata["model_name"], metadata["category"])
        metadata["enricher"] = enricher_clazz

    return enrichment_inputs_metadata


def enrich_data(article_json, enrichment_inputs_metadata):
    n = len(enrichment_inputs_metadata)

    new = {}

    file_name = article_json["meta_info"]["dataset_id"]
    enrichers = build_enrichers(file_name, enrichment_inputs_metadata)
    for enricher in enrichers:
        try:
            logging.info(f"enriching {file_name} with {enricher[0].model_name}...")
            enrichment_response = enrich_content(enricher, article_json)
            new[CATEGORY_TO_OUTPUT[enricher[0].category]] = enrichment_response
        
        except Exception as e:
            logging.error(f"error enriching file: {file_name} with {enricher[0].model_name}:{enricher[0].model_source} "
                            f"due to: {e}")

    if len(new) == n:
        result = {**article_json, **new}
        d = datetime.strptime(result["published_date"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")


        result["published_date"] = d
        result["dataset_id"] = result["meta_info"]["dataset_id"]
        result.pop("meta_info")
        result["authors"] = ", ".join(result["authors"])
        result["entities"] = ", ".join(result["entities"])
        result["keywords"] = ", ".join(result["keywords"])
        result["sentiment_score"] = result["sentiment"]["sentiment_score"]
        result["sentiment"] = result["sentiment"]["sentiment"]
        return result


CATEGORY_TO_OUTPUT = {
    config.NER : "entities",
    config.SUMMARIZATION : "summary",
    config.KEYBERT_ALL_MINI_LM_L6_V2 : "keywords",
    config.ZERO_SHOT_CLASSIFICATION : "topic",
    "sentiment" : "sentiment"
}

def enrich(processed_file_gen):
    enrichment_inputs_metadata = [
        {
            "model_source": config.SPACY,
            "model_name": config.SPACY_NER_EN_CORE_WEB_MD,
            "category": config.NER
        },
        {
            "model_source": config.TRANSFORMERS,
            "model_name": config.TRANSFORMERS_SUMMARIZATION_SSHLEIFER_DISTILBART_CNN_6_6,
            "category": config.SUMMARIZATION
        },
        {
            "model_source": config.TRANSFORMERS,
            "model_name": config.KEYBERT_ALL_MINI_LM_L6_V2,
            "category": config.KEYBERT_ALL_MINI_LM_L6_V2
        },
        {
            "model_source": config.TRANSFORMERS,
            "model_name": config.TRANSFORMERS_CLASSIFICATION_VALHALLA_DISTILBART_MNLI_12_1,
            "category": config.ZERO_SHOT_CLASSIFICATION
        },
        {
            "model_source": config.TRANSFORMERS,
            "model_name": "sentiment",
            "category": "sentiment"
        }
    ]

    all_metadatas = []
    all_metadatas.extend(enrichment_inputs_metadata)

    enrichment_inputs_metadata = create_enrichers(all_metadatas)

    return enrich_data(processed_file_gen, enrichment_inputs_metadata=enrichment_inputs_metadata)
