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

            # Asset Category
            "asset": "Unknown",

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
                    "History download failed %s "
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
                # Yahoo endpoints
                ##################################################################

                price = ticker.price
                quote_type = ticker.quote_type
                asset_profile = ticker.asset_profile

                ##################################################################
                # Price Information
                ##################################################################

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

                    result["exchange"] = p.get(
                        "exchangeName",
                        ""
                    )

                    result["currency"] = p.get(
                        "currency",
                        ""
                    )

                    result["current_price"] = p.get(
                        "regularMarketPrice",
                        0.0
                    )

                ##################################################################
                # Quote Type
                ##################################################################

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

                    ##################################################################
                    # Financial Asset Class
                    ##################################################################

                    asset = (
                        qt.get("quoteType")
                        or qt.get("instrumentType")
                        or "Unknown"
                    )

                    asset = str(asset).upper()

                    if asset == "EQUITY":

                        result["asset"] = "Equity"

                    elif asset == "FUTURE":

                        result["asset"] = "Commodity Future"

                    elif asset == "ETF":

                        result["asset"] = "ETF"

                    elif asset == "INDEX":

                        result["asset"] = "Index"

                    elif asset == "CURRENCY":

                        result["asset"] = "Currency"

                    elif asset == "CRYPTOCURRENCY":

                        result["asset"] = "Cryptocurrency"

                    else:

                        result["asset"] = asset.title()

                ##################################################################
                # Asset Profile
                ##################################################################

                profile = {}

                if isinstance(asset_profile, dict):
                    profile = asset_profile.get(symbol, {})

                if not isinstance(profile, dict):
                    profile = {}

                country = profile.get("country")
                sector = profile.get("sector")
                industry = profile.get("industry")
                description = profile.get("longBusinessSummary", "")

                # Asset classes that are global
                GLOBAL_ASSETS = {
                    "ETF",
                    "Index",
                    "Currency",
                    "Cryptocurrency",
                    "Commodity Future"
                }

                if result["asset"] in GLOBAL_ASSETS:
                    result["country"] = "Global"
                else:
                    result["country"] = country or "Unknown"

                result["sector"] = sector or "Unknown"
                result["industry"] = industry or "Unknown"
                result["description"] = description

                if result["asset"] == "ETF":
                    result["sector"] = result["sector"] if result["sector"] != "Unknown" else "Exchange Traded Fund"
                    result["industry"] = result["industry"] if result["industry"] != "Unknown" else "ETF"

                elif result["asset"] == "Index":
                    result["sector"] = "Market Index"
                    result["industry"] = "Stock Market Index"

                elif result["asset"] == "Currency":
                    result["sector"] = "Foreign Exchange"
                    result["industry"] = "Currency Pair"

                elif result["asset"] == "Cryptocurrency":
                    result["sector"] = "Digital Assets"
                    result["industry"] = "Cryptocurrency"

                elif result["asset"] == "Commodity Future":
                    result["sector"] = "Commodities"
                    result["industry"] = "Commodity Futures"

                ##################################################################
                # Friendly fallback
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

                logger.error(
                    "Company information failed %s : %s",
                    symbol,
                    ex
                )

                self._retry_sleep(attempt)

        logger.error(
            "Unable to fetch company information : %s",
            symbol
        )

        return self._default_company(symbol)
            

    ##########################################################################
    # Latest Quote
    ##########################################################################

    def get_quote(
        self,
        symbol: str
    ) -> Dict:
        """
        Returns latest market quote.
        """

        try:

            ticker = self._create_ticker(symbol)

            price = ticker.price

            # Uncomment only for debugging
            # print("=" * 80)
            # print("SYMBOL :", symbol)
            # print("PRICE :", price)
            # print("=" * 80)

            if not isinstance(price, dict):
                return {}

            quote = price.get(symbol, {})

            current_price = quote.get(
                "regularMarketPrice",
                0.0
            )

            previous_close = quote.get(
                "regularMarketPreviousClose",
                0.0
            )

            change_percent = 0.0

            if previous_close:
                change_percent = (
                    (current_price - previous_close)
                    / previous_close
                ) * 100

            return {

                "current_price": current_price,

                "previous_close": previous_close,

                "change_percent": change_percent,

                "open": quote.get(
                    "regularMarketOpen",
                    0.0
                ),

                "day_high": quote.get(
                    "regularMarketDayHigh",
                    0.0
                ),

                "day_low": quote.get(
                    "regularMarketDayLow",
                    0.0
                ),

                "volume": quote.get(
                    "regularMarketVolume",
                    0
                ),

                "market_cap": quote.get(
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