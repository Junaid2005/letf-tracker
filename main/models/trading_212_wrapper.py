"""Wrapper file for trading 212 access"""

import os
import requests
from dotenv import load_dotenv

# maybe this should be a class


def get_api_key():
    """Get the trading 212 api key from the .env file"""
    load_dotenv()
    return os.getenv("TRADING_212_KEY")


def get_portfolio():
    """Query trading 212 for the users portfolio"""
    url = "https://live.trading212.com/api/v0/equity/portfolio"
    headers = {"Authorization": get_api_key()}
    response = requests.get(url, headers=headers, timeout=5)
    data = response.json()
    return data


def get_all_instruments():
    """Query trading 212 for all the instruments available"""
    url = "https://live.trading212.com/api/v0/equity/metadata/instruments"
    headers = {"Authorization": get_api_key()}
    response = requests.get(url, headers=headers, timeout=5)
    data = response.json()
    return data


def get_account_metadata():
    """Query trading 212 for the metadata of the users account"""
    url = "https://live.trading212.com/api/v0/equity/account/info"
    headers = {"Authorization": get_api_key()}
    response = requests.get(url, headers=headers, timeout=5)
    data = response.json()
    return data
