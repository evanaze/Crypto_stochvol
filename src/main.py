#!/usr/bin/env python3

""" This is the main script for this project.
"""

import analysis, sample_calls    # The scripts this project uses
import gdax

from os import listdir
import numpy as np


##################################################################

def prompt():
	""" General interactive prompt to guide the user through data collection.
	"""

	# Inform the user on what price data has been taken
	print("\nCurrent available historical data for calibration: ")
	data_files = listdir('call_data/')
	for i in range(len(data_files)):
		print(data_files[i])
	# Ask the user if they would like to sample more points
	done = False
	while done != True:
		inp = input("\nWould you like to sample more historical price data? (y/n)   ")
		try:
			if inp.lower() == 'y':
				sample_calls.random_calls()
			if inp.lower() == 'n':
				print("Continuing to analysis.\n")
				done = True
			else:
				print("Invalid input.")
		except ValueError:
			print("\nUnable to interpret input. Please try again.")

def analyze():
	""" Allows the user to select which portfolios to analyze
	"""

	# Analyze the available data
	coins = ''
	params = []
	done = False
	while done != True:
		S_0_dat, K_dat, V_dat, T, coin = analysis.load()
		theta, T = analysis.LM(S_0_dat, K_dat, V_dat, T)
		params.append([theta, T, coin])
		if coins == '':
			coins = coin
		else:
			coins += ', ' + coin + '.'
		try:
			print("Current coins analyzed:", coins)
			inp = input("Analyze another dataset? (y/n)	")
			if inp.lower() == 'y':
				continue
			if inp.lower() == 'n':
				print("\nFinal parameters:", params)
				done = True
		except ValueError:
			print("\nUnable to interpret input. Please try again.")
	return params

def invest():
	""" Simple script for obaining the amount desired to invest
	"""
	done = False
	while done != True:
		inp = input("\nInitial investment into Crypto market: ")
		try:
			S_0 = float(inp)
			done = True 
		except Exception: 
			print("Unable to convert to suitable format. Please try again.")
	return S_0

def generate_portfolio(S_0, params):
	""" This script analyzes possible portfolios based on the calculated
		parameters on the observed data, and the user inputted investment.
	"""
	public_client = gdax.PublicClient()
	allvar = []
	sumvar = 0
	for coin in params:
		theta = coin[0]
		v = theta[0]
		T = coin[1]
		prod_id = coin[2]
		# Get the current value of the coin, i.e. how much you bought
		name = prod_id + '-USD'
		stats = public_client.get_product_24hr_stats(name)
		value = (float(stats['high']) + float(stats['low']))/2
		allvar.append([prod_id, value, v])
		sumvar += v
	priority = sorted(allvar, key=lambda i: i[2])
	portfolio = []
	for i in priority:
		investment = S_0*i[2]/sumvar
		currency = investment/i[1]
		portfolio.append((i[0], currency, investment)) # id, investment, currency
	print("\nYour suggested investments are: \n")
	for coin in portfolio:
		print("%s: %s for %s USD" % (coin[0], coin[1], coin[2]))
	# Prompt to save the portfolio
	done = False
	while done != True:
		inp = input("\nWould you like to save this portfolio? (y/n)	")
		try:
			if inp.lower() == 'y':
				public_client = gdax.PublicClient()
				current_date = np.datetime64(public_client.get_time().get("iso").split('T')[0])
				# Save the file
				with open("portfolios/%s.txt" % (current_date), "w") as f:
					for coin in portfolio:
						f.write(str(coin[0]) + ', ' + str(coin[1]) + ', ' + str(coin[2]) + '\n')
				print("Portfolio saved. Exiting.\n")
				done = True
			if inp.lower() == 'n':
				print("Program complete. Exiting.\n")
				done = True
		except ValueError:
			print("Your input could not be interpreted.")


if __name__ == "__main__":
	prompt()
	params = analyze()
	S_0 = invest()
	generate_portfolio(S_0, params)
	
