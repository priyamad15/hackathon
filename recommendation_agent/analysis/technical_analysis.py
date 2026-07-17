"""
==============================================================================
technical_analysis.py

Technical Analysis Engine

Indicators:

- RSI
- SMA20
- SMA50
- MACD

Generates:
- Technical score
- Trading signal

==============================================================================

"""
import pandas as pd
from config import (
    RSI_PERIOD,
    SMA_SHORT,
    SMA_LONG,
    MACD_FAST,
    MACD_SLOW,
    MACD_SIGNAL
)


from utils.logger import logger

class TechnicalAnalysis:

    def __init__(self):

        pass

    ##########################################################################
    # RSI
    ##########################################################################

    def calculate_rsi(

        self,

        prices,

        period=RSI_PERIOD

    ):

        delta = prices.diff()
        gain = delta.where(

            delta > 0,

            0

        )
        loss = -delta.where(

            delta < 0,

            0

        )

        avg_gain = gain.rolling(

            period

        ).mean()

        avg_loss = loss.rolling(

            period

        ).mean()

        rs = avg_gain / avg_loss

        rsi = 100 - (

            100 /

            (

                1 + rs

            )

        )

        return rsi

    ##########################################################################
    # MACD
    ##########################################################################

    def calculate_macd(

        self,

        prices

    ):

        ema_fast = prices.ewm(

            span=MACD_FAST,

            adjust=False

        ).mean()

        ema_slow = prices.ewm(

            span=MACD_SLOW,

            adjust=False

        ).mean()

        macd = ema_fast - ema_slow

        signal = macd.ewm(

            span=MACD_SIGNAL,

            adjust=False

        ).mean()



        return macd, signal

    ##########################################################################
    # Complete Analysis
    ##########################################################################

    def analyze(

        self,

        history

    ):

        try:

            if history is None or history.empty:
                return self.default_result()
            close = history["close"]

            if len(close) < SMA_LONG:
                logger.warning(
                    "Insufficient history for analysis"
                )


                return self.default_result()


            ##############################################################
            # Indicators
            ##############################################################

            sma20 = close.rolling(

                SMA_SHORT

            ).mean()



            sma50 = close.rolling(

                SMA_LONG

            ).mean()

            rsi = self.calculate_rsi(

                close

            )

            macd, signal = self.calculate_macd(

                close

            )

            latest_price = close.iloc[-1]
            latest_rsi = rsi.iloc[-1]
            latest_sma20 = sma20.iloc[-1]
            latest_sma50 = sma50.iloc[-1]
            latest_macd = macd.iloc[-1]
            latest_signal = signal.iloc[-1]
            score = 50

            ##############################################################
            # RSI logic
            ##############################################################

            if latest_rsi < 30:
                score += 15

            elif latest_rsi > 70:
                score -= 15


            ##############################################################
            # Moving average trend
            ##############################################################

            if latest_sma20 > latest_sma50:
                score += 20

            else:
                score -= 10

            ##############################################################
            # MACD
            ##############################################################

            if latest_macd > latest_signal:
                score += 15
            else:
                score -= 10

            score = max(

                0,

                min(
                    100,
                    score
                )

            )

            if score >= 75:
                signal_name = "BUY"
            elif score >= 50:
                signal_name = "HOLD"
            else:
                signal_name = "SELL"

            return {
                "price":
                    round(
                        float(latest_price),2
                    ),
                    
                "rsi":
                    round(
                        float(latest_rsi),2
                    ),

                "sma20":
                    round(
                        float(latest_sma20),2
                    ),

                "sma50":
                    round(
                        float(latest_sma50),2
                    ),

                "macd":
                    round(
                        float(latest_macd),2
                    ),

                "macd_signal":
                    round(
                        float(latest_signal),2
                    ),

                "technical_score":
                    score,

                "technical_signal":
                    signal_name

            }

        except Exception as ex:
            logger.error(
                "Technical analysis failed : %s",
                ex
            )

            return self.default_result()

    ##########################################################################
    # Default Response
    ##########################################################################

    def default_result(self):


        return {

            "price": 0,
            "rsi": 0,
            "sma20": 0,
            "sma50": 0,
            "macd": 0,
            "macd_signal": 0,
            "technical_score": 50,
            "technical_signal": "HOLD"
        }