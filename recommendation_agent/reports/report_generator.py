"""
==============================================================================
report_generator.py

Report Generator

Creates

output/
    recommendations_{timestamp}.json
    recommendations_{timestamp}.csv

==============================================================================

"""

import json
import pandas as pd

from config import (

    JSON_OUTPUT,

    CSV_OUTPUT

)

from utils.logger import logger

class ReportGenerator:

    ##########################################################################
    # Constructor
    ##########################################################################

    def __init__(self):

        pass

    ##########################################################################
    # JSON
    ##########################################################################

    def generate_json(

        self,

        report

    ):

        try:

            with open(

                JSON_OUTPUT,

                "w",

                encoding="utf-8"

            ) as file:

                json.dump(

                    report,

                    file,

                    indent=4,

                    default=str,

                    ensure_ascii=False

                )

            logger.info(

                "JSON report created : %s",

                JSON_OUTPUT

            )

        except Exception as ex:

            logger.exception(

                "JSON generation failed : %s",

                ex

            )

    ##########################################################################
    # CSV
    ##########################################################################

    def generate_csv(

        self,

        recommendations

    ):

        if not recommendations:

            logger.warning(

                "No recommendations available"

            )

            return

        try:

            rows = []

            ##############################################################
            # Keep only user-friendly columns
            ##############################################################

            for stock in recommendations:

                rows.append(

                    {

                        "Symbol":
                            stock.get(
                                "symbol"
                            ),

                        "Company":
                            stock.get(
                                "company_name"
                            ),

                        "Country":
                            stock.get(
                                "country"
                            ),

                        "Sector":
                            stock.get(
                                "sector"
                            ),

                        "Industry":
                            stock.get(
                                "industry"
                            ),

                        "Price":
                            stock.get(
                                "price"
                            ),

                        "Recommendation":
                            stock.get(
                                "recommendation"
                            ),

                        "Risk":
                            stock.get(
                                "risk"
                            ),

                        "Score":
                            stock.get(
                                "score"
                            ),

                        "Reason":
                            stock.get(
                                "reason"
                            )

                    }

                )

            ##############################################################
            # Highest score first
            ##############################################################

            rows = sorted(
                rows,
                key=lambda x: x["Score"],
                reverse=True
            )

            df = pd.DataFrame(rows)

            df.to_csv(

                CSV_OUTPUT,

                index=False

            )

            self.csv_output_file = CSV_OUTPUT

            logger.info(

                "CSV report created : %s",

                CSV_OUTPUT

            )

        except Exception as ex:

            logger.exception(

                "CSV generation failed : %s",

                ex

            )

    ##########################################################################
    # Complete Report
    ##########################################################################

    def generate_report(

        self,

        recommendations,

        market_context,

        country_summary,

        commodity_recommendations

    ):

        """
        Final report structure.

        {
            market_context
            commodity_recommendations
            country_summary
            recommendations
        }

        """

        try:

            ##############################################################
            # Final JSON Structure
            ##############################################################

            report = {

                "market_context": market_context,

                "commodity_recommendations": commodity_recommendations,

                "country_summary": country_summary,

                "recommendations": recommendations

            }

            ##############################################################
            # Generate JSON
            ##############################################################

            self.generate_json(
                report
            )

            ##############################################################
            # Generate CSV
            ##############################################################

            self.generate_csv(
                recommendations
            )

            ##############################################################
            # Logging
            ##############################################################

            logger.info(

                "=" * 80

            )

            logger.info(

                "Reports generated successfully"

            )

            logger.info(

                "JSON : %s",

                JSON_OUTPUT

            )

            logger.info(

                "CSV  : %s",

                CSV_OUTPUT

            )

            logger.info(

                "=" * 80

            )

            logger.info(

                "Total recommendations : %s",

                len(recommendations)

            )
            return report

        except Exception as ex:

            logger.exception(

                "Report generation failed : %s",

                ex

            )

            return {}