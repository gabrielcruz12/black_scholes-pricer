import math
from scipy.stats import norm

def _d1_d2(S, K, T, r, sigma):
	d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
	d2 = d1 - sigma * math.sqrt(T)
	return d1, d2

def call_price(S, K, T, r, sigma):
	d1, d2 = _d1_d2(S, K, T, r, sigma)
	return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)

def put_price(S, K, T, r, sigma):
	d1, d2 = _d1_d2(S, K, T, r, sigma)
	return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

if __name__ == "__main__":
	S, K, T, r, sigma = 100, 100, 1.0, 0.05, 0.20
	print(call_price(S, K, T, r, sigma))
	print(put_price(S, K, T, r, sigma))

