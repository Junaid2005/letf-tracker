import yfinance as yf
from datetime import datetime, timedelta
import pandas_market_calendars as mcal
import re
import pytz
import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.logger import logger


class securityPair:
    def __init__(self, underlying, letf):
        self.underlying = underlying
        self.letf = letf

        # add way to make sure tickers are real
        self.underlyingTicker = yf.Ticker(underlying)
        self.letfTicker = yf.Ticker(letf)

    def main(self):
        close_time = self.get_closing_time(self.letfTicker)
        if not isinstance(close_time, pd.Timestamp):
            return close_time

        leverage = self.get_leverage(self.letfTicker)
        if leverage == "Error finding leverage":
            return leverage

        target_timezone = self.get_timezone(self.underlyingTicker)
        open_time = close_time.astimezone(target_timezone)

        change = self.get_pricing_change(open_time, datetime.now(target_timezone))
        if isinstance(change, str):
            return change
        return self.calculate_return(leverage, change)

    def get_closing_time(self, yf_ticker):
        info = yf_ticker.info
        exchange_str = info.get(
            "exchange", f"Error: Can't find exchange for {yf_ticker}"
        )
        exchange = mcal.get_calendar(exchange_str)

        schedule = exchange.schedule(
            start_date=datetime.now().today() - timedelta(days=5),
            end_date=datetime.now().today(),
        )
        recent_closes = schedule[-2:]["market_close"].tolist()
        recent_closes.reverse()

        for close in recent_closes:
            if close < pytz.UTC.localize(datetime.now()):
                logger.log("debug", f"{yf_ticker} closed at {close}")
                return close

        return "Error: Can't find a recent close"

    def get_leverage(self, yf_ticker):
        info = yf_ticker.info
        # ADD SOMETHING FOR THE WORD 'SHORT/INVERSE'
        error_message = "Error finding leverage"
        longName = info.get("longName", error_message)
        match = re.search(r"(-?\d+x)", longName)
        if match:
            leverage = match.group(0)
            logger.log("debug", f"Found leverage for {yf_ticker} to be {leverage}")
            return leverage

        logger.log("debug", error_message)
        return error_message

    def get_timezone(self, yf_ticker):
        info = yf_ticker.info
        timezone_name = info.get("timeZoneFullName", "Not found")
        logger.log("debug", f"{yf_ticker} found to be in timezone {timezone_name}")
        return pytz.timezone(timezone_name)

    def get_pricing_change(self, start_timestamp, current_timestamp):
        open_start_range = start_timestamp - timedelta(minutes=5)
        open_end_range = start_timestamp + timedelta(minutes=5)

        logger.log("debug", f"Current datetime {current_timestamp}")

        data = self.underlyingTicker.history(
            start=open_start_range, end=open_end_range, interval="1m"
        )
        if data.empty:
            logger.log(
                "debug", f"Unable to price {self.underlying} at {start_timestamp}"
            )
            return "Error getting pricing"
        elif start_timestamp in data.index:
            start_price = data.loc[start_timestamp].Open
            logger.log(
                "debug",
                f"Price of {self.underlying} at {start_timestamp}: {start_price}",
            )
        else:
            start_price = data.iloc[0].Open
            logger.log(
                "debug",
                f"Failed to price {self.underlying} at open. Using {data.iloc[0].name}: {start_price}",
            )

        data = self.underlyingTicker.history(period="1d", interval="1m", prepost=True)
        current_price = data["Close"].iloc[-1]
        logger.log(
            "debug",
            f"Current price of {self.underlying} at {current_timestamp}: {current_price}",
        )
        percent = (current_price - start_price) * 100 / start_price
        return percent

    def calculate_return(self, leverage, change):
        leverage = int(leverage[:-1])
        result = leverage * change
        logger.log("debug", f"Multiplied {leverage} by {change} resulting in {result}")
        return f"{round(result, 2)}%"
