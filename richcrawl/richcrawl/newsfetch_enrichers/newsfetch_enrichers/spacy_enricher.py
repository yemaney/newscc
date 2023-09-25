import spacy

from .. import config
from .enricher import Enricher


class SpacyEnricher(Enricher):
    def __init__(self, model_name: str = config.SPACY_NER_EN_CORE_WEB_MD):
        self.model_name = model_name
        self.nlp = spacy.load(model_name)
