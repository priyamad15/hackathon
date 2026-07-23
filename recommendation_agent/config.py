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
- H2 Database

==============================================================================

"""

from pathlib import Path
from datetime import datetime

##############################################################################
# Timestamp
##############################################################################

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

##############################################################################
# Project Root
##############################################################################

PROJECT_ROOT = Path(__file__).resolve().parent

##############################################################################
# Project Directories
##############################################################################

DATA_DIR = PROJECT_ROOT / "data"

OUTPUT_DIR = PROJECT_ROOT / "output"

LOG_DIR = PROJECT_ROOT / "logs"

BIN_DIR = PROJECT_ROOT / "bin"

##############################################################################
# Create folders automatically
##############################################################################

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

##############################################################################
# Logging
##############################################################################

LOG_FILE = LOG_DIR / "application.log"

LOG_LEVEL = "INFO"

##############################################################################
# Database Configuration
##############################################################################

DATABASE_ENABLED = True

DATABASE_TYPE = "H2"

DATABASE_DRIVER = "org.h2.Driver"

DATABASE_USER = "sa"

DATABASE_PASSWORD = ""

DATABASE_FILE = PROJECT_ROOT / "market_recommendation"

DATABASE_URL = (
    f"jdbc:h2:file:{DATABASE_FILE.as_posix()}"
)

H2_JAR = BIN_DIR / "h2-2.4.240.jar"

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

# Download news only for top-ranked stocks

MAX_NEWS_STOCKS = 20

# Number of articles per company

MAX_NEWS_PER_COMPANY = 2

# DuckDuckGo timeout

NEWS_TIMEOUT = 5

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
# Additional Asset Universe
##############################################################################

ETF_SYMBOLS = [
    "SPY",
    "QQQ"
]

INDEX_SYMBOLS = [
    "^GSPC",
    "^IXIC"
]

CURRENCY_SYMBOLS = [
    "EURUSD=X",
    "JPY=X"
]

CRYPTO_SYMBOLS = [
    "BTC-USD",
    "ETH-USD"
]

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
# Optional Future Settings
##############################################################################

# Maximum rows loaded into H2 at one time
DATABASE_BATCH_SIZE = 1000

# Print database connection details during startup
DATABASE_DEBUG = True

##############################################################################
# Application Metadata
##############################################################################

APPLICATION_NAME = "European Stock Recommendation Agent"

APPLICATION_VERSION = "1.0"

##############################################################################
# End of Configuration
##############################################################################