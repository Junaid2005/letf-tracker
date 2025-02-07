"""File defines the SecurityPair class that manages LETF and Underlying Security Relationship"""

# pylint: disable=broad-exception-caught
# this is just laziness tbh i should find the errors ^
from datetime import datetime, timedelta
import sys
import os
import copy
import pandas as pd
import pandas_market_calendars as mcal
import pytz

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from core.logger import logger
from models.cache_manager import cache_manager
from models.yfinance_wrapper import YFinanceSecurity

# update all 'yf_ticker' to represent what the ticker is, letf or the underlying WHERE IT MAKES


class SecurityPair:
    """Class holding the leveraged etf and its underlying security"""

    def __init__(self, underlying, letf):
        self.underlying = underlying
        self.letf = letf

        self.underlying_ticker = YFinanceSecurity(underlying)
        self.letf_ticker = YFinanceSecurity(letf)

    def is_valid_pair(self) -> bool:
        """Returns if both of the tickers provided are found by yfinance"""
        return (
            self.underlying_ticker.is_real_security()
            and self.letf_ticker.is_real_security()
        )

    def get_percent_return(self):
        """Returns extended hours percentage returns in a pair (or error)"""
        # is this valid behaviour
        # should i really be telling the user to stop using the tool if both pairs are live
        if self.is_pair_live():
            return "Pair is already in sync"

        close_time = self.get_closing_time(self.letf_ticker)
        if not isinstance(close_time, pd.Timestamp):
            return close_time

        target_timezone = self.underlying_ticker.get_timezone()
        open_time = close_time.astimezone(target_timezone)

        change = self.underlying_ticker.get_pricing_change(
            open_time, datetime.now(target_timezone)
        )
        if isinstance(change, str):
            return change

        leverage = self.letf_ticker.get_leverage()
        if leverage == "Error finding leverage":
            return leverage

        return self.calculate_return(leverage, change)

    def get_absolute_return(self, ccy_rates, percent_return):
        """Returns absolute return in a pair (or error)"""
        try:
            change = float(percent_return.rstrip("%")) / 100
        except ValueError:
            return "No return to calculate real value from"

        base_ccy = cache_manager.get("CURRENCY_CODE")
        security = copy.deepcopy(cache_manager.get_security(self.letf))
        if security.get("error"):
            return security["error"]

        raw_value = security["quantity"] * security["averagePrice"]
        logger.logger.debug(
            f"Multiplying {security['quantity']} by {security['averagePrice']} to get {raw_value}",
        )

        if security["currencyCode"] == "GBX":
            raw_value /= 100
            security["currencyCode"] = "GBP"
            logger.logger.debug(f"Converted GBX to GBP. New value is {raw_value}")

        if security["currencyCode"] != base_ccy:
            raw_value = ccy_rates.convert(raw_value, security["currencyCode"], base_ccy)
            logger.logger.debug(
                f"Converted {security['currencyCode']} to {base_ccy}. New value is {raw_value}",
            )

        ppl = security.get("ppl")
        fx_ppl = security.get("fxPpl") or 0
        original_value = raw_value + ppl + fx_ppl
        logger.logger.debug(
            f"Added PPLs (ppl: {ppl}, fxPpl: {fx_ppl}) to get {original_value}",
        )
        live_value = original_value * change
        logger.logger.debug(
            f"Multiplied {original_value} by {change} to get {live_value}"
        )
        return live_value

    def __is_security_live(self, yf_ticker):
        name = yf_ticker.security.info.get("shortName", "")
        cal = self.__get_exchange_cal(yf_ticker)
        if isinstance(cal, str):
            logger.logger.error(cal)
            return False
        schedule = self.__get_schedule(cal)
        if isinstance(schedule, str):
            logger.logger.error(f"{schedule} for {name}")
            return False

        now_utc = datetime.now(pytz.utc)
        now_timestamp = pd.Timestamp(now_utc)
        converted_timestamp = now_timestamp.tz_convert(
            yf_ticker.get_timezone(log=False)
        )
        try:
            is_open = cal.open_at_time(schedule, converted_timestamp)
        except (ValueError, IndexError):
            is_open = False
        logger.logger.debug(f"{name} is currently {'trading' if is_open else 'closed'}")
        return is_open

    def is_pair_live(self) -> bool:
        """Returns if both of the securities are currently trading"""
        return self.__is_security_live(self.letf_ticker) and self.__is_security_live(
            self.underlying_ticker
        )

    def get_closing_time(self, yf_ticker_letf):
        """Returns last closing time of letf"""
        info = yf_ticker_letf.security.info
        name = info.get("symbol", "Couldn't find symbol")
        exchange_str = info.get("exchange", f"Error: Can't find exchange for {name}")
        exchange = mcal.get_calendar(exchange_str)

        schedule = exchange.schedule(
            start_date=datetime.now().today() - timedelta(days=5),
            end_date=datetime.now().today(),
        )
        recent_closes = schedule[-2:]["market_close"].tolist()
        recent_closes.reverse()

        for close in recent_closes:
            if close < datetime.now(pytz.utc):
                logger.logger.debug(f"{name} closed at {close}")
                return close

        return "Error: Can't find a recent close"

    def calculate_return(self, leverage, change):
        """Multiplies percentage return by leverage found"""
        leverage = int(leverage[:-1])
        result = leverage * change
        logger.logger.debug(f"Multiplied {leverage} by {change} resulting in {result}")
        return f"{round(result, 2)}%"

    def __get_exchange_cal(self, yf_ticker):
        yf_ticker_info = yf_ticker.security.info
        exchange_str = yf_ticker_info.get(
            "exchange", f"Error: Can't find exchange for {yf_ticker}"
        )
        exchange_map = {"NMS": "NASDAQ", "NGM": "NASDAQ"}
        try:
            exchange_cal = mcal.get_calendar(
                exchange_map.get(exchange_str, exchange_str)
            )
            return exchange_cal
        except Exception:
            name = yf_ticker_info.get("shortName", "")
            error_message = f"Could not get calendar for exchange {name}"
            return f"Error: {error_message}"

    def __get_schedule(
        self,
        exchange_cal,
        start=datetime.now().today(),
        end=datetime.now().today(),
    ):
        try:
            schedule = exchange_cal.schedule(
                start_date=start, end_date=end, start="pre", end="post"
            )
            return schedule
        except Exception:
            logger.logger.warning("Exchange has no extended hours")
            try:
                schedule = exchange_cal.schedule(
                    start_date=start,
                    end_date=end,
                )
                return schedule
            except Exception:
                return "Error getting schedule for exchange"
