from .enricher import Enricher


class TransformersEnricher(Enricher):
    def __init__(self, model_name: str):
        self.model_name = model_name
