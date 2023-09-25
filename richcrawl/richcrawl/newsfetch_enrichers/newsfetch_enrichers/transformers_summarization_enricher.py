import logging

from transformers import pipeline

from .. import config
from ..common.datatypes import Summarization
from .transformers_enricher import TransformersEnricher


class TransformersSummarizationEnricher(TransformersEnricher):
    def __init__(self, model_name: str):
        super().__init__(model_name)
        self.summarization_pipeline = pipeline(config.TRANSFORMERS_SUMMARIZATION_PIPELINE_NAME, model=self.model_name, truncation=True)

    def enrich(self, text: str) -> Summarization:
        results = self.summarization_pipeline(text)
        for result in results:
            return result["summary_text"]

        logging.warning("No summary found for text...", )
        return result["summary_text"]


if __name__ == '__main__':
    content = "New Horizons brings Million Lords to 2.0 with a whole new user experience with new UI and art style, and narrative Expeditions, setting the mobile multiplayer strategy game up for victory in 2022\nLYON, France: 6 January, 2022 \u2014 Developer Million Victories announces the launch of the New Horizons update for mobile MMO strategy game Million Lords. Available now for iOS and Android, New Horizons introduces a new user experience that will make the game more accessible for new players, and the new Expeditions game mode to challenge veteran adventurers in the popular mobile RTS game.\nCheck out the Million Lords teaser here:\nMillion Lords is a new take on the 4X strategy game with more than 500,000 players. Million Lords brings classic strategy gameplay to mobile devices, with an unlimited number of players in a single world, allowing battles and conquest at an unprecedented scale.\nThe New Horizons update for Million Lords introduces a new UI, developed with players\u2019 feedback and built for accessibility, making the update a great jumping-on point for new players. And New Horizons also introduces updated artwork refreshing the game\u2019s look for 2022 in ways that will surprise and delight returning players.\nToday players can also embark on solo adventures for the first time in Expeditions \u2013 a brand new feature and a new way to play Million Lords. Expeditions will test players\u2019 decision-making skills as they send their heroes off on an epic journey with escalating difficulty and rewards. After every encounter, players will have the choice to flee with their loot or fight on for even greater rewards. Expeditions will offer players deeper insight into the Million Lords universe with new lore to be revealed on every adventure.\n\u201cWith New Horizons we want to welcome new players with a richer, deeper fantasy world and to give long-time players a whole new way to play,\u201d Says Benoit Ducrest, CEO and Creative Director at Million Victories. \u201cWith the new interface developed with the community\u2019s feedback in mind, it is a perfect moment to start Million Lords. When combined with the whole new way to play provided by the Expeditions, we\u2019re certain that Million Lords will continue to grow, attracting new and long-time players alike.\u201d\nSee the Million Lords New Horizons Teaser trailer here, and download the New Horizons launch screens and artwork here.\nMillion Lords is available now on iOS and Android. Download Million Lords at:\nLearn more at MillionLords.com and keep in touch via Facebook and Twitter."

    summarization_enricher = TransformersSummarizationEnricher(
        config.TRANSFORMERS_SUMMARIZATION_SSHLEIFER_DISTILBART_CNN_6_6)
    results = summarization_enricher.enrich(content)
    print(results)

    summarization_enricher = TransformersSummarizationEnricher(config.TRANSFORMERS_SUMMARIZATION_GOOGLE_PEGASUS_XSUM)
    results = summarization_enricher.enrich(content)
    print(results)
