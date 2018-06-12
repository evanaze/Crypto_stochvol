#!/usr/bin/env python3

""" This script gives some exploratory info about our data.
	Namely, the Coins & Tokens currently available.
"""

import gdax
from binance.client import Client

# GDAX
public_client = gdax.PublicClient()
## Current Coinbase prices
C_prices = public_client.get_products()

# Binance
api_key = "DBofF4N98IxNtPED3vNfQuDkIIlxYlAJL9Ycl2tWdQ1OJIz13qgCOd2Hrehl2HMm"
api_secret = "vCe6E3vVRtqsuxjqbhZSQn9IgrCOPUpCJxVfkb97Mnw1PbHk36J8JmxVEB8isrMu"

client = Client(api_key, api_secret)

## Current Binance prices
B_prices = client.get_all_tickers()

# Now, lets look at the size of the data we currently have
## Unique symbols for Coinbase
C_symbols = list(set(dic.get('base_currency') for dic in C_prices))
print('\nCoins available through Coinbase: ',C_symbols)

## Unique symbols for Binance
B_symbols = list(set(dic.get('symbol') for dic in B_prices))
print('\nTokens currently available through binance: %s  And %s more...\n' % (B_symbols[:7], len(B_symbols) - 7))

print(C_prices)
