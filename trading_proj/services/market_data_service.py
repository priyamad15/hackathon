"""
==============================================================================
market_data_service.py

Market Context Service

Responsibilities:

1. Load European stock universe
2. Fetch global market indices
3. Fetch commodity prices

Uses YahooService internally.

==============================================================================

"""


import pandas as pd


from services.yahoo_service import YahooService


from config import (
    MARKET_FILE,
    MARKET_INDICES,
    COMMODITIES
)


from utils.logger import logger

class MarketDataService:

    def __init__(self):

        self.yahoo = YahooService()

    ##########################################################################
    # Load European Stocks
    ##########################################################################

    def load_market_stocks(self):


        try:
            logger.info(

                "Loading European market file"

            )

            df = pd.read_csv(

                MARKET_FILE

            )
            return df


        except Exception as ex:
            logger.error(

                "Market file loading failed : %s",

                ex

            )
            
            return pd.DataFrame()

    ##########################################################################
    # Market Indices
    ##########################################################################

    def get_market_indices(self):


        output = {}

        logger.info(

            "Fetching market indices"

        )

        for name, symbol in MARKET_INDICES.items():


            try:
                quote = self.yahoo.get_quote(

                    symbol

                )

                output[name] = {


                    "symbol": symbol,


                    "price":

                        quote.get(

                            "regularMarketPrice",

                            0

                        ),


                    "change":

                        quote.get(

                            "regularMarketChangePercent",

                            0

                        )

                }

            except Exception as ex:
            
                logger.warning(
                    "Index fetch failed %s : %s",
                    name,
                    ex

                )
                output[name] = {}

        return output

    ##########################################################################
    # Commodity Prices
    ##########################################################################

    def get_commodities(self):


        output = {}

        logger.info(

            "Fetching commodities"

        )

        for name, symbol in COMMODITIES.items():
            try:
                quote = self.yahoo.get_quote(

                    symbol

                )

                output[name] = {

                    "symbol": symbol,

                    "price":

                        quote.get(

                            "regularMarketPrice",

                            0

                        ),

                    "change":

                        quote.get(

                            "regularMarketChangePercent",

                            0

                        )

                }

            except Exception as ex:
                logger.warning(

                    "Commodity fetch failed %s : %s",
                    name,
                    ex
                )
                
                output[name] = {}
        return output


    ##########################################################################
    # Complete Market Context
    ##########################################################################

    def get_market_context(self):

        return {
            "indices":
                self.get_market_indices(),

            "commodities":
                self.get_commodities()

        }