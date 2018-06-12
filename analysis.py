#!/usr/bin/env python3

""" We define the market price of a call option with strike K and maturity T 
	C(K_i, T_i). The price of the stock is modeled by the Heston Stochastic
	volatility model, where the price of the stock at time t S_t has variance
	v_t such that the variance approaches some long-term variance v_bar that 
	it approaches at rate k with volatility sigma and correlation between
	its proccess and the process of the stock price rho.

	In this script, we use Cui's method of calibrating this stochastic
	volatility model.
	From here, we can determine the fair price of the stock using a different
	script, `fair_price.py`.
"""

import numpy as np
import warnings
from os import listdir
import gdax

warnings.simplefilter('ignore')

global T, ndat

def load():
	# Load the data
	print("\nAvailable data files for analysis: ")
	data_files = listdir('call_data/')
	for i in range(len(data_files)):
		print(str(i) + ': ' + data_files[i])

	infile = input("\nChoose the data file to read: ")
	# Make sure the file extention wasn't included
	try:
		choice = int(infile)
	except:
		print("Unable to interpret choice. Please provide the number of your choice.")

	name = data_files[choice]
	try:
		T = int(name.split("_")[2])
	except Exception:
		T = 90
	path = 'call_data/' + name
	S_0_dat = []
	K_dat = []
	V_dat = []
	with open(path, 'r') as f:
		calls = f.readlines()
		for call in calls:
			point = call.split(', ')
			S_0_dat.append(float(point[1]))
			K_dat.append(float(point[2]))
			V_dat.append(float(point[3]))
	coin = name.split("_")[0]
	return S_0_dat, K_dat, V_dat, T, coin

############################################################################

""" These are the functions that will help us optimize to our data.
	r() gives us the residues of the estimated value and the calcualted value.
	We optimize with respect to the parameter theta with LM()
"""

# These functions help us calculate the predicted value
def P_c1(theta, u, K, t, S_0):
	return np.real(np.exp(-1j*u*np.log(K))/(1j*u)*phi(theta, u - 1j, t, S_0))

def P_c2(theta, u, K, t, S_0):
	return np.real(np.exp(-1j*u*np.log(K))/(1j*u)*phi(theta, u, t, S_0))

def C(theta, S_0, K, t): # The predicted value
	N = 10
	tot = 0
	for k in range(N):
		i = k + 1
		# Numeric integration
		if k == 0:
			k = 0.1
		fk_1 = 1/np.pi*(P_c1(theta, k, K, t, S_0) - K*P_c2(theta, k, K, t, S_0))
		fk = 1/np.pi*(P_c1(theta, i, K, t, S_0) - K*P_c2(theta, i, K, t, S_0))
		dk = (i - k)/N
		tot += (fk_1 + fk)/2*dk
	return (S_0 - K)/2 + tot

# The residues we wish to minimize
def r(theta, S_0_dat, K_dat, V_dat, T):
	residues = np.array(np.zeros(ndat))
	for i in range(ndat):
		S_0 = S_0_dat[i]
		K = K_dat[i]
		v = V_dat[i]
		if v <= 0:
			v = 0
		residues[i] =  C(theta, S_0, K, T) - v
	return residues.reshape(ndat, 1)

def params(theta, u, t):
	# The parameters we wish to optimize
	v = theta[0]
	v_bar = theta[1]
	rho = theta[2]
	k = theta[3]
	sigma = theta[4]

	# Parameters from the characteristic function
	ksi = k - sigma*rho*1j*u
	d = np.sqrt(ksi**2 + sigma**2*(u**2 + 1j*u))
	g = (ksi - d)/(ksi + d)

	# Larger parameters
	A_1 = (u**2 + 1j*u)*np.sinh(d*t/2)
	A_2 = d*np.cosh(d*t/2) + ksi*np.sinh(d*t/2)
	A = A_1/A_2
	B = d*np.exp(k*t/2)/A_2
	D = np.log(d) + (k - d)*t/2 - np.log( (d+ksi)/2 + (d-ksi)/2*np.exp(-d*t))
	return v, v_bar, rho, k, sigma, ksi, d, g, A_1, A_2, A, B, D


# The characteristic function
def phi(theta, u, t, S_0):
	v, v_bar, rho, k , sigma, ksi, d, g, A_1, A_2, A, B, D = params(theta, u, t)
	return np.exp(1j*u*(np.log(S_0)) - t*k*v_bar*rho*1j*u/sigma - v*A + 2*k*v_bar/(sigma**2)*D)


# The gradient of the characteristic function. Inedependent of phi.
def h(theta, K, t, u):
	v, v_bar, rho, k , sigma, ksi, d, g, A_1, A_2, A, B, D = params(theta, u, t)

	dddrho = -ksi*sigma*1j*u/d
	dA_2drho = -sigma*1j*u*(2 + t*ksi)*(ksi*np.cosh(d*t/2)/(2*d) + d*np.sinh(d*t/2))
	dA_1drho = -1j*u*(u**2 + 1j*u)*t*ksi*sigma*np.cosh(d*t/2)/(2*d)
	dAdrho = 1/A_2*dA_1drho - A/A_2*dA_2drho
	dBdrho = np.exp(k*t/2)*(1/A_2*dddrho - d/(A_2**2)*dA_2drho)
	dBdk = 1j/(sigma*u)*dBdrho + t*B/2
	dddsigma = (rho/sigma - 1/ksi)*dddrho + sigma*u**2/d
	dA_1dsigma = (u**2 + 1j*u)*t/2*dddsigma*np.cosh(d*t/2)
	dA_2dsigma = rho/sigma*dA_2drho - (2+t*ksi)/(1j*u*t*ksi)*dA_1drho + sigma*t*A_1/2
	dAdsigma = 1/A_2*dA_1dsigma - A/A_2*dA_2dsigma
	# Returns a 5 element gradient for each parameter
	return np.array([-A, 2*k/(sigma**2)*D - t*k*rho*1j*u/sigma, -v*dAdrho + 2*k*v_bar/(sigma**2*d)*(dddrho - d/A_2*dA_2drho) - t*k*v_bar*1j*u/sigma, v/(sigma*1j*u)*dAdrho + 2*v_bar/(sigma**2)*D + 2*k*v_bar/(sigma**2*B)*dBdk - t*v_bar*rho*1j*u/sigma, -v*dAdsigma - 4*k*v_bar/(sigma**3)*D + 2*k*v_bar/(sigma**2*d)*(dddsigma - d/A_2*dA_2dsigma) + t*k*v_bar*rho*1j*u/(sigma**2)])

# Helps us evaluate the jacobian
def P1(theta, u, K, t, S_0, h_j):
	return np.real(K**(-1j*u)/(1j*u)*phi(theta, u-1j, t, S_0)*h_j)

def P2(theta, u, K, t, S_0, h_j):
	return np.real(K**(-1j*u)/(1j*u)*phi(theta, u, t, S_0)*h_j)

# The Jacobian
def jac(theta, S_0_dat, K_dat, t):
	N = 10
	grad = np.array(np.zeros(5))
	Grad = np.matrix(np.zeros((ndat, 5)))
	for a in range(ndat):
		S_0 = S_0_dat[a]
		K = K_dat[a]
		tot = 0
		for k in range(N):
			i = k + 1
			# Numeric integration
			if k == 0:
				k = 0.1
			# Calculate h(u)
			h_k = h(theta, K, t, k)
			h_i = h(theta, K, t, i)
			# Numeric integration
			if k == 0:
				k = 0.1
			fk_1 = 1/np.pi*(P1(theta, k, K, t, S_0, h_k) - K*P2(theta, k, K, t, S_0, h_k))
			fk = 1/np.pi*(P1(theta, i, K, t, S_0, h_i) - K*P2(theta, i, K, t, S_0, h_i))
			h_k = h_i
			dk = (i - k)/N
			tot += (fk_1 + fk)/2*dk
		Grad[a, :] = tot
	return Grad.T

def flatten(l):
	return np.array([item for sublist in l for item in sublist])

########################################################################

""" Now, lets calibrate to our observations.
"""


def LM(S_0_dat, K_dat, V_dat, T):
	""" This function optimizes our parameters using the Levenberg-Marquardt
		algorithm.
	"""
	global ndat
	
	ndat = len(K_dat)	
	# The initial guess at theta
	theta = np.array([0.08, 0.10, -0.80, 3.00, 0.25]).reshape(5,)

	# Parameters for optimization
	e = np.ones((ndat, 1))
	thresh = 1e-8   # Threshold

	print("\nCalibrating...")
	N = 10000 # number of steps
	v = 2
	for i in range(N):
		theta[0] = v
		res = r(theta, S_0_dat, K_dat, V_dat, T)
		f = np.linalg.norm(res)
		J = jac(theta, S_0_dat, K_dat, T)
		if i == 0:
			mu = max(np.diagonal(J).copy())
		deltaf = flatten(np.array(J*res)).reshape(5,1)
		dtheta = flatten(np.array(1/(J*J.T + mu)*(deltaf)))
		theta_k1 = theta + dtheta
		res1 = r(theta_k1, S_0_dat, K_dat, V_dat, T)
		f1 = np.linalg.norm(res1)
		dL = np.dot(dtheta.reshape(1,5), mu*dtheta.reshape(5,1) + deltaf)
		dF = f - f1
		if i % 15 == 0:
			print("\nIteration %s. Current parameters: %s" % (i, theta))
		if dF > 0 and dL > 0:
			theta = theta_k1
			v = theta[0]
		else:
			mu = mu*v
			v = 2*v
		if f <= thresh:
			print("\nCondition 1 met:")
			print("Objective function minimized")
			return theta
			break
		if np.linalg.norm(J*e) <= thresh:
			print("\nCondition 2 met:")
			print("Small gradient step")
			return theta
			break
		if np.linalg.norm(dtheta)/np.linalg.norm(theta) <= thresh:
			print("\nCondition 3 met:")
			print("Stagnating update")
			return theta
			break
	print("\nThe calibration did not converge.\n")


if __name__ == "__main__":
	import gdax, portfolio

	S_0_dat, K_dat, V_dat, T, coin = load()
	theta = LM(theta, S_0_dat, K_dat, V_dat, T)
	print("Final parameters:", theta)
	# Get the current info of the coin
	pc = gdax.PublicClient()
	# The name of the coin we're analyzing
	name = coin + '-USD'
	stats = pc.get_product_24hr_stats(name)
	# Average the 24hr high and low to estimate the current value of the coin
	S_0 = (float(stats['high']) + float(stats['low']))/2
	print("\nThe current value of %s is roughly %s USD." % (coin, S_0))
	# Let's say you want to make 10% after 90 days
	K = int(S_0*0.9)
	print("If you wanted to make 10 percent profit in 90 days, the expected value of this option is: %s" % (C(theta, S_0, K, T)))
