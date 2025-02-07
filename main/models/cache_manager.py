"""Custom cache manager class"""

from datetime import datetime, timedelta
import sys
import os
from cachetools import LRUCache

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from core.logger import logger
from models.trading_212_wrapper import (
    get_portfolio,
    get_all_instruments,
    get_account_metadata,
)


# add a way to make it last between sessions, whats the point if refreshes on every cli command
# is that possible?
class CacheManager:
    """Custom cache manager class"""

    def __init__(self, maxsize=10000):
        self.cache = LRUCache(maxsize=maxsize)

    def set(self, key, value):
        """Set a value to a key"""
        self.cache[key] = value

    def get(self, key, default=None):
        """Return a value from a key"""
        return self.cache.get(key, default)

    def is_portfolio_expired(self):
        """Return if the portfolio data has expired"""
        return datetime.now() - timedelta(minutes=1) > self.get(
            "LAST_UPDATED_PORTFOLIO", datetime.min
        )

    def set_last_portfolio_update_time(self):
        """Set the last time the portfolio data was updated"""
        self.set("LAST_UPDATED_PORTFOLIO", datetime.now())

    def init_account_metadata(self):
        """Set what currency the account is set up in"""
        if self.get("CURRENCY_CODE", None) is None:
            account_metadata = get_account_metadata()
            self.set("CURRENCY_CODE", account_metadata["currencyCode"])
            logger.logger.debug(
                f"Set cache base currency as {account_metadata['currencyCode']}",
            )

    def get_account_currency(self):
        """Get what currency the account is set up in"""
        return self.get("CURRENCY_CODE", None)

    def get_security(self, ticker):
        """Return the data for a security in user's portfolio"""
        return next(
            (
                scty
                for scty in self.get("CACHED_PORTFOLIO", [])
                if scty.get("key") == ticker
            ),
            None,
        )

    def refresh_212_cache(self, pairs):
        """Refresh the cache by:
        1. Fetching data about securities in the user's portfolio
        2. Adding to each security with its own pertaining data
        """
        if not self.is_portfolio_expired():
            logger.debug("Portfolio cache is still valid")
            return
        logger.debug("Portfolio cache is expired, refreshing...")
        self.init_account_metadata()
        raw_portfolio = get_portfolio()
        raw_instruments = get_all_instruments()
        cached_portfolio = []

        for pair in pairs:
            letf_ticker = pair[2].split(".")[0]

            security = next(
                (
                    {
                        "ticker": security.get("ticker"),
                        "quantity": security.get("quantity"),
                        "averagePrice": security.get("averagePrice"),
                        "ppl": security.get("ppl"),
                        "fxPpl": security.get("fxPpl"),
                    }
                    for security in raw_portfolio
                    if isinstance(security, dict)
                    and letf_ticker in security.get("ticker", "")
                ),
                None,
            )

            if security is None:
                error_message = f"Could not find {pair[2]} in portfolio"
                logger.log("error", error_message)
                portfolio_object = {"key": pair[2], "error": error_message}
                cached_portfolio.append(portfolio_object)
                continue
            logger.logger.debug(
                f"Matched {letf_ticker} in portfolio to {security['ticker']}"
            )

            metadata = next(
                (
                    {
                        "key": pair[2],
                        "ticker": instrument.get("ticker"),
                        "currencyCode": instrument.get("currencyCode"),
                    }
                    for instrument in raw_instruments
                    if isinstance(instrument, dict)
                    and security["ticker"] == instrument.get("ticker", "")
                ),
                None,
            )

            if metadata is None:
                error_message = f"Could not find metadata for {security['ticker']}"
                logger.log("error", error_message)
                portfolio_object = {"key": pair[2], "error": error_message}
                cached_portfolio.append(portfolio_object)
                continue
            logger.debug(f"Found {metadata['ticker']} in instruments")

            portfolio_object = {**metadata, **security}
            cached_portfolio.append(portfolio_object)

        self.set("CACHED_PORTFOLIO", cached_portfolio)
        self.set_last_portfolio_update_time()
        logger.debug(f"Replaced cache with {len(cached_portfolio)} items")


cache_manager = CacheManager()
