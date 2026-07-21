"""
==============================================================================
news_service.py

News Service

Fetches:
    - Market news
    - Company specific news

Source:
    DuckDuckGo (ddgs)

No API key required.

Compatible with:
    - Current main.py
    - Current Recommendation Engine

==============================================================================

"""

from concurrent.futures import ThreadPoolExecutor, as_completed

from ddgs import DDGS

from config import (
    NEWS_LIMIT,
    COMPANY_NEWS_LIMIT,
    MARKET_NEWS_LIMIT,
    MAX_WORKERS
)

from utils.logger import logger


class NewsService:

    ##########################################################################
    # Constructor
    ##########################################################################

    def __init__(self):

        pass

    ##########################################################################
    # Generic Search
    ##########################################################################

    def _search(
        self,
        query,
        limit
    ):

        logger.info("Searching news : %s", query)

        results = []

        try:

            with DDGS(timeout=3) as ddgs:

                response = list(

                    ddgs.news(

                        keywords=query,

                        max_results=limit

                    )

                )

            for item in response:

                results.append(

                    {

                        "title": item.get("title", ""),

                        "summary": item.get("body", ""),

                        "url": item.get("url", ""),

                        "source": item.get("source", ""),

                        "published": item.get("date", "")

                    }

                )

            if not results:

                logger.info(

                    "No news found for query : %s",

                    query

                )

        except Exception as ex:

            logger.warning(

                "News search failed %s : %s",

                query,

                ex

            )

            return []

        return results

    ##########################################################################
    # Market News
    ##########################################################################

    def get_market_news(self):

        logger.info(

            "Downloading market news..."

        )

        queries = [

            "European stock market latest news",

            "European economy outlook",

            "ECB interest rates",

            "European inflation",

            "European financial markets"

        ]

        news = []

        seen_urls = set()

        for query in queries:

            articles = self._search(

                query,

                MARKET_NEWS_LIMIT

            )

            for article in articles:

                url = article.get("url", "")

                if url and url not in seen_urls:

                    news.append(article)

                    seen_urls.add(url)

            if len(news) >= NEWS_LIMIT:

                break

        logger.info(

            "Market news downloaded : %s articles",

            len(news)

        )

        return news[:NEWS_LIMIT]
    
        ##########################################################################
    # Company News
    ##########################################################################

    def get_company_news(
        self,
        symbol
    ):

        queries = [

            f"{symbol} stock latest news",

            f"{symbol} company news"

        ]

        seen_urls = set()

        articles = []

        for query in queries:

            try:

                results = self._search(

                    query,

                    COMPANY_NEWS_LIMIT

                )

                for item in results:

                    url = item.get("url", "")

                    if url and url not in seen_urls:

                        seen_urls.add(url)

                        articles.append(item)

                #
                # Stop if enough news has been collected
                #
                if len(articles) >= COMPANY_NEWS_LIMIT:

                    break

            except Exception as ex:

                logger.warning(

                    "Company news search failed %s : %s",

                    symbol,

                    ex

                )

        return articles[:COMPANY_NEWS_LIMIT]

    ##########################################################################
    # Concurrent Company News
    ##########################################################################

    def get_multiple_company_news(
        self,
        symbols
    ):

        logger.info(

            "Downloading company news for %s stocks...",

            len(symbols)

        )

        output = {}

        with ThreadPoolExecutor(
            max_workers=MAX_WORKERS
        ) as executor:

            futures = {

                executor.submit(

                    self.get_company_news,

                    symbol

                ): symbol

                for symbol in symbols

            }

            for future in as_completed(futures):

                symbol = futures[future]

                try:

                    output[symbol] = future.result()

                    logger.info(

                        "News downloaded : %s (%s articles)",

                        symbol,

                        len(output[symbol])

                    )

                except Exception as ex:

                    logger.warning(

                        "Company news failed %s : %s",

                        symbol,

                        ex

                    )

                    output[symbol] = []

        logger.info(

            "Company news download completed."

        )

        return output