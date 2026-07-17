"""
==============================================================================
yahoo_service.py

Yahoo Finance Service

Uses yahooquery

Features
--------
- Historical price download
- Company profile
- Quote
- In-memory cache
- Automatic retry
- Fast execution

==============================================================================

"""

import time
from typing import Dict, Optional

import pandas as pd
from yahooquery import Ticker

from config import (
    HISTORY_PERIOD,
    HISTORY_INTERVAL,
    MAX_RETRIES,
    RETRY_DELAY
)

from utils.logger import logger


class YahooService:
    """
    Wrapper around yahooquery.

    This class is intentionally lightweight because the POC
    repeatedly calls Yahoo Finance for hundreds of symbols.
    """

    ##########################################################################
    # Constructor
    ##########################################################################

    def __init__(self):

        # Cache company information
        self.company_cache: Dict[str, Dict] = {}

        # Cache history
        self.history_cache: Dict[str, pd.DataFrame] = {}

        logger.info("YahooService initialized")

    ##########################################################################
    # Internal Helper
    ##########################################################################

    def _create_ticker(
        self,
        symbol: str
    ) -> Ticker:

        return Ticker(
            symbol,
            asynchronous=False
        )

    ##########################################################################
    # Default Company Information
    ##########################################################################

    @staticmethod
    def _default_company(
        symbol: str
    ) -> Dict:

        return {

            "company_name": symbol,

            "country": "Unknown",

            "sector": "Unknown",

            "industry": "Unknown",

            "description": "",

            "currency": "",

            "exchange": "",

            "current_price": 0.0

        }

    ##########################################################################
    # Retry Wrapper
    ##########################################################################

    def _retry_sleep(
        self,
        attempt: int
    ):

        logger.warning(
            "Retry %s/%s",
            attempt + 1,
            MAX_RETRIES
        )

        time.sleep(RETRY_DELAY)

        ##########################################################################
    # Historical Price Data
    ##########################################################################

    def get_history(
        self,
        symbol: str
    ) -> Optional[pd.DataFrame]:
        """
        Download historical OHLCV data.

        Returns
        -------
        DataFrame
            Historical data with columns like:
            date, open, high, low, close, volume
        """

        ######################################################################
        # Cache
        ######################################################################

        if symbol in self.history_cache:
            return self.history_cache[symbol]

        ######################################################################
        # Retry Loop
        ######################################################################

        for attempt in range(MAX_RETRIES):

            try:

                logger.info(
                    "Downloading history : %s",
                    symbol
                )

                ticker = self._create_ticker(symbol)

                history = ticker.history(
                    period=HISTORY_PERIOD,
                    interval=HISTORY_INTERVAL
                )

                if history is None:
                    logger.warning(
                        "No history returned : %s",
                        symbol
                    )
                    return None

                ##################################################################
                # yahooquery returns MultiIndex DataFrame
                ##################################################################

                if isinstance(history, pd.DataFrame):

                    history = history.reset_index()

                    # Keep only this symbol if multiple exist
                    if "symbol" in history.columns:
                        history = history[
                            history["symbol"] == symbol
                        ]

                    history = history.sort_values(
                        by="date"
                    ).reset_index(drop=True)

                    if history.empty:
                        logger.warning(
                            "Empty history : %s",
                            symbol
                        )
                        return None

                    self.history_cache[symbol] = history

                    return history

                logger.warning(
                    "Unexpected history format : %s",
                    symbol
                )

                return None

            except Exception as ex:

                logger.warning(
                    "History download failed %s (Attempt %s/%s): %s",
                    symbol,
                    attempt + 1,
                    MAX_RETRIES,
                    ex
                )

                self._retry_sleep(attempt)

        ######################################################################
        # Failed
        ######################################################################

        logger.error(
            "Unable to download history : %s",
            symbol
        )

        return None
    
        ##########################################################################
    # Company Information
    ##########################################################################

    def get_company_information(
        self,
        symbol: str
    ) -> Dict:
        """
        Returns company metadata.

        Output example:

        {
            company_name
            country
            sector
            industry
            description
            exchange
            currency
            current_price
        }
        """

        ######################################################################
        # Cache
        ######################################################################

        if symbol in self.company_cache:
            return self.company_cache[symbol]

        result = self._default_company(symbol)

        for attempt in range(MAX_RETRIES):

            try:

                logger.info(
                    "Fetching company information : %s",
                    symbol
                )

                ticker = self._create_ticker(symbol)

                ##################################################################
                # yahooquery endpoints
                ##################################################################

                price = ticker.price
                quote_type = ticker.quote_type
                asset_profile = ticker.asset_profile

                ##############################################################
                # Price Information
                ##############################################################

                if isinstance(price, dict):

                    p = price.get(symbol, {})

                    if not isinstance(p, dict):
                        logger.warning(
                            "Unexpected price response for %s : %s",
                            symbol,
                            p
                        )
                        p = {}

                    result["company_name"] = (
                        p.get("shortName")
                        or p.get("longName")
                        or symbol
                    )

                    result["exchange"] = (
                        p.get("exchangeName", "")
                    )

                    result["currency"] = (
                        p.get("currency", "")
                    )

                    result["current_price"] = (
                        p.get("regularMarketPrice", 0.0)
                    )

                ##############################################################
                # Quote Type
                ##############################################################

                if isinstance(quote_type, dict):

                    qt = quote_type.get(symbol, {})

                    if not isinstance(qt, dict):
                        logger.warning(
                            "Unexpected quote_type response for %s : %s",
                            symbol,
                            qt
                        )
                        qt = {}

                    result["company_name"] = (
                        qt.get("longName")
                        or qt.get("shortName")
                        or result["company_name"]
                    )

                ##############################################################
                # Asset Profile
                ##############################################################

                if isinstance(asset_profile, dict):

                    profile = asset_profile.get(symbol, {})

                    if not isinstance(profile, dict):
                        logger.warning(
                            "Unexpected asset_profile response for %s : %s",
                            symbol,
                            profile
                        )
                        profile = {}

                    result["country"] = profile.get(
                        "country",
                        "Unknown"
                    )

                    result["sector"] = profile.get(
                        "sector",
                        "Unknown"
                    )

                    result["industry"] = profile.get(
                        "industry",
                        "Unknown"
                    )

                    result["description"] = (
                        profile.get(
                            "longBusinessSummary",
                            ""
                        )
                    )

                ##################################################################
                # Friendly fallback if description missing
                ##################################################################

                if not result["description"]:

                    result["description"] = (
                        f"{result['company_name']} operates in the "
                        f"{result['sector']} sector."
                    )

                ##################################################################
                # Cache
                ##################################################################

                self.company_cache[symbol] = result

                return result

            except Exception as ex:

                logger.warning(
                    "Company information failed %s "
                    "(Attempt %s/%s): %s",
                    symbol,
                    attempt + 1,
                    MAX_RETRIES,
                    ex
                )

                self._retry_sleep(attempt)

        ######################################################################
        # Failed
        ######################################################################

        logger.warning(
            "Using default company information : %s",
            symbol
        )

        return result
    
        ##########################################################################
    # Latest Quote
    ##########################################################################

    def get_quote(
        self,
        symbol: str
    ) -> Dict:
        """
        Returns latest market quote.

        Example:
            {
                current_price
                previous_close
                open
                day_high
                day_low
                volume
                market_cap
            }
        """

        try:

            ticker = self._create_ticker(symbol)

            price = ticker.price

            if not isinstance(price, dict):
                return {}

            quote = price.get(symbol, {})

            return {

                "current_price":
                    quote.get(
                        "regularMarketPrice",
                        0.0
                    ),

                "previous_close":
                    quote.get(
                        "regularMarketPreviousClose",
                        0.0
                    ),

                "open":
                    quote.get(
                        "regularMarketOpen",
                        0.0
                    ),

                "day_high":
                    quote.get(
                        "regularMarketDayHigh",
                        0.0
                    ),

                "day_low":
                    quote.get(
                        "regularMarketDayLow",
                        0.0
                    ),

                "volume":
                    quote.get(
                        "regularMarketVolume",
                        0
                    ),

                "market_cap":
                    quote.get(
                        "marketCap",
                        0
                    )

            }

        except Exception as ex:

            logger.error(
                "Quote failed %s : %s",
                symbol,
                ex
            )

            return {}

    ##########################################################################
    # Clear Cache
    ##########################################################################

    def clear_cache(self):

        self.company_cache.clear()

        self.history_cache.clear()

        logger.info("YahooService cache cleared")

    ##########################################################################
    # Cache Statistics
    ##########################################################################

    def cache_info(self) -> Dict:

        return {

            "history_cache": len(self.history_cache),

            "company_cache": len(self.company_cache)

        }

    ##########################################################################
    # Health Check
    ##########################################################################

    def ping(self) -> bool:
        """
        Simple connectivity check.
        """

        try:

            ticker = self._create_ticker("AAPL")

            _ = ticker.price

            return True

        except Exception as ex:

            logger.error(
                "Yahoo connectivity failed : %s",
                ex
            )

            return False