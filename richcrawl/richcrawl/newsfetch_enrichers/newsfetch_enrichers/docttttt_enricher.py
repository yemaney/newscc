import logging

from transformers import T5Tokenizer, T5ForConditionalGeneration
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline

import config
from common.datatypes import QuestionAndContext, GeneratedQuestions
from newsfetch_enrichers.enricher import Enricher

class DocT5Enricher(Enricher):
    def __init__(self, model_name: str = config.TRANSFORMERS_DOC2QUERY_T5_BASE_MSMACRO):
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)

    def enrich(self, context: str) -> GeneratedQuestions:

        input_ids = self.tokenizer.encode(context, return_tensors='pt')
        outputs = self.model.generate(
            input_ids=input_ids,
            max_length=64,
            do_sample=True,
            top_p=0.95,
            num_return_sequences=5)

        logging.info("Text being analyzed: %s", context)
        logging.debug("Generating questions...")

        questions_and_contexts = [] # type: list[QuestionAndContext]
        for i in range(len(outputs)):
            question = self.tokenizer.decode(outputs[i], skip_special_tokens=True)
            questions_and_contexts.append(QuestionAndContext(question=question, context=context))

        return GeneratedQuestions(questions_and_contexts=questions_and_contexts)

if __name__ == "__main__":
    docs = [
        "The futures were higher on Wednesday, after a risk-on rally that finally held its ground. After a brutal start to the year for the Nasdaq and the Russell 2000, both indexes closed Tuesday higher but still are lurking just below the down 20% bear market status. All the major indexes and the transports soared higher, as both oil and gold once again plunged, and there was selling across the Treasury curve as the five-year and 10-year notes and the 30-year bond closed at 52-week high yields.\nThe collapse in oil pricing is perhaps the best news for Americans, as prices at the pump had in some locations risen to the highest levels ever. Brent crude closed at $98.85 a barrel, down well over 7%, while West Texas Intermediate ended the day down a stunning 8% to $94.57. While it will take some time to flow through to the retail level, drivers should see things start to improve in April.\n24/7 Wall St. reviews dozens of analyst research reports each day of the week with a goal of finding fresh ideas for investors and traders alike. Some of these daily analyst calls cover stocks to buy. Other calls cover stocks to sell or avoid. Remember that no single analyst call should ever be used as a basis to buy or sell a stock. Consensus analyst target data is from Refinitiv.\nThese are the top analyst upgrades, downgrades and initiations seen on Wednesday, March 16, 2022.\nAPA Corp. (NASDAQ: APA): Goldman Sachs raised the price target on shares of the energy giant to $46.50 from $36 while keeping a Neutral rating. The consensus target is $41.98. The stock closed Tuesday at $36.70.\nArcher Daniels Midland Inc. (NYSE: ADM): Goldman Sachs raised its $79 target price to $91 while maintaining a Buy rating. The consensus target is $73.85. The last trade on Tuesday came in at $82.79.\nBigCommerce Holdings Inc. (NASDAQ: BIGC): Berenberg initiated coverage with a Hold rating and a $21 target price. The consensus target is $35.67. The final trade on Tuesday was reported at $17.72.\nBioventus Inc. (NASDAQ: BVS): Craig Hallum started coverage with a Buy rating and a $30 price target. The consensus is much lower at $19. The stock closed on Tuesday at $13.45, up over 6% for the day.\nCompass Therapeutics Inc. (NASDAQ: CMPX): Ladenburg Thalmann started coverage with a Buy rating and a $7 target. The consensus is higher at $9.43. The stock closed almost 7% higher on Tuesday at $1.54.\nCoupa Software Inc. (NASDAQ: COUP): Piper Sandler downgraded the stock to Neutral from Overweight and slashed the $230 target price to $70. For now, the consensus target is $193.57. The shares closed Tuesday at $72.55, down almost 20% after announcing disappointing guidance.",
        "Ukraine and Russian negotiators have reportedly made progress in settlement talks that could end Putin\u2019s war. The Financial Times reported Wednesday morning that Russian Foreign Minister Sergei Lavrov said that \u201c\u2018absolutely specific wordings\u2019 were \u2018close to being agreed'\u201d between the two sides. The agreement includes \u201csecurity guarantees for Moscow and neutrality for Kyiv.\u201d\nIn its report on the settlement talks, CNBC cites Lavrov\u2019s comments in a televised interview for Russian television:\nIn the talks between Russia and Ukraine, there is some hope of reaching a compromise. \u2026 The neutral status of Ukraine is now being seriously discussed in the negotiations in conjunction with other security issues. There are already specific formulations that are close to being agreed upon.\nLavrov then added that the Russian invasion (which Putin and other Russian leaders insist on calling a special military operation) was \u201cnot so much about Ukraine, but about the world order\u201c: \u201cThe United States under Biden subjugated Europe, and the current crisis is an epochal moment in defining the world order.\u201d\nUkraine President Volodymyr Zelensky said in a radio broadcast that the negotiations were beginning to \u201csound more realistic\u201d:\nAll wars end in agreements . . . As I am told, the positions in the negotiations sound more realistic. However, time is still needed for the decisions to be in Ukraine\u2019s interests. Our heroes, our defenders give us this time defending Ukraine everywhere.\nAt 9:00 a.m. ET, Zelensky will deliver a virtual address to the U.S. Congress. Senate Majority Leader Chuck Schumer and House Speaker Nancy Pelosi said in a letter to Senators and Representatives that Congress is committed \u201cto supporting Ukraine as they face Putin\u2019s cruel and diabolical aggression, and to passing legislation to cripple and isolate the Russian economy as well as deliver humanitarian, security and economic assistance to Ukraine.\u201d\nRussia would be in default on its sovereign debt if it pays the coupon on its U.S. dollar-denominated Eurobond debt in rubles when the 30-day grace period expires on April 2, according to a commentary by Fitch Ratings. On March 8, Fitch downgraded Russia\u2019s sovereign debt from B to C, signifying that a default was imminent based on Russian President Vladimir Putin\u2019s decree of March 5 establishing \u201ca differential treatment of external debt payments to creditors in countries that had joined sanctions against Russia, including their payment in roubles.\u201d\nU.S. premarket trading was solidly in the green Wednesday morning as hopes rise for a settlement between Russia and Ukraine. Perhaps an even more upbeat note, however, was sounded by China\u2019s central bank governor, Yi Gang, essentially guaranteed stability in capital markets, support for overseas stock listings, a fix for the floundering real estate market and an end to the persecution of the country\u2019s high-tech giants. J.P. Morgan downgraded 28 Chinese tech stocks on Tuesday, calling them \u201cuninvestable\u201d for the next six to 12 months.\nAnd where does China fit in? In an Opinion article at Bloomberg News, Shuli Ren writes:",
        "Weapons have become an important part of the discussion about world order. The Russian attack on Ukraine has triggered shipments of hundreds of millions of dollars of weapons to the battered country. These have come from a wide range of nations, including the United States and many NATO members. Notably, these weapons have been given and not sold. And they have been very effective as the Ukraine military attacks the Russian invaders.\nAmong the effects of what has become a war is that many countries will buy weapons to replace those given to Ukraine. As the \u201carsenal of democracy,\u201d the United States provides most of these, for a fee. The United States is the world\u2019s leading arms exporter, shipping almost $9.4 billion in arms to nearly 100 different countries around the globe in 2020 alone. In recent years, 22 countries have spent over $1 billion purchasing weapons from the United States.\nTo determine the country buying the most weapons from the U.S. government, 24/7 Wall St. reviewed data from the Stockholm International Peace Research Institute\u2019s Arms Transfers Database on the value of arms exports from the United States to other countries.\nSince 2010, U.S. arms manufacturers have shipped over $105 billion worth of arms around the world. These shipments have gone to strategic allies in Asia, the Middle East, Europe and elsewhere. The United States is, of course, not the only arms supplier. Many of the countries on this list also purchase significant amounts of arms from Russia, China and other nations.\nThough the United States has by far the world\u2019s largest military budget of any nation, it does not have the largest military in the world when it comes to personnel. In fact, the United States ranks fifth, after four other countries with at least 1 million armed services personnel.\nThe country the United States sells the most arms to is Saudi Arabia. Here are the details:\nArms imports from the United States, 2010 to 2020: $17.61 billion\nU.S. arms imports as share of total, 2010 to 2020: 64.8%\nLargest arms suppliers, 2016 to 2020: United States, United Kingdom, France\nNational military expenditure in 2020: $57.52 billion (8.4% of gross domestic product)\nIn determining the country buying the most weapons from the U.S. government, countries were ranked based on the total value of arms exports received from the United States from 2010 to 2020. Arms data covers actual deliveries of major conventional weapons. Supplemental data on arms imports from the United States as a share of a country\u2019s total arms imports was calculated using data from the Stockholm International Peace Research Institute. Data on the largest arms suppliers by total value from 2016 to 2020, as well as national military expenditure in 2020 and national military expenditure as a percentage of gross domestic product in 2020, also came from the Stockholm International Peace Research Institute.\nClick here to see all the countries buying the most weapons from America.",
        "Fame can be a double-edged sword for those in the entertainment world. The attention, the glamor, and the adulation are great, but the pressure of staying on top is enormous. And it weighs even more heavily on child actors, who get saddled with descriptions like \u201cprodigy\u201d and \u201cprecocious\u201d when they turn in a spellbinding performance. A breakout role for child actors has been a blessing for some, a curse for others.\nTo compile a list of more than 50 of the best child actor performances of all time, 24/7 Tempo gathered information from IMDb, an online movie database owned by Amazon, as well as various entertainment industry media sources.\nSome of the breakout roles for child actors can be considered harrowing, such as the possessed girl played by Linda Blair in \u201cThe Exorcist\u201d and Heather O\u2019Rourke\u2019s character who is tormented by malevolent spirits in the Poltergeist movies. Isabelle Fuhrman\u2019s performance as a sociopathic girl in \u201cOrphan\u201d was so disturbing, one critic wasn\u2019t sure she would ever get another role.\nSome young actors performed convincingly in themes about the effects of dislocation caused by war, such as Brigitte Fossey and Georges Poujouly in \u201cForbidden Games,\u201d Edmund Moeschke in \u201cGermany Year Zero,\u201d and Nikolay Spiridonov in \u201cCome and See.\u201d\nA great performance as a child actor doesn\u2019t mean a long career, such as those enjoyed by Drew Barrymore or Christina Ricci. Actors such as Moeschke and John Howard Davies had a brief movie career and either disappeared or they switched to film production. Others resumed their film pursuits later in life. Fossey chose to focus on school, and Indian actor Subir Banerjee went 57 years between film credits before appearing in the movie \u201cAchal: The Stagnant\u201d in 2012.\nClick here to see amazing child actor performances of the last 100 years\nCritically acclaimed performances by child actors have been an indicator of Oscar-winning roles to come for Christian Bale, Jodie Foster, and Natalie Portman. For Anna Paquin, her screen debut in \u201cThe Piano\u201d at age 11 earned her a Best Supporting Actress Oscar, making her the second-youngest actress to win a competitive Academy Award (Tatum O\u2019Neal at 10 years old was the youngest). (These actors won an Oscar before the age of 30.)\nWe can only speculate about the careers of Heather O\u2019Rourke and River Phoenix, actors who distinguished themselves in their formative years and died too soon. (These are 20 movie and TV stars who died far too young.)",
    ]

    enricher = DocT5Enricher()
    for doc in docs:
        generated_questions = enricher.enrich(context=doc)
        for question_and_context in generated_questions.questions_and_contexts:
            logging.info(f"Generated question was: {question_and_context.question}")
