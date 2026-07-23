"""
==============================================================================
recommendation_engine.py

Recommendation Engine

Purpose
-------
Generate simple investment recommendations using:

1. Technical score
2. Company news sentiment
3. Overall market trend
4. Commodity trend
5. Sector outlook

No LLM
No AI

==============================================================================

"""

from typing import Dict


class RecommendationEngine:

    ##########################################################################
    # Constructor
    ##########################################################################

    def __init__(self):

        pass

    ##########################################################################
    # News Sentiment Score
    ##########################################################################

    def news_score(
        self,
        news
    ):

        if not news:
            return 0

        score = 0

        positive_words = [

            "growth",
            "profit",
            "upgrade",
            "strong",
            "beat",
            "expansion",
            "record",
            "increase",
            "surge",
            "acquisition",
            "bullish"

        ]

        negative_words = [

            "loss",
            "downgrade",
            "lawsuit",
            "decline",
            "fall",
            "weak",
            "investigation",
            "bankruptcy",
            "bearish",
            "drop"

        ]

        for article in news:

            text = (

                article.get("title", "") +

                " " +

                article.get("body", "")

            ).lower()

            for word in positive_words:
                if word in text:
                    score += 3

            for word in negative_words:
                if word in text:
                    score -= 3

        return score

    ##########################################################################
    # Sector Score
    ##########################################################################

    def sector_score(
        self,
        sector
    ):

        sector = (sector or "").lower()

        mapping = {

            "technology": 12,

            "healthcare": 10,

            "financial services": 6,

            "industrials": 5,

            "consumer defensive": 8,

            "consumer cyclical": 3,

            "utilities": 6,

            "energy": 7,

            "basic materials": 4,

            "communication services": 5,

            "real estate": 2

        }

        return mapping.get(
            sector,
            0
        )
    
    ##########################################################################
    # Market Score
    ##########################################################################

    def market_score(
        self,
        market_context
    ):

        score = 0

        indices = market_context.get(
            "indices",
            {}
        )

        for _, value in indices.items():

            try:

                change = float(
                    value.get(
                        "change_percent",
                        0
                    )
                )

                if change > 1:

                    score += 3

                elif change > 0:

                    score += 2

                elif change < -1:

                    score -= 3

                elif change < 0:

                    score -= 2

            except Exception:

                pass

        return score

        ##########################################################################
    # Commodity Score
    ##########################################################################

    def commodity_score(
        self,
        market_context,
        sector
    ):

        commodities = market_context.get(
            "commodities",
            {}
        )

        sector = (sector or "").lower()

        score = 0

        ######################################################################
        # Gold
        ######################################################################

        gold = commodities.get(
            "GOLD",
            {}
        )

        if sector == "financial services":

            if gold.get("trend") == "UP":
                score += 2

        ######################################################################
        # Oil (WTI / Brent)
        ######################################################################

        oil = (
            commodities.get("WTI_OIL")
            or commodities.get("BRENT_OIL")
            or {}
        )

        if sector == "energy":

            if oil.get("trend") == "UP":
                score += 5
            elif oil.get("trend") == "DOWN":
                score -= 3

        ######################################################################
        # Silver
        ######################################################################

        silver = commodities.get(
            "SILVER",
            {}
        )

        if sector == "basic materials":

            if silver.get("trend") == "UP":
                score += 2

        ######################################################################
        # Copper
        ######################################################################

        copper = commodities.get(
            "COPPER",
            {}
        )

        if sector in (
            "industrials",
            "basic materials"
        ):

            if copper.get("trend") == "UP":
                score += 2

        return score

    ##########################################################################
    # Risk Level
    ##########################################################################

    def risk_level(
        self,
        score
    ):

        if score >= 80:
            return "Low"

        if score >= 60:
            return "Medium"

        return "High"

    ##########################################################################
    # Recommendation
    ##########################################################################

    def recommendation(
        self,
        score
    ):

        ##############################################################
        # No HOLD in final output
        ##############################################################

        if score >= 80:

            return "STRONG BUY"

        if score >= 60:

            return "BUY"

        if score >= 40:

            return "SELL"

        return "STRONG SELL"
    
        ##########################################################################
    # Generate Recommendation
    ##########################################################################

    def generate(
        self,
        technical_result,
        company_info,
        company_news,
        market_context
    ):
        """
        Final recommendation engine.

        Inputs
        ------
        technical_result : dict
        company_info     : dict
        company_news     : list
        market_context   : dict
        """

        ##############################################################
        # Base Technical Score
        ##############################################################

        technical_score = technical_result.get(
            "score",
            50
        )

        ##############################################################
        # Additional Scores
        ##############################################################

        sector = company_info.get(
            "sector",
            "Unknown"
        )

        news = self.news_score(
            company_news
        )

        market = self.market_score(
            market_context
        )

        commodity = self.commodity_score(
            market_context,
            sector
        )

        sector_bonus = self.sector_score(
            sector
        )

        ##############################################################
        # Final Score
        ##############################################################

        final_score = (
            technical_score +
            news +
            market +
            commodity +
            sector_bonus
        )

        # Clamp to 0–100
        final_score = max(
            0,
            min(100, final_score)
        )

        ##############################################################
        # Recommendation & Risk
        ##############################################################

        recommendation = self.recommendation(
            final_score
        )

        risk = self.risk_level(
            final_score
        )

        ##############################################################
        # Layman-friendly Reason
        ##############################################################

        company = company_info.get(
            "company_name",
            "This company"
        )

        industry = company_info.get(
            "industry",
            "its industry"
        )

        if recommendation == "STRONG BUY":

            reason = (
                f"{company} is a well-established company in the "
                f"{industry} industry. Recent market conditions, "
                "sector outlook and news are favourable, making it "
                "one of the stronger investment opportunities."
            )

        elif recommendation == "BUY":

            reason = (
                f"{company} operates in the {industry} industry. "
                "Current market conditions indicate reasonable "
                "growth potential, making it a suitable investment "
                "for investors willing to take moderate risk."
            )

        elif recommendation == "SELL":

            reason = (
                f"{company} is showing weaker overall momentum. "
                "Current market conditions suggest caution, and "
                "waiting for better opportunities may be advisable."
            )

        else:

            reason = (
                f"{company} currently faces several unfavourable "
                "market factors. The overall outlook is weak and "
                "the downside risk appears relatively high."
            )

        ##############################################################
        # Return
        ##############################################################

        return {

            "recommendation": recommendation,

            "risk_level": risk,

            "reason": reason,

            "final_score": final_score

        }
    
    ##########################################################################
    # Commodity Recommendations
    ##########################################################################

    def commodity_recommendations(
        self,
        market_context
    ):
        """
        Build BUY / SELL recommendations for commodities
        based on trend and price movement.
        """

        recommendations = []

        commodities = market_context.get(
            "commodities",
            {}
        )

        commodity_names = {

            "GOLD": "Gold",

            "SILVER": "Silver",

            "WTI_OIL": "Crude Oil",

            "BRENT_OIL": "Brent Oil",

            "COPPER": "Copper",

            "NATURAL_GAS": "Natural Gas"

        }

        for key, values in commodities.items():

            trend = str(
                values.get(
                    "trend",
                    "NEUTRAL"
                )
            ).upper()

            price = float(
                values.get(
                    "price",
                    0
                ) or 0
            )

            recommendation = "HOLD"

            reason = "Commodity is trading sideways."

            ##############################################################
            # Up Trend
            ##############################################################

            if trend in ("UP", "BULLISH", "POSITIVE"):

                recommendation = "BUY"

                if key == "GOLD":

                    reason = (
                        "Gold is strengthening and continues to "
                        "act as a safe-haven asset."
                    )

                elif key == "SILVER":

                    reason = (
                        "Silver demand remains healthy with "
                        "positive momentum."
                    )

                elif key in ("WTI_OIL", "BRENT_OIL"):

                    reason = (
                        "Oil prices are improving which may "
                        "benefit energy markets."
                    )

                elif key == "COPPER":

                    reason = (
                        "Copper prices indicate healthy "
                        "industrial demand."
                    )

                elif key == "NATURAL_GAS":

                    reason = (
                        "Natural Gas prices are strengthening."
                    )

            ##############################################################
            # Down Trend
            ##############################################################

            elif trend in ("DOWN", "BEARISH", "NEGATIVE"):

                recommendation = "SELL"

                reason = (
                    "Commodity is weakening and downside risk "
                    "appears higher."
                )

            ##############################################################

            recommendations.append(

                {

                    "commodity":
                        commodity_names.get(
                            key,
                            key
                        ),

                    "symbol":
                        values.get(
                            "symbol",
                            key
                        ),

                    "price":
                        round(
                            price,
                            2
                        ),

                    "trend":
                        trend,

                    "recommendation":
                        recommendation,

                    "reason":
                        reason

                }

            )

        return recommendations

    ##########################################################################
    # Health Check
    ##########################################################################

    def ping(self):

        return True