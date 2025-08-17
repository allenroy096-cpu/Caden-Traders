
# Minimal Flask app and Upstox API helpers for web UI and data fetching
import os
import requests
import pandas as pd
from flask import Flask, render_template, request, jsonify

# Upstox API credentials (replace with your own if needed)
UPSTOX_API_KEY = 'ab15e840-cd19-4cc1-ab38-1337cf6ae09c'
UPSTOX_API_SECRET = 'v2sfur9bmx'
UPSTOX_ACCESS_TOKEN = 'eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiJBQzY0MDYiLCJqdGkiOiI2ODljY2RlZGYxNDhhNjBjZTI5ZGEzMjQiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc1NTEwNjc5NywiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzU1MTIyNDAwfQ.aBoHVdO7i1AlkJODX_SSQXXJlp1C2diGW-RQPJz_V-U'

def fetch_upstox_historical_candles(instrument_token, interval, start_date, end_date):
	"""
	Fetch historical candles for an instrument from Upstox REST API.
	interval: '1minute', '3minute', '5minute', '15minute', '30minute', '60minute', 'day'
	start_date, end_date: 'YYYY-MM-DD'
	Returns: DataFrame with columns ['timestamp', 'open', 'high', 'low', 'close', 'volume']
	"""
	url = f"https://api.upstox.com/v2/historical-candle/{instrument_token}/{interval}"
	headers = {"Authorization": f"Bearer {UPSTOX_ACCESS_TOKEN}"}
	params = {"from": start_date, "to": end_date}
	r = requests.get(url, headers=headers, params=params)
	data = r.json()
	if data.get('status') == 'success':
		df = pd.DataFrame(data['data']['candles'], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
		return df
	else:
		raise Exception(f"Upstox API error: {data}")

def fetch_upstox_instruments(exchange='NSE_EQ'):
	"""
	Download and load the Upstox instruments CSV file for the given exchange.
	Returns: DataFrame with instrument details.
	"""
	url = f"https://assets.upstox.com/market-quote/instruments/exchange/{exchange}.csv"
	local_csv = f"{exchange}.csv"
	if not os.path.exists(local_csv):
		r = requests.get(url)
		with open(local_csv, 'wb') as f:
			f.write(r.content)
	df = pd.read_csv(local_csv)
	return df

app = Flask(__name__)

@app.route('/')
def home():
	return render_template('index.html')

@app.route('/fetch_historical', methods=['POST'])
def fetch_historical():
	params = request.json or {}
	instrument_token = params.get('instrument_token')
	interval = params.get('interval', 'day')
	start_date = params.get('start_date')
	end_date = params.get('end_date')
	try:
		df = fetch_upstox_historical_candles(instrument_token, interval, start_date, end_date)
		return jsonify({
			'columns': df.columns.tolist(),
			'rows': df.values.tolist()
		})
	except Exception as e:
		return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
	app.run(debug=True, port=5000)
