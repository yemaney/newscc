import logging

from richcrawl.newsfetch_enrichers import config
from .spacy_ner_enricher import SpacyNerEnricher
from .transformers_ner_enricher import TransformersNerEnricher
from .transformers_summarization_enricher import TransformersSummarizationEnricher
from .transformers_zeroshot_classification_enricher import TransformersZeroShotClassificationEnricher
from .keyword_extraction_enricher import KeyBertKeywordExtractionEnricher
from .topic_modeling_enricher import TopicModelingEnricher
from .transformers_sentiment_classification_enricher import TransformerSentimentClassificationEnricher

class EnricherModelFactory():
    def __init__(self):
        self.enricher_models = {}

    def get_enricher(self, model_source, model_name, category):
        enricher_clazz = None
        enricher_model_key = model_source + model_name + category
        if enricher_model_key in self.enricher_models.keys():
            enricher_clazz = self.enricher_models[enricher_model_key]
        else:
            if model_source == config.SPACY and category == config.NER:
                enricher_clazz = SpacyNerEnricher(model_name)
            elif model_source == config.TRANSFORMERS and category == config.NER:
                enricher_clazz = TransformersNerEnricher(model_name)
            elif model_source == config.TRANSFORMERS and category == config.ZERO_SHOT_CLASSIFICATION:
                enricher_clazz = TransformersZeroShotClassificationEnricher(
                    model_name,
                    config.NEWS_HIGH_LEVEL_CATEGORIES2)

            elif model_source == config.TRANSFORMERS and category == config.SUMMARIZATION:
                enricher_clazz = TransformersSummarizationEnricher(model_name)
            elif model_source == config.TRANSFORMERS and category == config.KEYBERT_ALL_MINI_LM_L6_V2:
                enricher_clazz = KeyBertKeywordExtractionEnricher(model_name)

            elif model_source == config.TRANSFORMERS and category == "sentiment":
                enricher_clazz = TransformerSentimentClassificationEnricher()
            if enricher_clazz:
                self.enricher_models[enricher_model_key] = enricher_clazz
            else:
                logging.warn(f"Enricher not found for model_source: {model_source}, model_name: {model_name}, category: {category}")

        return enricher_clazz