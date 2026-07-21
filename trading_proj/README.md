# European Stock Recommendation Agent

A modular Python application that analyzes European stocks using **technical indicators**, **company fundamentals**, and **market news** to generate investment recommendations. The application retrieves historical market data from Yahoo Finance, ranks stocks using a weighted scoring model, enriches top-ranked stocks with recent news, and exports the results to **CSV**, **JSON**, and an **H2 database**.

```text
Stock Universe
      │
      ▼
Historical Data + Company Information
      │
      ▼
Technical Analysis (RSI, SMA, MACD)
      │
      ▼
Initial Scoring & Ranking
      │
      ▼
Top-N News Enrichment (DuckDuckGo)
      │
      ▼
Final Recommendation Engine
      │
      ├── CSV Report
      ├── JSON Report
      └── H2 Database
```

## Technical Indicators

* **RSI (Relative Strength Index):** Measures price momentum to identify overbought (>70) and oversold (<30) conditions, helping detect potential trend reversals.
* **SMA (Simple Moving Average):** Uses 20-day and 50-day moving averages to identify short- and medium-term market trends. A bullish crossover (SMA20 > SMA50) indicates upward momentum.
* **MACD (Moving Average Convergence Divergence):** Compares short- and long-term exponential moving averages to identify trend strength and potential buy/sell signals through MACD and Signal line crossovers.

## Key Features

* Concurrent retrieval of historical prices and company fundamentals.
* Technical analysis using RSI, SMA(20/50), and MACD indicators.
* News enrichment for top-ranked stocks to optimize external requests.
* Rule-based recommendation engine with confidence scoring and risk assessment.
* Automatic generation of CSV/JSON reports and H2 database tables.
* Modular architecture for easy extension with additional indicators, data sources, or databases.

## Tech Stack

**Python • YahooQuery • DuckDuckGo (DDGS) • Pandas • H2 Database • JayDeBeApi • ThreadPoolExecutor**

## Run

```bash
pip install -r requirements.txt
python main.py
```
