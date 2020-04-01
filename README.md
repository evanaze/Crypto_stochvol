# Crypto Stochastic Volatility
This is my final project for UCSB PHYS 129L - Intro to Scientific Computing.
Volatility analysis using the Heston Stochastic Volatility model on synthetic options of cryptocurrencies available on Coinbase in Python using GDAX API.
The writeup and results of this project are available in the `docs` directory.

## Usage
This program is tested with Python version 3.7.
Required packages are [gdax](https://github.com/csko/gdax-python-api) and [numpy](https://numpy.org).
Run `python3 src/main.py` to execute. You will be guided through the program.

## Future Work
* Modify for suggested portfolio optimization and tracking.
* Alter to work with equity options on exchanges.

## Works Cited
* Calibration method taken from this [paper](https://arxiv.org/abs/1511.08718).
* Data collection from [Coinbase](https://www.coinbase.com).
* Project created for the [UCSB Physics Department](https://www.physics.ucsb.edu).
