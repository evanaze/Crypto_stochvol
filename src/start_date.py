#!/usr/bin/env python3

""" This script gets the first date a coin was available on Coinbase.
	It saves these dates to a file `Cbase_dates.dat` for reference.
"""

import os.path
from time import sleep
import numpy as np
import gdax


###########################################################################

def start_date(product_id):
	print("Finding start date for:",product_id)
	# Let's get the current date of the GDAX server
	current_date = np.datetime64(public_client.get_time().get("iso").split('T')[0])

	# Now to find the start date
	test_start = current_date 
	test_end = current_date
	test = np.zeros(300)
	while len(test) == 300:
		test_start -= np.timedelta64(300, 'D')
		test = public_client.get_product_historic_rates(
			start=test_start,
			end=test_end,
			granularity=86400,
			product_id=product_id
		)
		test_end -= np.timedelta64(300, 'D')
	# Calculate the start date based on when the loop ended
	start_date = np.datetime64(test_start) + np.timedelta64(300 - len(test), 'D')

	# Test to see if we got it right:
	test = public_client.get_product_historic_rates(
		start=np.datetime64(start_date) - 2,
		end=np.datetime64(start_date) - 1,
		granularity=86400,
		product_id=product_id
	)

	if test == []:
		print("\n`start_date.py` was successful. %s was first offered %s on Coinbase.\n" % (product_id, start_date))
	else:
		print("`start_date.py` was not successful.")

	return start_date


if __name__ == "__main__":
	# Start the Coinbase client
	public_client = gdax.PublicClient()
	# Get the available symbols
	C_prices = public_client.get_products()
	C_symbols = list(set(dic.get('id') for dic in C_prices))
	
	file = open("C_dates.csv", "w+")
	for product_id in C_symbols:
		# Let's only do coins in US Dollars
		if product_id.split("-")[1] == 'USD':
			date = start_date(product_id)
			# Write the results to a file
			file.write(product_id + ", " + str(date) + "\n")
	file.close()
