"""
==============================================================================
main.py

European Stock Recommendation Agent

Data Sources
------------
1. Yahoo Finance (yahooquery)
2. DuckDuckGo News

No LLM
No API Keys

Outputs
-------
output/
    recommendations_{timestamp}.json
    recommendations_{timestamp}.csv
    H2 database tables recommendations_{timestamp}

==============================================================================

"""

import traceback

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from config import DATABASE_ENABLED
from database.db_loader import DatabaseLoader

from config import (

    MAX_WORKERS,

    MAX_NEWS_STOCKS

)

from utils.logger import logger

from services.yahoo_service import YahooService
from services.news_service import NewsService
from services.market_data_service import MarketDataService

from analysis.technical_analysis import TechnicalAnalysis
from analysis.recommendation_engine import RecommendationEngine

from reports.report_generator import ReportGenerator


##############################################################################
# Helper
##############################################################################

def fetch_history(
    yahoo,
    symbol
):

    return (

        symbol,

        yahoo.get_history(symbol)

    )


def fetch_company_info(
    yahoo,
    symbol
):

    return (

        symbol,

        yahoo.get_company_information(symbol)

    )


##############################################################################
# Main
##############################################################################

def main():

    logger.info("=" * 80)
    logger.info("European Stock Recommendation Agent Started")
    logger.info("=" * 80)

    try:

        ######################################################################
        # Initialize Services
        ######################################################################

        yahoo = YahooService()

        news_service = NewsService()

        market_service = MarketDataService()

        technical = TechnicalAnalysis()

        recommendation_engine = RecommendationEngine()

        report_generator = ReportGenerator()

        ######################################################################
        # Load Stocks
        ######################################################################

        logger.info(
            "Loading stock universe..."
        )

        market_df = market_service.load_market_stocks()

        if market_df.empty:

            logger.error(
                "No stocks available."
            )

            return

        symbols = (

            market_df["symbol"]

            .dropna()

            .unique()

            .tolist()

        )

        logger.info(

            "Stocks Loaded : %s",

            len(symbols)

        )

        ######################################################################
        # Market Context
        ######################################################################

        logger.info(

            "Loading Market Context..."

        )

        market_context = (

            market_service.get_market_context()

        )

        ######################################################################
        # Containers
        ######################################################################

        history_data = {}

        company_information = {}

        recommendations = []

        company_news = {}

        commodity_recommendations = []

        country_summary = {}

        logger.info(
            "Initialization completed."
        )

        ######################################################################
        # Download Historical Data
        ######################################################################

        with ThreadPoolExecutor(
            max_workers=MAX_WORKERS
        ) as executor:

            futures = {

                executor.submit(
                    fetch_history,
                    yahoo,
                    symbol
                ): symbol

                for symbol in symbols

            }

            for future in as_completed(futures):

                symbol = futures[future]

                try:

                    _, history = future.result()

                    history_data[symbol] = history

                except Exception as ex:

                    logger.warning(

                        "History unavailable for %s : %s",

                        symbol,

                        ex

                    )

                    history_data[symbol] = None

        logger.info(

            "Historical data downloaded for %s stocks",

            len(history_data)

        )

        ######################################################################
        # Download Company Information
        ######################################################################

        logger.info(

            "Downloading company information..."

        )

        with ThreadPoolExecutor(
            max_workers=MAX_WORKERS
        ) as executor:

            futures = {

                executor.submit(
                    fetch_company_info,
                    yahoo,
                    symbol
                ): symbol

                for symbol in symbols

            }

            for future in as_completed(futures):

                symbol = futures[future]

                try:

                    _, info = future.result()

                    company_information[symbol] = info or {}

                except Exception as ex:

                    logger.warning(

                        "Company information unavailable for %s : %s",

                        symbol,

                        ex

                    )

                    company_information[symbol] = {}

        logger.info(

            "Company information downloaded."

        )

        ######################################################################
        # Commodity Recommendations
        ######################################################################

        logger.info(

            "Generating commodity recommendations..."

        )

        try:

            commodity_recommendations = (

                recommendation_engine.commodity_recommendations(

                    market_context

                )

            )

        except Exception as ex:

            logger.warning(

                "Commodity recommendation failed : %s",

                ex

            )

            commodity_recommendations = []

        logger.info(

            "Commodity recommendations generated."

        )

        ######################################################################
        # IMPORTANT
        #
        # Company news is NOT downloaded here.
        #
        # News will be downloaded ONLY for the final Top Ranked stocks.
        # This reduces DuckDuckGo requests dramatically.
        ######################################################################

        company_news = {}

        ######################################################################
        # Analyse Stocks
        ######################################################################

        logger.info(

            "Analysing stocks..."

        )

      
        initial_results = []

        for symbol in symbols:

            try:

                history = history_data.get(symbol)

                if history is None:
                    continue

                ##############################################################
                # Technical Analysis
                ##############################################################

                technical_result = technical.analyze(history)

                ##############################################################
                # Company Information
                ##############################################################

                company_info = company_information.get(
                    symbol,
                    {}
                )

                ##############################################################
                # Initial Recommendation
                # (No news yet)
                ##############################################################

                result = recommendation_engine.generate(

                    technical_result,

                    company_info,

                    [],

                    market_context

                )

                ##############################################################
                # Save everything for second pass
                ##############################################################

                initial_results.append(

                    {

                        "symbol": symbol,

                        "technical_result": technical_result,

                        "company_info": company_info,

                        "initial_result": result

                    }

                )

            except Exception as ex:

                logger.exception(

                    "Failed processing %s : %s",

                    symbol,

                    ex

                )

        ######################################################################
        # Rank by Initial Score
        ######################################################################

        initial_results = sorted(

            initial_results,

            key=lambda x:

                x["initial_result"].get(
                    "final_score",
                    0
                ),

            reverse=True

        )

        ######################################################################
        # Download News ONLY for Top Stocks
        ######################################################################

        top_symbols = [

            x["symbol"]

            for x in initial_results[:MAX_NEWS_STOCKS]

        ]

        logger.info(

            "Downloading news for Top %s stocks...",

            len(top_symbols)

        )

        company_news = news_service.get_multiple_company_news(
            top_symbols
        )

        logger.info(

            "News downloaded."

        )

        recommendations = []

        for item in initial_results:

            symbol = item["symbol"]

            technical_result = item["technical_result"]

            company_info = item["company_info"]

            news = company_news.get(
                symbol,
                []
            )

            ##############################################################
            # Only Top Stocks have news.
            # Others receive an empty list.
            ##############################################################

            final_result = recommendation_engine.generate(

                technical_result,

                company_info,

                news,

                market_context

            )

            recommendation = final_result.get(
                "recommendation",
                "SELL"
            )

            ##############################################################
            # Ignore HOLD
            ##############################################################

            if recommendation == "HOLD":
                continue

            recommendations.append(

                {

                    "symbol": symbol,

                    "company_name":
                        company_info.get(
                            "company_name"
                        ) or symbol,

                    "country":
                        company_info.get(
                            "country"
                        ) or "Unknown",

                    "sector":
                        company_info.get(
                            "sector"
                        ) or "Unknown",

                    "industry":
                        company_info.get(
                            "industry"
                        ) or "Unknown",

                    "description":
                        company_info.get(
                            "description"
                        ) or "",

                    "price":
                        round(
                            float(
                                technical_result.get(
                                    "price",
                                    0
                                ) or 0
                            ),
                            2
                        ),

                    "recommendation":
                        recommendation,

                    "risk":
                        final_result.get(
                            "risk_level",
                            "Medium"
                        ),

                    "score":
                        round(
                            float(
                                final_result.get(
                                    "final_score",
                                    0
                                ) or 0
                            ),
                            2
                        ),

                    "reason":
                        final_result.get(
                            "reason",
                            ""
                        ),

                    "latest_news":
                        news

                }

            )

        ######################################################################
        # Final Sort
        ######################################################################

        recommendations = sorted(

            recommendations,

            key=lambda x: x["score"],

            reverse=True

        )

        ######################################################################
        # Country Summary
        ######################################################################

        country_summary = {}

        for country in sorted(

            {

                x["country"]

                for x in recommendations

            }

        ):

            stocks = [

                x

                for x in recommendations

                if x["country"] == country

            ]

            country_summary[country] = {

                "strong_buy":

                    [

                        x

                        for x in stocks

                        if x["recommendation"] == "STRONG BUY"

                    ][:2],

                "buy":

                    [

                        x

                        for x in stocks

                        if x["recommendation"] == "BUY"

                    ][:2],

                "sell":

                    [

                        x

                        for x in stocks

                        if x["recommendation"] == "SELL"

                    ][:2],

                "strong_sell":

                    [

                        x

                        for x in stocks

                        if x["recommendation"] == "STRONG SELL"

                    ][:2]

            }

        ######################################################################
        # Reports
        ######################################################################

        report_generator.generate_report(

            recommendations,

            market_context,

            country_summary,

            commodity_recommendations

        )

        loader = None

        try:
            if DATABASE_ENABLED:
                loader = DatabaseLoader()
                loader.load_csv(report_generator.csv_output_file)

        finally:
            if loader is not None:
                loader.close()

        ######################################################################
        # Console Summary
        ######################################################################

        logger.info("=" * 80)

        logger.info(

            "Market Scan Completed Successfully"

        )

        logger.info(

            "Stocks Analysed : %s",

            len(symbols)

        )

        logger.info(

            "Recommendations : %s",

            len(recommendations)

        )

        logger.info(

            "Countries : %s",

            len(country_summary)

        )

        logger.info(

            "Commodity Recommendations : %s",

            len(commodity_recommendations)

        )

        logger.info("=" * 80)

    except Exception as ex:

        logger.exception(

            "Application failed : %s",

            ex

        )

        traceback.print_exc()


##############################################################################
# Entry Point
##############################################################################

if __name__ == "__main__":

    main()
