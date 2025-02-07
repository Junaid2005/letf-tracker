"""Used for querying information and pricing for securities"""

import os
import re
import sys
from datetime import timedelta

import pytz
import yfinance as yf
from core.logger import logger

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class YFinanceSecurity:
    """Wrapper for yfinance objects"""

    def __init__(self, ticker):
        self.ticker = ticker
        self.security = yf.Ticker(ticker)

    def is_real_security(self) -> bool:
        """Returns whether yfinance found the ticker"""
        return bool(self.security.info.get("longName"))

    def get_leverage(self) -> str:
        """Returns the leverage for a security"""
        info = self.security.info
        error_message = "Error finding leverage"
        long_name = info.get("longName", error_message)
        match = re.search(r"(-?\d+x)", long_name)
        if match:
            leverage = match.group(0)
            if (
                "short" in long_name.lower() or "inverse" in long_name.lower()
            ) and leverage[0] != "-":
                leverage = f"-{leverage}"
            logger.logger.debug(f"Found leverage for {self.ticker} to be {leverage}")
            return leverage

        logger.logger.debug(error_message)
        return error_message

    def get_timezone(self, log=True):
        """Returns a pytz timezone for a security"""
        info = self.security.info
        timezone_name = info.get("timeZoneFullName", "Not found")
        if log:
            logger.logger.debug(
                f"{self.ticker} found to be in timezone {timezone_name}"
            )
        return pytz.timezone(timezone_name)

    def get_pricing_change(self, start_timestamp, current_timestamp):
        """Get the difference in price between now and the start_timestamp"""
        open_start_range = start_timestamp - timedelta(minutes=5)
        open_end_range = start_timestamp + timedelta(minutes=5)

        logger.logger.debug(f"Current datetime {current_timestamp}")

        data = self.security.history(
            start=open_start_range,
            end=open_end_range,
            interval="1m",
            prepost=True,
        )
        if data.empty:
            logger.logger.debug(f"Unable to price {self.ticker} at {start_timestamp}")
            return "Error getting pricing"
        if start_timestamp in data.index:
            start_price = data.loc[start_timestamp].Open
            logger.logger.debug(
                f"Price of {self.ticker} at {start_timestamp}: {start_price}",
            )
        else:
            start_price = data.iloc[0].Open
            logger.logger.debug(
                f"Failed to price {self.ticker} at open. Using {data.iloc[0].name}: {start_price}",
            )

        data = self.security.history(period="5d", interval="1m", prepost=True)
        current_price = data["Close"].iloc[-1]
        logger.logger.debug(
            f"Price of {self.ticker} at {current_timestamp}: {current_price}",
        )
        percent = (current_price - start_price) * 100 / start_price
        return percent

    def get_intraday_data(self):
        """Returns a list containing today's pricing"""
        intraday_data = self.security.history(period="1d", interval="1m", prepost=True)[
            "Open"
        ].tolist()

        return intraday_data if intraday_data else []
        # add some way to pad data for when session is still live
