import streamlit as st
from black_scholes import call_price, put_price

import numpy as np
import matplotlib.pyplot as plt

import sqlite3
conn = sqlite3.connect("black_scholes.db")
cursor = conn.cursor()

cursor.execute("""
	CREATE TABLE IF NOT EXISTS inputs(
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		S REAL,
		K REAL,
		T REAL,
		sigma REAL,
		r REAL
	)
""")

cursor.execute("""
	CREATE TABLE IF NOT EXISTS outputs (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		input_id INTEGER,
		vol_shock REAL,
		price_shock REAL,
		call_value REAL,
		put_value REAL,
		FOREIGN KEY (input_id) REFERENCES inputs (id)
	)
""")

conn.commit()

st.title("Black-Scholes Option Pricer")

S = st.number_input("Underlying spot price (S)", value=100.0)
K =st.number_input("Strike price (K)", value=100.0)
T = st.number_input("Time to expiry in years (T)", value=1.0)
sigma = st.number_input("Annualized volatility (sigma)", value=0.20)
r = st.number_input("Annualized risk-free rate (r)", value=0.05)
call_purchase_price = st.number_input("Call purchase price (paid)", value=10.0)
put_purchase_price = st.number_input("Put purchase price (paid)", value=5.0)

spot_range = np.linspace(S * 0.8, S * 1.2, 10)
vol_range = np.linspace(sigma * 0.5, sigma * 1.5, 10)

call_grid = np.zeros((len(vol_range), len(spot_range)))
for i, v in enumerate(vol_range):
	for j, s in enumerate(spot_range):
		call_grid[i, j] = call_price(s, K, T, r, v)

put_grid = np.zeros((len(vol_range), len(spot_range)))
for i, v in enumerate(vol_range):
	for j, s in enumerate(spot_range):
		put_grid[i, j] = put_price(s, K, T, r, v)

call_pnl = call_grid - call_purchase_price
put_pnl = put_grid - put_purchase_price

if st.button("Calculate"):
	call = call_price(S, K, T, r, sigma)
	put = put_price(S, K, T, r, sigma)
	st.write("Call price:", call)
	st.write("Put price:", put)

	cursor.execute(
		"INSERT INTO inputs (S, K, T, sigma, r) VALUES (?, ?, ?, ?, ?)",
		(S, K, T, sigma, r)
	)
	input_id = cursor.lastrowid
	conn.commit()

	for i, v in enumerate(vol_range):
		for j, s in enumerate(spot_range):
			vol_shock = v - sigma
			price_shock = s - S
			call_value = call_grid[i, j]
			put_value = put_grid[i, j]

			cursor.execute(
				"INSERT INTO outputs (input_id, vol_shock, price_shock, call_value, put_value) VALUES (?, ?, ?, ?, ?)",
				(input_id, vol_shock, price_shock, call_value, put_value)
			)

	conn.commit()

call_pnl = call_grid - call_purchase_price
put_pnl = put_grid - put_purchase_price

fig, ax = plt.subplots()
im = ax.imshow(call_pnl, cmap="RdYlGn", aspect="auto", vmin=-abs(call_pnl).max(), vmax=abs(call_pnl).max())
ax.set_xticks(range(len(spot_range)))
ax.set_xticklabels([f"{s:.0f}" for s in spot_range])
ax.set_yticks(range(len(vol_range)))
ax.set_yticklabels([f"{v:.2f}" for v in vol_range])
ax.set_xlabel("Spot Price")
ax.set_ylabel("Volatility")
ax.set_title("Call P&L Heatmap")
fig.colorbar(im, ax=ax, label="Call P&L")

fig2, ax2 = plt.subplots()
im2 = ax2.imshow(put_pnl, cmap="RdYlGn", aspect="auto", vmin=-abs(put_pnl).max(), vmax=abs(put_pnl).max())
ax2.set_xticks(range(len(spot_range)))
ax2.set_xticklabels([f"{s:.0f}" for s in spot_range])
ax2.set_yticks(range(len(vol_range)))
ax2.set_yticklabels([f"{v:.2f}" for v in vol_range])
ax2.set_xlabel("Spot Price")
ax2.set_ylabel("Volatility")
ax2.set_title("Put P&L Heatmap")
fig2.colorbar(im2, ax=ax2, label="Put P&L")

col1, col2 = st.columns(2)

with col1:
	st.pyplot(fig)
	st.caption(f"Unrealized P&L today (T={T} years remaining), not payoff at expiration.")

with col2:
	st.pyplot(fig2)
	st.caption(f"Unrealized P&L today (T={T} years remaining), not payoff at expiration.")
