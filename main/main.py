import argparse
from dotenv import load_dotenv
import os
from models.email import send_email
from models.security_pair import securityPair
from models.table import tabulateTable
from core.logger import logger
from db.dashboard import DashboardDB


def loadEnv():
    load_dotenv()
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASS")
    return sender_email, sender_password


def main(dashboard, sender_email=None, sender_password=None, allow_email=False):
    parser = argparse.ArgumentParser(description="LETF Tracker")

    parser.add_argument(
        "-s",
        "--search",
        nargs=2,
        help="Query the Underlying Security and LETF ticker to analyse - Input the underlying security ticker and then LETF ticker",
        required=False,
    )

    parser.add_argument(
        "-a",
        "--add",
        nargs=2,
        help="Add a security pair to your dashboard - Input the underlying security ticker and then LETF ticker",
        required=False,
    )

    parser.add_argument(
        "-r",
        "--remove",
        nargs=1,
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

    args = parser.parse_args()

    if args.debug:
        logger.setDebug()

    if args.search:
        pair = securityPair(args.search[0], args.search[1])
        data = [
            {
                "Underlying": args.search[0],
                "LETF": args.search[1],
                "Change": pair.main(),
            }
        ]
        tabulateTable(data).print_table()
    elif args.add:
        dashboard.add_record(args.add[0], args.add[1])
        logger.log("info", f"Added {args.add[0], args.add[1]} to dashboard")
    elif args.remove:
        dashboard.delete_record(args.remove[0])
        logger.log("info", f"Removed {args.remove[0]} from dashboard")
    elif args.dashboard:
        records = dashboard.get_all_records()
        data = []
        for db_pair in records:
            pair = securityPair(db_pair[1], db_pair[2])
            data.append(
                {"Underlying": db_pair[1], "LETF": db_pair[2], "Change": pair.main()}
            )

        if not args.email:
            tabulateTable(data).print_table()
        else:
            if allow_email:
                html_table = tabulateTable(data).prepare_html_table()
                send_email(sender_email, sender_password, html_table)
            else:
                logger.log("error", "Please set up your .env correctly to use email")


if __name__ == "__main__":
    dashboard = DashboardDB()
    sender_email, sender_password = loadEnv()
    if sender_email and sender_password:
        main(dashboard, sender_email, sender_password, True)
    else:
        logger.log(
            "warning",
            "Disabling email functionality... .env is not set up correctly. See the README.md for more info on how to do so.",
        )
        main(dashboard, allow_email=False)
