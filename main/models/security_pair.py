import yfinance as yf
from datetime import datetime, timedelta
import re
import pytz
import sys
import os

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

        leverage = self.get_leverage(self.letfTicker)
        if leverage == "Not found":
            return "Error finding leverage"

        target_timezone = self.get_timezone(self.underlyingTicker)
        open_time = close_time.astimezone(target_timezone)

        change = self.get_pricing_change(open_time, datetime.now(target_timezone))
        return self.calculate_return(leverage, change)

    def get_closing_time(self, yf_ticker):
        date = datetime.today().date()

        while date.weekday() in [0, 6]:
            date = date - timedelta(days=1)

        previous_date = date - timedelta(days=1)

        data = yf_ticker.history(interval="30m", start=previous_date, end=date)
        close_time = data.iloc[-1].name + timedelta(minutes=30)
        logger.log("debug", f"{yf_ticker} closed on {close_time}")

        return close_time.to_pydatetime()

    def get_leverage(self, yf_ticker):
        info = yf_ticker.info
        # ADD SOMETHING FOR THE WORD 'SHORT/INVERSE'
        longName = info.get("longName", "Not found")
        match = re.search(r"(-?\d+x)", longName)
        if match:
            leverage = match.group(0)
        else:
            leverage = "Not found"
        logger.log("debug", f"Found leverage for {yf_ticker} to be {leverage}")
        return leverage

    def get_timezone(self, yf_ticker):
        info = yf_ticker.info
        timezone_name = info.get("timeZoneFullName", "Not found")
        logger.log("debug", f"{yf_ticker} found to be in timezone {timezone_name}")
        return pytz.timezone(timezone_name)

    def get_pricing_change(self, start_timestamp, current_timestamp):
        logger.log("debug", f"Starting pricing at {start_timestamp}")

        open_start_range = start_timestamp - timedelta(minutes=5)
        open_end_range = start_timestamp + timedelta(minutes=5)

        logger.log("debug", f"Current datetime {current_timestamp}")

        data = self.underlyingTicker.history(
            start=open_start_range, end=open_end_range, interval="1m"
        )
        start_price = data.loc[start_timestamp].Open
        logger.log(
            "debug", f"Price of {self.underlying} at {start_timestamp}: {start_price}"
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
