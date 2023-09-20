import logging
from abc import ABC
from typing import Any

from .. import config

logging.basicConfig(level=config.LOGLEVEL)

class Enricher(ABC):
    def enrich(self, *args, **kwargs) -> Any:
        raise NotImplementedError