"""
==============================================================================
config.py

Central configuration for Simplified Market Recommendation POC

Architecture:
- Yahoo Finance data
- News data
- Technical analysis
- Commodity + market context
- JSON/CSV reports

==============================================================================

"""

from pathlib import Path
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

##############################################################################
# Project Paths
##############################################################################

PROJECT_ROOT = Path(__file__).resolve().parent


DATA_DIR = PROJECT_ROOT / "data"

OUTPUT_DIR = PROJECT_ROOT / "output"

LOG_DIR = PROJECT_ROOT / "logs"


# Create folders automatically

DATA_DIR.mkdir(exist_ok=True)

OUTPUT_DIR.mkdir(exist_ok=True)

LOG_DIR.mkdir(exist_ok=True)

##############################################################################
# Input Files
##############################################################################

MARKET_FILE = DATA_DIR / "european_markets.csv"


##############################################################################
# Output Files
##############################################################################

JSON_OUTPUT = OUTPUT_DIR / f"recommendations_{timestamp}.json"

CSV_OUTPUT = OUTPUT_DIR / f"recommendations_{timestamp}.csv"

##########################################################################
# News Configuration
##########################################################################

# Download news only for top-ranked stocks
MAX_NEWS_STOCKS = 20

# Number of articles per company
MAX_NEWS_PER_COMPANY = 2

# DuckDuckGo timeout
NEWS_TIMEOUT = 5


##############################################################################
# Logging
##############################################################################

LOG_FILE = LOG_DIR / "application.log"

LOG_LEVEL = "INFO"




##############################################################################
# Yahoo Finance
##############################################################################

# yahooquery settings

HISTORY_PERIOD = "3mo"

HISTORY_INTERVAL = "1d"


MAX_RETRIES = 3

RETRY_DELAY = 2


YAHOO_TIMEOUT = 20




##############################################################################
# Threading / Performance
##############################################################################

MAX_WORKERS = 10




##############################################################################
# Market Scanner
##############################################################################

TOP_STOCKS_PER_COUNTRY = 10




##############################################################################
# News
##############################################################################

NEWS_LIMIT = 10

MARKET_NEWS_LIMIT = 10

COMPANY_NEWS_LIMIT = 5




##############################################################################
# Commodities
##############################################################################

COMMODITIES = {


    "WTI_OIL":

        "CL=F",


    "BRENT_OIL":

        "BZ=F",


    "GOLD":

        "GC=F",


    "SILVER":

        "SI=F",


    "COPPER":

        "HG=F",


    "NATURAL_GAS":

        "NG=F"

}




##############################################################################
# Market Indices
##############################################################################

MARKET_INDICES = {


    "EURO_STOXX50":

        "^STOXX50E",


    "GERMANY_DAX":

        "^GDAXI",


    "FRANCE_CAC40":

        "^FCHI",


    "UK_FTSE100":

        "^FTSE",


    "US_SP500":

        "^GSPC"

}




##############################################################################
# Technical Analysis
##############################################################################

RSI_PERIOD = 14


SMA_SHORT = 20


SMA_LONG = 50


MACD_FAST = 12


MACD_SLOW = 26


MACD_SIGNAL = 9




##############################################################################
# Recommendation Scoring
##############################################################################

TECHNICAL_WEIGHT = 0.60


NEWS_WEIGHT = 0.20


MARKET_WEIGHT = 0.20



BUY_THRESHOLD = 75


HOLD_THRESHOLD = 50




##############################################################################
# Database Support
##############################################################################

DATABASE_ENABLED = True

DATABASE_TYPE = "H2"