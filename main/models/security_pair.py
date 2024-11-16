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
        closeTime = self.get_closing_time(self.letfTicker)
        leverage = self.get_leverage(self.letfTicker)
        if leverage == "Not found":
            return "Error"
        location = self.get_location(self.underlyingTicker)

        datetime_obj = datetime.fromisoformat(closeTime)
        change = self.get_pricing_change(datetime_obj, location)
        return self.calculateLeverage(leverage, change)

    def get_closing_time(self, yf_ticker):
        date = datetime.today().date()

        while date.weekday() in [0, 6]:
            date = date - timedelta(days=1)

        previous_date = date - timedelta(days=1)

        data = yf_ticker.history(interval="30m", start=previous_date, end=date)
        close_row = data.iloc[-1]
        close_time = close_row.name + timedelta(minutes=30)
        logger.log("debug", f"{yf_ticker} closed at {close_time}")

        return str(close_time)

    def get_leverage(self, yf_ticker):
        info = yf_ticker.info
        # ADD SOMETHING FOR THE WORD 'SHORT'
        longName = info.get("longName", "Not found")
        match = re.search(r"(-?\d+x)", longName)
        if match:
            leverage = match.group(0)
        else:
            leverage = "Not found"
        logger.log("debug", f"Leverage for {yf_ticker} declared as {leverage}")
        return leverage

    def get_location(self, yf_ticker):
        info = yf_ticker.info
        tzName = info.get("timeZoneFullName", "Not found")
        logger.log("debug", f"{yf_ticker} found to be in timezone {tzName}")
        return tzName

    def get_pricing_change(self, start_time, timezone):
        date = datetime.today().date()
        while date.weekday() in [5, 6]:
            date = date - timedelta(days=1)

        start_time = datetime.fromisoformat(str(start_time))

        target_timezone = pytz.timezone(timezone)
        start_time = start_time.astimezone(target_timezone)
        start_date = start_time.replace(year=date.year, month=date.month, day=date.day)
        logger.log("debug", f"Starting pricing at {start_date}")

        open_start_range = start_date - timedelta(minutes=5)
        open_end_range = start_date + timedelta(minutes=5)

        current_date = datetime.now(target_timezone)
        logger.log("debug", f"Current datetime {current_date}")

        if start_date > current_date:
            return "LETF is ahead"
        else:
            data = self.underlyingTicker.history(
                start=open_start_range, end=open_end_range, interval="1m"
            )
            startPrice = data.loc[start_date].Open
            logger.log(
                "debug", f"Price of {self.underlying} at {start_date}: {startPrice}"
            )

            data = self.underlyingTicker.history(
                period="1d", interval="1m", prepost=True
            )
            latest_price = data["Close"].iloc[-1]
            logger.log(
                "debug",
                f"Current price of {self.underlying} at {current_date}: {latest_price}",
            )
            percent = (latest_price - startPrice) * 100 / startPrice
            return percent

    def calculateLeverage(self, leverage, change):
        leverage = int(leverage[:-1])
        result = leverage * change
        logger.log("debug", f"Multiplied {leverage} by {change} resulting in {result}")
        return f"{round(result, 2)}%"
