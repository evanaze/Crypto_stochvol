#!/usr/bin/env python3

""" This script defines two functions to sample data points from historical
	price data. One will take a random sample from all of the historical data,
	and the other with sample points recently before a date.
	Currently, we're defaulting to Coinbase because the number of options is << 	Binance.
"""

import numpy as np
import gdax
import time
import os

global T
global current_date, product_id, n


######################################################################

def prompt_samp():
	done = False
	while done != True:
		inp1 = input('\nWhich coin to sample from?\n1: Bitcoin\n2: Etherium\n3: Bitcoin Cash\n4: Litecoin\n')
		inp2 = input('\nHow many points to sample?\nWarning: sampling time is approximately 6 points a minute to avoid overloading the server.\n')
		try:
			T
		except NameError:
			T = 90
		inp3 = input('\nWould you like to consider a different maturity? (y/n)\nCurrent maturity: %s days   ' % (T))
		try:
			idx = int(inp1) - 1
			Coins = ['BTC-USD', 'ETH-USD', 'BCH-USD', 'LTC-USD']
			Cid = Coins[idx]
		except Exception:
			print("Unable to select product ID")

		try:
			n = int(inp2)
		except Exception:
			print("Invalid number of points to sample")

		try:
			if inp3.lower() == 'y':
				mat = input('\nNew maturity: ')
				T = int(mat)
			done = True
		except Exception:
			print("\nUnable to interpret at least one input. Please try again")
	return n, Cid, T


def random_calls(n, product_id, T):
	# Generate random dates
	def random_date_generator(start_date):
		""" This function makes random dates from when the currency began.
			Since we are considering option calls with maturity T=90 days,
			we need to also pick days 90 days before the current date
			so we can make a perfect option call from historical data.
		"""

		range_in_days = current_date + np.timedelta64(-T, "D") - np.datetime64(start_date)
		days_to_add = np.arange(1, range_in_days-1)
		random_date = np.datetime64(start_date) + np.random.choice(days_to_add, n, replace=False)
		return random_date

	def make_calls(random_dates):
		# sample the random dates
		calls = []
		count = 0
		n_rest = 3 # the number of points to rest after
		sleep = 30 # the time to sleep in between sampling

		# Sample the dates
		runtime = int((n*sleep)/(n_rest*60))
		if runtime > 1:
			s = "s"
		else:
			s = ""
		if n % n_rest == 0:
			tot_cyc = n // n_rest
		else:
			tot_cyc = n // n_rest + 1
		print('\nSampling dates on %s. Expected runtime: %s minute%s.\n' % (product_id.split('-')[0], runtime, s))
		for date in random_dates:
			# The initial price
			sample = public_client.get_product_historic_rates(
				start=date,
				end=(np.datetime64(date) + np.timedelta64(1, 'D')),
				granularity=86400,
				product_id=product_id
			)
			# The price at maturity
			s_date = date + np.timedelta64(T, 'D')
			s_sample = public_client.get_product_historic_rates(
				start=s_date,
				end=(np.datetime64(s_date) + np.timedelta64(1, 'D')),
				granularity=86400,
				product_id=product_id
			)
			count += 1

			try: # try to get the close price
				close_price = sample[0][3]
				strike = s_sample[0][3]
				# the value of the option
				v = strike - close_price
				# Save the point
				data = [str(date), close_price, strike, v]
				print(data)
				calls.append(data)
				if count % n_rest == 0:
					if n - count == 0:
						break
					print("\nSleeping for %s seconds." % (sleep))
					print("Data points taken so far:", count,"\n%s left to take. Time remaining: %s seconds.\n" % (n - count, (tot_cyc - count/n_rest)*sleep))
					time.sleep(sleep)	
				if count % 100 == 0:
					print("\nSleeping for 5 minutes.")
					time.sleep(300)
			except Exception:
				print("Unable to take data point. Exiting.")
				break
			calls.sort()
		return calls


	if True: #args.exchange == "Coinbase":
		public_client = gdax.PublicClient()
		current_date = np.datetime64(public_client.get_time().get("iso").split('T')[0])

		# Try to read in start dates from C_dates.csv
		try:
			with open("C_dates.csv", "r") as f:
				dates = f.readlines()
				for point in dates:
					if point.split(", ")[0] == product_id:
						start_date = str(point.split(", ")[1].strip("\n"))

		except Exception: # if there are not yet start dates
			from start_date import start_date
			start_date(product_id)
			random_calls(n)

		# make the random dates
		random_dates = random_date_generator(start_date)
		# Make calls from the random dates
		calls = make_calls(random_dates)
		# Save the calls to a data file with today's date and the maturity
		with open("call_data/%s_%s_%s.csv" % (product_id.split('-')[0], str(current_date), str(T)), "w") as f:
			for call in calls:
				f.write(call[0] + ', ' + str(call[1]) + ', ' + str(call[2]) + ', ' + str(call[3]) + '\n')
	else:
		print("This version is not configured to sample from Binance")
		

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"--exchange",
		type=str,
		default="Coinbase",
		choices=set(("Coinbase", "Binance")),
		help="Exchange to take data from"
	)
	parser.add_argument(
		"--id",
		type=str,
		default="BTC",
		choices=set(("ETH", "BTC", "LTC", "BCH")),
		help="Coin to get data for. By default gets USD data"
	)
	parser.add_argument(
		"--n",
		type=int,
		default="50",
		help="Number of calls to sample"
	)
	parser.add_argument(
		"--T",
		type=int,
		default="90",
		help="Maturity to sample"
	)
	args = parser.parse_args()
	
	n = args.n
	T = args.T
	Cid = args.id

	random_calls(n, Cid, T)
