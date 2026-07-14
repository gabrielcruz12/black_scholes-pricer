from black_scholes import call_price, put_price

S = float(input("Underlying spot price (S): "))
K = float(input("Strike (K): "))
T = float(input("Time to expiry in years (T): "))
sigma = float(input("Annualized volatility, e.g. 0.20 (sigma): "))
r = float(input("Annualized risk-free rate, e.g. 0.05 (r): "))

call = call_price(S, K, T, r, sigma)
put = put_price(S, K, T, r, sigma)

print("Call price:", call)
print("Put price:", put)


