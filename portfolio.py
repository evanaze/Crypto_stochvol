#!/usr/bin/env python3

""" This script has two functions: 1. prompt the user for a time frame to 
	consider and an initial investment. 2. Use the results from analysis.py to
	construct an optimial investment plan.
"""

def prompt():
	done = False
	while done != True:
		inp = input("\nInitial investment into Crypto market: ")
		try:
			S_0 = float(inp)
			done = True
		except Exception:
			print("Unable to convert to suitable format. Please try again.")
	return S_0
