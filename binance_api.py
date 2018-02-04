"""
  Utilities to connect with the Binance API.

  Basic usage:
      from binance_api import client
"""

from binance.client import Client
from apikeys import api_key, api_secret

client = Client(api_key, api_secret, {'timeout': 99999})
