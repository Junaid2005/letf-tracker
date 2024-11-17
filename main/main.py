import argparse
import pandas as pd
from tabulate import tabulate
from models.security_pair import securityPair
from models.table import tabulateTable
from core.logger import logger
from db.dashboard import DashboardDB


def main(dashboard):
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
        tabulateTable(data)
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
        tabulateTable(data)


if __name__ == "__main__":
    dashboard = DashboardDB()
    main(dashboard)
