#!/usr/bin/env python3

""" This is the main script for this project.
"""


############################################################################

if __name__ == "__main__":
	import portfolio, analysis, sample_calls	# The scripts this project uses

	
	S_0 = portfolio.prompt()
	# Ask the user if they would like to sample more points
	done = False
	while done != True:
		inp = input("\nWould you like to sample more historical price data? (y/n)   ")
		try:
			if inp.lower() == 'y':
				n, Cid, T = sample_calls.prompt_samp()
				sample_calls.random_calls(n, Cid, T)
			if inp.lower() == 'n':
				print("Continuing to analysis.\n")
				break
			inp2 = input("\nWould you like to continue sampling data? (y/n)")
			try:
				if inp2.lower() == 'y':
					continue
				if inp2.lower() == 'n':
					print("Continuing to analysis.\n")
					done = True
			except:
				print("\nUnable to interpret input. Please try again.")
		except Exception:
			print("\nUnable to interpret input. Please try again.")

	# Analyze the available data
	coins = ''
	params = []
	done = False
	while done != True:
		S_0_dat, K_dat, V_dat, T, coin = analysis.load()
		theta = analysis.LM(S_0_dat, K_dat, V_dat, T)
		params.append([theta, coin])
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
				print("Building portfolio.")
				done = True
		except Exception:
			print("\nUnable to interpret input. Please try again.")

	# Create a portfolio
	print("\nFinal parameters:", params)
