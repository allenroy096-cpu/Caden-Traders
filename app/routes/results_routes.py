from flask import jsonify, render_template, Blueprint
import sqlite3

results = Blueprint('results', __name__)
DB_PATH = 'trading_bot.db'

def fetch_watchlist():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT symbol, added_on, reason FROM watchlist')
    rows = c.fetchall()
    conn.close()
    return [dict(symbol=s, added_on=a, reason=r) for s, a, r in rows]

def fetch_shortlist():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT symbol, consolidation_start, consolidation_end FROM shortlisted')
    rows = c.fetchall()
    conn.close()
    return [dict(symbol=s, consolidation_start=cs, consolidation_end=ce) for s, cs, ce in rows]

@results.route('/api/watchlist')
def api_watchlist():
    return jsonify(fetch_watchlist())

@results.route('/api/shortlist')
def api_shortlist():
    return jsonify(fetch_shortlist())

@results.route('/results')
def results_page():
    return render_template('results.html')
