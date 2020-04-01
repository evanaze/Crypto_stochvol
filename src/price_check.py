#!/usr/env python3

""" This script checks the value of an existing portfolio and displays it to the user.
"""

import os

def check():
	import gdax
	done = False
	while done != True:
		# Display the current portfolios
		portfolios = os.listdir('portfolios/')
		print("\nExisting portfolios: ")
		for i in range(len(portfolios)):
			print(str(i) + ': ' + portfolios[i])
		inp = input("\nChoose a portfolio to check: ")
		try:
			choice = int(inp)
			path = 'portfolios/' + portfolios[choice]
			investments = []
			with open(path, 'r') as f:
				inv = f.readlines()
				for i in range(len(inv)):
					point = inv[i].split(', ')
					prod_id = point[0]
					currency = float(point[1])
					S_0 = float(point[2])
					investments.append((prod_id, currency, S_0))
		except ValueError:
			print("Your input could not be interpreted")
		pc = gdax.PublicClient()
		profit = 0
		for i in investments:
			name = i[0] + '-USD'
			stats = pc.get_product_24hr_stats(name)
			S_0 = i[2]
			currency = i[1]
			S_t = (float(stats['high']) + float(stats['low']))/2
			print("Your investment in %s at %s USD is now worth %s" % (i[0], S_0, S_t*currency))
			profit += S_t*currency - S_0
		print("\nYour total profit/loss for this portfolio:", profit) 
		inp2 = input("\nExamine another portfolio? (y/n)  ")
		try:
			if inp2.lower() == 'y':
				continue
			if inp2.lower() == 'n':
				print("Exiting")
				done = True
		except ValueError:
			print("Your input could not be interpreted")


if __name__ == "__main__":
	check()
