from newsfetch_core.api_schemas import Article


class TestArticle():
    def test_parse(self):
        json_string = {
            "title": "Tourists flock to Death Valley National Park to feel record 127-degree temps",
            "authors": ["John Doe", "Jane Doe"],
            "content": "The area reportedly recorded Earth's \"hottest-ever September day,\" reaching 127 degrees. But this is only the beginning.\nThe area reportedly recorded Earth's \"hottest-ever September day,\" reaching 127 degrees. But this is only the beginning.\nDEATH VALLEY, Calif. (KABC) -- Tourists flocked to Death Valley National Park Thursday to feel the heat - literally.\nThe area recorded Earth's \"hottest-ever September day,\" reaching 127 degrees. Video posted by Reuters shows visitors taking photos with the park's temperature marker.\nBut this is only the beginning.\nThe hottest temperatures are expected to peak Monday or Tuesday, meaning Thursday's record may be short-lived.\nGov. Gavin Newsom on Wednesday declared an emergency to increase energy production and relaxed rules aimed at curbing air pollution and global warming gases. He emphasized the role climate change was playing in the heat wave.\n\"All of us have been trying to outrun Mother Nature, but it's pretty clear Mother Nature has outrun us,\" Newsom said. \"The reality is we're living in an era of extremes: extreme heat, extreme drought - and with the flooding we're experiencing around the globe.\"\nNewsom's declaration followed \"Flex Alert\" calls for conservation by the California Independent System Operator, which oversees the state's electrical grid. The agency issued another Flex Alert for Friday afternoon - its third in a row.\nVIDEO: What's a Flex Alert?\nIn August 2020, a record heat wave caused a surge in power use for air conditioning that overtaxed the grid. That caused two consecutive nights of rolling blackouts, affecting hundreds of thousands of residential and business customers.\nRolling blackouts \"are a possibility but not an inevitability\" during the current heat wave, said Elliot Mainzer, president and CEO of the California Independent System Operator.\nCooling centers were being opened across the state and officials encouraged people to seek comfort at public libraries and stores - even if just for a few hours to prevent overheating.\nThe Associated Press contributed to this report.",
            "excerpt": "Tourists flocked to Death Valley National Park Thursday to feel the record-setting 127-degree temperatures as the region a feels brutal heat wave.",
            "content_length": 2071,
            "published_date": "2022-09-03T01:23:10Z",
            "url": "https://abc7.com/death-valley-hottest-september-day-2022-heat-wave-southern-california/12191728/",
            "domain": "abc7.com",
            "media": "https://cdn.abcotvs.com/dip/images/12191482_090222-kabc-4pm-death-valley-temp-record-vid.jpg?w=1600",
            "language": "en",
            "meta_info": {
                "dataset_id": "14109a15-124f-437d-9755-fef978e21eed",
                "dataset": "news-cc",
                "dataset_content_length": "237353",
                "warc_sourced_date": "2022-09-03T01:54:16Z",
                "warc_extracted_date": "2022-09-03T01:15:09Z",
                "warc_processed_date": "2022-09-03T01:48:07Z",
            }
        }
        article = Article(**json_string)
        assert article.title == "Tourists flock to Death Valley National Park to feel record 127-degree temps"
        assert article.meta_info["dataset_id"] == "14109a15-124f-437d-9755-fef978e21eed"
