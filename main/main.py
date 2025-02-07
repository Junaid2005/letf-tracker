"""File to run cli from"""

import argparse
import os
from dotenv import load_dotenv
from currency_converter import CurrencyConverter
from models.emailer import send_email
from models.security_pair import SecurityPair
from models.table import TabulateTable
from models.cache_manager import cache_manager
from core.logger import logger
from db.dashboard import dashboard


def load_env():
    """Load the user's environment file"""
    load_dotenv()
    env_email = os.getenv("EMAIL_USER")
    env_password = os.getenv("EMAIL_PASS")
    env_t212_key = os.getenv("TRADING_212_KEY")
    return env_email, env_password, env_t212_key


def main():
    """Handles argparsers arguments"""
    sender_email, sender_password, t212_key = load_env()
    parser = argparse.ArgumentParser(description="LETF Tracker")

    parser.add_argument(
        "-s",
        "--search",
        nargs=2,
        help="""Query the Underlying Security and LETF ticker to analyse -
          Input the underlying security ticker and then LETF ticker""",
        required=False,
    )

    parser.add_argument(
        "-a",
        "--add",
        nargs=2,
        help="""Add a security pair to your dashboard -
          Input the underlying security ticker and then LETF ticker""",
        required=False,
    )

    parser.add_argument(
        "-r",
        "--remove",
        nargs=2,
        help="Remove a pair from your dashboard - Input the underlying security ticker",
        required=False,
    )

    parser.add_argument(
        "-d",
        "--dashboard",
        action="store_true",
        help="View your dashboard",
        required=False,
    )

    parser.add_argument(
        "-de", "--debug", action="store_true", help="Enable debug mode", required=False
    )

    parser.add_argument(
        "-e", "--email", action="store_true", help="Email results", required=False
    )

    parser.add_argument(
        "-ac",
        "--absolute-change",
        action="store_true",
        help="Connect to your Trading 212 account and see the absolute change",
        required=False,
    )

    parser.add_argument(
        "-ui", "--ui", action="store_true", help="Run with streamlit", required=False
    )

    args = parser.parse_args()

    if args.ui:
        streamlit_script = os.path.join(os.path.dirname(__file__), "frontend", "app.py")
        logger.logger.info(f"Starting Streamlit UI: {streamlit_script}")
        os.system(f"streamlit run {streamlit_script}")
        return

    if args.debug:
        logger.set_debug()

    if args.search:
        pair = SecurityPair(args.search[0], args.search[1])
        data = [
            {
                "Underlying": args.search[0],
                "LETF": args.search[1],
                "Ext Hours %": pair.get_percent_return(),
            }
        ]
        TabulateTable(data).print_table()
    elif args.add:
        dashboard.add_record(args.add[0], args.add[1])
    elif args.remove:
        dashboard.delete_record(args.remove[0], args.remove[1])
    elif args.dashboard:
        records = dashboard.get_all_records()
        data = []
        t212_valid = False
        ccy_rates = None
        if args.absolute_change:
            if not t212_key:
                logger.logger.warning(
                    """Your .env is not set up correctly to see the real change. 
                    See the README.md for more info""",
                )
            else:
                t212_valid = True
                ccy_rates = CurrencyConverter()
                cache_manager.refresh_212_cache(records)

        for db_pair in records:
            pair = SecurityPair(db_pair[1], db_pair[2])
            percent_change = pair.get_percent_return()
            scty_pair = {
                "Underlying": db_pair[1],
                "LETF": db_pair[2],
                "Ext Hours %": percent_change,
            }
            if t212_valid:
                scty_pair["Ext Hours"] = pair.get_absolute_return(
                    ccy_rates, percent_change
                )
            data.append(scty_pair)

        if not args.email:
            TabulateTable(data).print_table()
        else:
            if sender_email and sender_password:
                html_table = TabulateTable(data).prepare_html_table()
                send_email(sender_email, sender_password, html_table)
            else:
                logger.log(
                    "error",
                    """Your .env is not set up correctly to use email. 
                    See the README.md for more info""",
                )


if __name__ == "__main__":
    main()
